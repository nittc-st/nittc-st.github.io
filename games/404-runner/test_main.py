"""フレーム境界とシーン遷移の回帰テスト（Pyxelの画面・音声はモック）。"""

from pathlib import Path
import runpy
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch


class GameTests(unittest.TestCase):
    def setUp(self):
        self.pyxel = MagicMock(width=128, height=128, frame_count=0)
        self.pyxel.channels = [SimpleNamespace(gain=0.125) for _ in range(4)]
        self.pyxel.btnp.return_value = False
        self.pressed = set()
        self.released = set()
        self.pyxel.btn.side_effect = lambda key: key in self.pressed
        self.pyxel.btnr.side_effect = lambda key: key in self.released
        self.pyxel.tilemaps[0].pget.return_value = (0, 0)
        self.pyxel.tilemap.return_value.pget.return_value = (0, 0)
        with patch.dict("sys.modules", pyxel=self.pyxel):
            self.game = runpy.run_path(str(Path(__file__).with_name("main.py")))
        self.app = self.pyxel.run.call_args.args[0].__self__

    def tick(self, frame):
        self.pyxel.frame_count = frame
        self.app.update()

    def test_default_mute_and_toggle(self):
        self.assertTrue(self.app.is_muted)
        self.assertEqual([channel.gain for channel in self.pyxel.channels], [0] * 4)
        self.pyxel.btnp.side_effect = lambda key: key == self.pyxel.KEY_M
        self.tick(1)
        self.assertFalse(self.app.is_muted)
        self.assertEqual([channel.gain for channel in self.pyxel.channels], [0.125] * 4)
        self.app._init_values()
        self.assertFalse(self.app.is_muted)
        self.tick(2)
        self.assertTrue(self.app.is_muted)
        self.assertEqual([channel.gain for channel in self.pyxel.channels], [0] * 4)

    def test_countdown_and_bgm(self):
        self.pressed.add(self.pyxel.KEY_SPACE)
        self.tick(20)
        self.pressed.clear()
        self.assertEqual(self.app.scene, self.game["COUNT"])
        for elapsed, count in [(0, 3), (29, 3), (30, 2), (60, 1), (90, 0), (119, 0)]:
            self.tick(20 + elapsed)
            self.assertEqual(self.app.start_count, count)
            self.assertEqual(self.app.scene, self.game["COUNT"])
            self.pyxel.playm.assert_not_called()
        self.tick(140)
        self.assertEqual(self.app.scene, self.game["MAIN"])
        self.pyxel.playm.assert_called_once_with(self.game["BGM"], loop=True)

    def test_sound_button_and_select(self):
        x, y, width, height = self.game["SOUND_BUTTON"]
        self.pyxel.mouse_x = x + width // 2
        self.pyxel.mouse_y = y + height // 2
        self.pyxel.btnp.side_effect = lambda key: key == self.pyxel.MOUSE_BUTTON_LEFT
        self.tick(1)
        self.assertFalse(self.app.is_muted)
        self.assertEqual([channel.gain for channel in self.pyxel.channels], [0.125] * 4)
        self.pyxel.mouse_x = 10
        self.tick(2)
        self.assertFalse(self.app.is_muted)
        self.pyxel.btnp.side_effect = lambda key: key == self.pyxel.GAMEPAD1_BUTTON_BACK
        self.tick(3)
        self.assertTrue(self.app.is_muted)
        self.assertEqual([channel.gain for channel in self.pyxel.channels], [0] * 4)

    def test_gamepad_start_result_and_restart(self):
        self.pressed.add(self.pyxel.GAMEPAD1_BUTTON_A)
        self.tick(1)
        self.assertEqual(self.app.scene, self.game["COUNT"])
        self.pressed.clear()
        self.tick(121)
        self.assertEqual(self.app.scene, self.game["MAIN"])
        self.app.life = 1
        self.app.player_y = 128
        self.tick(122)
        self.assertEqual(self.app.scene, self.game["GM_OV"])
        self.released.add(self.pyxel.GAMEPAD1_BUTTON_A)
        self.tick(123)
        self.assertEqual(self.app.scene, self.game["RESULT"])
        self.released.clear()
        self.tick(124)
        self.assertEqual(self.app.scene, self.game["RESULT"])
        self.released.add(self.pyxel.GAMEPAD1_BUTTON_A)
        self.tick(125)
        self.assertEqual(self.app.scene, self.game["TITLE"])
        self.assertEqual(self.app.life, 3)

    def test_gamepad_movement_jump_and_respawn_movement(self):
        self.app.scene = self.game["MAIN"]
        self.pyxel.tilemaps[0].pget.return_value = (2, 0)
        self.pressed.add(self.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        self.tick(1)
        self.assertAlmostEqual(self.app.player_x, 41.04)
        self.pressed = {self.pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, self.pyxel.GAMEPAD1_BUTTON_A}
        self.pyxel.tilemaps[0].pget.return_value = (0, 0)
        self.tick(2)
        self.assertAlmostEqual(self.app.player_x, 40)
        self.assertEqual(self.app.player_y, 100)
        self.app.player_y = 128
        self.tick(3)
        self.pressed = {self.pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT}
        self.tick(33)
        self.assertEqual(self.app.player_x, 42)
        self.assertTrue(self.app.is_falling)

    def test_respawn_wait_blink_and_landing(self):
        self.app.scene = self.game["MAIN"]
        self.app.player_y = 128
        self.tick(10)
        self.assertEqual(self.app.life, 2)
        self.assertEqual(self.app.respawn_wait_until, 40)
        self.pyxel.play.assert_called_once_with(3, 26, loop=False)
        for frame in range(11, 40):
            self.tick(frame)
            self.assertEqual((self.app.life, self.app.player_y, self.app.fg_scroll_x), (2, 8, 0))
        self.tick(40)
        self.assertEqual(self.app.player_y, 9.5)
        self.assertTrue(self.app.passing)
        self.assertFalse(self.app.hide)
        self.tick(43)
        self.assertTrue(self.app.hide)
        self.tick(46)
        self.assertFalse(self.app.hide)
        self.pyxel.tilemaps[0].pget.return_value = (2, 0)
        self.tick(47)
        self.assertFalse(self.app.is_falling)
        self.assertFalse(self.app.passing)
        self.assertFalse(self.app.hide)
        self.assertTrue(self.app.can_scroll)
        self.assertTrue(self.app.is_land)

    def test_gameover_result_score_and_restart(self):
        self.app.scene = self.game["MAIN"]
        self.app.life = 1
        self.app.distance = 123.4
        self.app.coin = 5
        self.app.player_y = 128
        self.tick(10)
        self.assertEqual(self.app.life, 0)
        self.assertEqual(self.app.scene, self.game["GM_OV"])
        self.assertIsNone(self.app.respawn_wait_until)
        self.pyxel.stop.assert_called_with(0)
        self.released.add(self.pyxel.KEY_SPACE)
        self.tick(11)
        self.assertEqual(self.app.scene, self.game["RESULT"])
        self.app.draw()
        texts = [call.args[2] for call in self.pyxel.text.call_args_list]
        self.assertEqual(texts, ["GAME OVER", "score: 128", "Space / JUMP: Retry", "SOUND OFF"])
        self.tick(12)
        self.assertEqual(self.app.scene, self.game["TITLE"])
        self.assertEqual((self.app.life, self.app.get_score()), (3, 0))
        self.assertIsNone(self.app.count_started_at)
        self.assertIsNone(self.app.respawn_wait_until)
        self.assertIsNone(self.app.blink_started_at)
        self.assertFalse(self.app.hide)

    def test_reset_during_respawn(self):
        self.app.scene = self.game["MAIN"]
        self.app.player_x = -9
        self.tick(100)
        self.assertEqual(self.app.life, 2)
        self.pressed.add(self.pyxel.KEY_RETURN)
        self.tick(101)
        self.assertEqual(self.app.scene, self.game["TITLE"])
        self.assertIsNone(self.app.respawn_wait_until)
        self.assertFalse(self.app.passing)
        self.assertFalse(self.app.hide)
        self.assertEqual(self.app.life, 3)

    def test_movement_jump_scroll_and_collision(self):
        self.app.scene = self.game["MAIN"]
        self.pyxel.tilemaps[0].pget.return_value = (2, 0)
        self.pressed.add(self.pyxel.KEY_RIGHT)
        self.tick(1)
        self.assertAlmostEqual(self.app.player_x, 41.04)
        self.assertEqual((self.app.fg_scroll_x, self.app.bg_scroll_x), (2, 1))
        self.pressed = {self.pyxel.KEY_LEFT}
        self.tick(2)
        self.assertAlmostEqual(self.app.player_x, 40)
        self.pyxel.tilemaps[0].pget.return_value = (0, 0)
        self.pressed = {self.pyxel.KEY_SPACE}
        self.tick(3)
        self.assertEqual(self.app.player_y, 100)
        self.assertAlmostEqual(self.app.player_dy, 3.56)
        self.pyxel.play.assert_called_with(3, 25, loop=False)
        self.pyxel.tilemap.return_value.pget.return_value = (2, 0)
        self.pressed.clear()
        x = self.app.player_x
        self.tick(4)
        self.assertAlmostEqual(self.app.player_x, x - (2 + self.app.speed * 1.02))
        self.assertFalse(self.app.can_foward)


if __name__ == "__main__":
    unittest.main()
