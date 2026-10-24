"""ゲーム本体とリソースだけをパッケージ化し、埋め込み用HTMLを生成する。"""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    source = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="404-runner-") as temporary:
        output = Path(temporary)
        stage = output / "404-runner"
        stage.mkdir()
        for filename in ("main.py", "my_resource.pyxres"):
            shutil.copyfile(source / filename, stage / filename)

        subprocess.run(
            [sys.executable, "-m", "pyxel", "package", str(stage), str(stage / "main.py")],
            cwd=output,
            check=True,
        )
        subprocess.run(
            [sys.executable, "-m", "pyxel", "app2html", "404-runner.pyxapp"],
            cwd=output,
            check=True,
        )
        # 標準の多ボタンパッドを外し、左右・ジャンプだけの操作UIを付ける。
        html = (output / "404-runner.html").read_text(encoding="utf-8")
        html = html.replace('gamepad: "enabled", ', '')
        controls = (source / "web_controls.html").read_text(encoding="utf-8")
        (source / "game.html").write_text(html + controls, encoding="utf-8")
    print(f"Generated: {source / 'game.html'}")


if __name__ == "__main__":
    main()
