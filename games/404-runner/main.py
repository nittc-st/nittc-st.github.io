import pyxel
from pathlib import Path

HEIGHT = 128
WIDTH  = 128
FPS = 30
SOUND_BUTTON = (86, 14, 40, 9)
PLAYER_X_INIT = 40
PLAYER_Y_INIT = HEIGHT - 24
DELTA_X_INIT  = 1
DELTA_Y_INIT  = 0
SPEED_INIT   = 2
TILE_FLOOR = (1, 0)
WALL_TILE_X = 4
PIXEL_SIZE = 8
END_OF_COURCE = 120

BGM = 0

SE_CH = 3
LAND_SE = 24
JUMP_SE = 25
FALL_SE = 26

TITLE  = 0
COUNT  = 1
MAIN   = 2
GM_OV  = 3
RESULT = 4

GROUND_TILES = [(2, 0), (2, 1), (3, 0)]

CHECK_POINT = [(2, 0), (6, 0), (2, 7), (6, 7)]

class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, fps=FPS)
        pyxel.mouse(True)
        pyxel.load(str(Path(__file__).with_name("my_resource.pyxres")))
        self.sound_gains = [channel.gain for channel in pyxel.channels]
        self.is_muted = True
        for channel in pyxel.channels:
            channel.gain = 0
        self._init_values()

        pyxel.run(self.update, self.draw)

    def _init_values(self):
        """Initialise values.
        """
        self.player_x = PLAYER_X_INIT
        self.player_y = PLAYER_Y_INIT

        self.player_dx = DELTA_X_INIT
        self.player_dy = DELTA_Y_INIT

        self.fg_scroll_x = 0
        self.bg_scroll_x = 0
        self.speed = SPEED_INIT
        self.scroll_count = 0

        self.has_right_inertia = False
        self.has_left_inertia = False

        self.is_land = True
        self.can_foward = True
        self.can_scroll = True
        self.can_jump = True
        self.is_falling = False
        self.passing = False
        self.hide = False
        self.respawn_wait_until = None
        self.blink_started_at = None

        self.scene = TITLE

        self.distance = 0
        self.coin = 0
        self.life = 3

        self.start_count = 3
        self.count_started_at = None

        self.__debug_mode = False

        pyxel.stop(0)

    def get_score(self) -> int:
        return int(self.distance + self.coin)

    def update(self):
        """Calculate the positions of what the app will have to draw.
        """
        # 初期状態は消音。ゲーム内ボタン・M・SELECTで切り替える。
        x, y, width, height = SOUND_BUTTON
        sound_clicked = (
            pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            and x <= pyxel.mouse_x < x + width
            and y <= pyxel.mouse_y < y + height
        )
        if (
            pyxel.btnp(pyxel.KEY_M)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_BACK)
            or sound_clicked
        ):
            self.is_muted = not self.is_muted
            for channel, gain in zip(pyxel.channels, self.sound_gains):
                channel.gain = 0 if self.is_muted else gain

        if self.is_pressed_reset():
            self._init_values()
        if self.is_pressed_debug():
            self.__debug_mode = True

        if self.__debug_mode:
            self.debug_function()

        if self.scene == TITLE:
            self.update_title()
        elif self.scene == COUNT:
            self.update_count()
        elif self.scene == MAIN:
            self.update_main()
        elif self.scene == GM_OV:
            self.update_gameover()
        elif self.scene == RESULT:
            self.update_result()

        # 復活中は約0.1秒ごとに点滅し、通常時は必ず表示する。
        self.hide = (
            self.passing
            and self.blink_started_at is not None
            and ((pyxel.frame_count - self.blink_started_at) // (FPS // 10)) % 2 == 1
        )

    def update_title(self):
        """Scan Key Space and then transfer to COUNT.
        """
        if (
            pyxel.btn(pyxel.KEY_SPACE)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_START)
        ):
            self.scene = COUNT
            self.count_started_at = pyxel.frame_count

    def update_count(self):
        """Display: 3, 2, 1, start and transfer to MAIN.
        """
        elapsed = pyxel.frame_count - self.count_started_at
        self.start_count = max(3 - elapsed // FPS, 0)
        if elapsed >= 4 * FPS:
            self.scene = MAIN
            pyxel.playm(BGM, loop=True)

    def update_main(self):
        """Game Engine
        """
        self.update_player()
        if self.respawn_wait_until is not None or self.scene != MAIN:
            return
        self.scroll_foreground()
        self.scroll_background()

    def update_gameover(self):
        """Scan key space and then transfer to RESULT.
        """
        if (
            pyxel.btnr(pyxel.KEY_SPACE)
            or pyxel.btnr(pyxel.GAMEPAD1_BUTTON_A)
            or pyxel.btnr(pyxel.GAMEPAD1_BUTTON_START)
        ):
            self.scene = RESULT

    def update_result(self):
        """Update result.
        """
        if (
            pyxel.btnr(pyxel.KEY_SPACE)
            or pyxel.btnr(pyxel.GAMEPAD1_BUTTON_A)
            or pyxel.btnr(pyxel.GAMEPAD1_BUTTON_START)
        ):
            self._init_values()
        pass

    def scroll_foreground(self):
        """Scroll the picture.
        """
        if not self.can_scroll:
            self.speed = SPEED_INIT
            return
        self.fg_scroll_x += self.speed
        self.distance += self.speed / 10

        # Reset scroll
        if (self.fg_scroll_x / PIXEL_SIZE) >= END_OF_COURCE:
            self.fg_scroll_x = 0

    def scroll_background(self):
        """Scroll the picture.
        """
        self.bg_scroll_x = self.fg_scroll_x / 2

    def update_player(self):
        """Update of the (x, y) position of the player.
        """

        # 待機中は落下判定も止め、残機を繰り返し減らさない。
        if self.respawn_wait_until is not None:
            if pyxel.frame_count < self.respawn_wait_until:
                return
            self.respawn_wait_until = None
            self.passing = True
            self.blink_started_at = pyxel.frame_count

        if self.has_fallen():
            self.at_player_fallen()
            return

        if self.is_falling:
            self.at_player_falling()
            return

        if self.is_pressed_debug():
            self.can_scroll = False
            self.can_jump = False
            self.__debug_mode = True

        if self.__debug_mode:
            self.debug_function()

        self.move_by_key()
        self.move_if_into_block()

    def move_by_key(self):
        """Move the player when was pushed the keys.
        """
        if (
            pyxel.btn(pyxel.KEY_LEFT)
            or pyxel.btn(pyxel.KEY_A)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
        ) and self.can_foward:
            self.player_x = max(self.player_x - (self.player_dx + self.speed * 0.02), 0)
        if (
            pyxel.btn(pyxel.KEY_RIGHT)
            or pyxel.btn(pyxel.KEY_D)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        ) and self.can_foward:
            self.player_x = min(self.player_x + (self.player_dx + self.speed * 0.02), pyxel.width - 8)
        if self.is_land and self.can_jump:
            if (
                pyxel.btn(pyxel.KEY_UP)
                or pyxel.btn(pyxel.KEY_SPACE)
                or pyxel.btn(pyxel.KEY_W)
                or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A)
            ):
                pyxel.play(SE_CH, JUMP_SE, loop=False)
                self.is_land = False
                self.player_dy = 4
        if not self.is_land and self.can_jump:
            # jumping tracks is not linear (fast, slow, stop, slow, fast)
            self.player_y = max(self.player_y - self.player_dy, 0)
            self.player_dy -= 0.4 + self.speed * 0.02

    def move_if_into_block(self):
        """Exit the player from the enlocatable block if the player is locating in this block.
        """
        if self.is_block_under():
            self.player_y = (self.get_player_coor()[1] % 16) * 8
            if not self.is_land:
                pyxel.play(SE_CH, LAND_SE, loop=False)
                self.speed += 0.005
            self.is_land = True
        else:
            self.is_land = False

        if self.is_block_right():
            self.player_x = self.player_x - (2 + self.speed * 1.02)
            self.can_foward = False
        else:
            self.can_foward = True

    def is_block_under(self) -> bool:
        """Returns True if the block under the player is ground or block.

        Returns:
            bool: True: block / False: not block
        """
        if True in {self.get_under_tile() == i for i in GROUND_TILES}:
            return True
        return False

    def is_block_right(self):
        """Returns True if the block right side of the player is ground or block.

        Returns:
            bool: True: block / False: not block
        """
        if True in {self.get_right_tile() == i for i in GROUND_TILES}:
            return True
        return False

    def at_player_fallen(self):
        """Play the events at the time of that the player has fallen.
        """
        pyxel.play(SE_CH, FALL_SE, loop=False)
        if self.life == 0:
            self.scene = GM_OV
            pyxel.stop(0)
            return
        self.can_scroll = False
        self.player_x = PLAYER_X_INIT
        self.player_y = 8
        self.is_falling = True
        self.passing = False
        self.respawn_wait_until = pyxel.frame_count + FPS

    def at_player_falling(self):
        """Play the events at the time of that the player is falling. (after respawned)
        """
        if self.is_block_under():
            self.passing = False
            self.blink_started_at = None
            self.hide = False
            self.can_scroll = True
            self.can_foward = True
            self.is_falling = False
            self.move_if_into_block()
            return
        self.player_y += 1.5
        if (
            pyxel.btn(pyxel.KEY_RIGHT)
            or pyxel.btn(pyxel.KEY_D)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        ) and not self.is_block_right():
            self.player_x = min(self.player_x + 2, pyxel.width - 8)
        elif (
            pyxel.btn(pyxel.KEY_LEFT)
            or pyxel.btn(pyxel.KEY_A)
            or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
        ):
            self.player_x = max(self.player_x - 2, 0)

    def has_fallen(self) -> bool:
        """Returns True if player was fallen.

        Returns:
            bool: True: fallen / False: not fallen
        """

        if self.player_y >= HEIGHT:
            self.life -= 1
            return True
        if self.player_x < -PIXEL_SIZE:
            self.life -= 1
            return True
        return False

    def is_pressed_reset(self) -> bool:
        """Returns True if The keys of reset command were pressed.

        Returns:
            bool: True: pressed / False: not pressed
        """
        if pyxel.btn(pyxel.KEY_CTRL) and pyxel.btn(pyxel.KEY_SHIFT) and pyxel.btn(pyxel.KEY_R):
            return True
        if pyxel.btn(pyxel.KEY_RETURN):
            return True
        return False

    def is_pressed_debug(self) -> bool:
        """Returns True if The keys of debug command were pressed.

        Returns:
            bool: True: pressed / False: not pressed
        """

        if pyxel.btn(pyxel.KEY_CTRL) and pyxel.btn(pyxel.KEY_SHIFT) and pyxel.btn(pyxel.KEY_D):
            return True
        return False

    def debug_function(self):
        """The functinos of debug.
        """
        print(self.get_player_coor(), self.get_beside_tile())
        if pyxel.btn(pyxel.KEY_O):
            self.can_scroll = not self.can_scroll
        if pyxel.btn(pyxel.KEY_P):
            self.can_jump = not self.can_jump

        if pyxel.btn(pyxel.KEY_H):
            self.fg_scroll_x -= 2
        if pyxel.btn(pyxel.KEY_J):
            self.player_y -= 2
        if pyxel.btn(pyxel.KEY_K):
            self.player_y += 2
        if pyxel.btn(pyxel.KEY_L):
            self.fg_scroll_x += 2

        if pyxel.btn(pyxel.KEY_Z):
            self.distance -= 1
        if pyxel.btn(pyxel.KEY_X):
            self.distance += 1

    def draw(self):
        """Draw the picture on the window.
        """
        if   self.scene == TITLE:
            self.draw_title()
        elif self.scene == COUNT:
            self.draw_count()
        elif self.scene == MAIN:
            self.draw_main()
        elif self.scene == GM_OV:
            self.draw_gameover()
        elif self.scene == RESULT:
            self.draw_result()

        x, y, width, height = SOUND_BUTTON
        pyxel.rect(x, y, width, height, pyxel.COLOR_NAVY)
        pyxel.text(x + 2, y + 2, "SOUND OFF" if self.is_muted else "SOUND ON", pyxel.COLOR_WHITE)

    def draw_title(self):
        """Draw the title page.
        """
        pyxel.cls(0)
        pyxel.text(pyxel.width // 2 - 24, pyxel.height // 2, "Space / JUMP", pyxel.COLOR_WHITE)

    def draw_count(self):
        """Draw the count down.
        """
        self.draw_main()
        fmt = str(self.start_count) if self.start_count else "START"
        x = pyxel.width // 2 - (0 if self.start_count else 10)
        pyxel.text(x, pyxel.height // 2 - 10, fmt, pyxel.COLOR_NAVY)

    def draw_main(self):
        """Draw a new picture to follow the positions of the things.
        """
        pyxel.cls(0)
        # Layer 3: Sky
        pyxel.bltm(0, 0, 0, 0, 256, pyxel.width + 1, pyxel.height + 1)
        # Layer 2: Background
        pyxel.bltm(0, 0, 0, self.bg_scroll_x, 128, pyxel.width, pyxel.height, 0)
        # Layer 1: Stage
        pyxel.bltm(0, 0, 0, self.fg_scroll_x, 0, pyxel.width, pyxel.height, 0)
        # Layer 1: Character
        if not self.hide:
            pyxel.blt( self.player_x, self.player_y, 0, 0, 8, 8, 8, 0)
        # layer 1: Score
        pyxel.text(5, 5, "Score: {}".format(int(self.distance + self.coin)), pyxel.COLOR_NAVY)
        pyxel.text(pyxel.width - 32, 5, "Life: {}".format(self.life), pyxel.COLOR_NAVY)

    def draw_gameover(self):
        """Draw the gameover page.
        """
        self.draw_main()
        pyxel.text(pyxel.width // 2 - 19, pyxel.height // 2 - 20, "GAME OVER!", pyxel.COLOR_NAVY)
        pyxel.text(pyxel.width // 2 - 24, pyxel.height // 2 + 30, "Space / JUMP", pyxel.COLOR_NAVY)

    def draw_result(self):
        """Draw the result page.
        """
        pyxel.cls(0)
        pyxel.text(pyxel.width // 2 - 18, pyxel.height // 2 - 40, "GAME OVER", pyxel.COLOR_WHITE)
        pyxel.text(pyxel.width // 2 - 16, pyxel.height // 2 - 20, "score: {}".format(self.get_score()), pyxel.COLOR_WHITE)
        pyxel.text(pyxel.width // 2 - 36, pyxel.height // 2 + 40, "Space / JUMP: Retry", pyxel.COLOR_WHITE)

    def get_beside_tile(self) -> tuple[tuple[int]]:
        """Get a position of a tile of around the player.

        Returns:
            tuple[tuple[int]]: tile data like (top, under, left, right)
        """
        return (
            self.get_top_tile(),
            self.get_under_tile(),
            self.get_left_tile(),
            self.get_right_tile()
        )

    def get_under_tile(self) -> tuple[int]:
        """Get a tile under the player.

        Returns:
            tuple[int]: (x, y) coordinate
        """
        cx, cy = self.get_player_coor(4)
        return pyxel.tilemaps[0].pget(cx, cy + 1)

    def get_top_tile(self) -> tuple[int]:
        """Get a tile top the player.

        Returns:
            tuple[int]: (x, y) coordinate
        """
        cx, cy = self.get_player_coor()
        return pyxel.tilemaps[0].pget(cx, cy - 1)

    def get_left_tile(self) -> tuple[int]:
        """Get a tile left the player.

        Returns:
            tuple[int]: (x, y) coordinate
        """
        cx, cy = self.get_player_coor()
        return pyxel.tilemap(0).pget(cx - 1, cy)

    def get_right_tile(self) -> tuple[int]:
        """Get a tile right the player.

        Returns:
            tuple[int]: (x, y) coordinate
        """
        cx, cy = self.get_player_coor()
        return pyxel.tilemap(0).pget(cx + 1, cy)

    def get_player_coor(self, gap_x: float = 0, gap_y: float = 0) -> tuple[int]:
        """Get a position of the player.

        Returns:
            tuple[int]: (x, y) coordinate
        """
        cx = (self.fg_scroll_x + self.player_x + gap_x) // PIXEL_SIZE
        cy = (self.player_y + gap_y) // PIXEL_SIZE
        return (cx, cy)

# Execute
App()
