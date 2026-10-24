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
        shutil.copyfile(output / "404-runner.html", source / "game.html")
    print(f"Generated: {source / 'game.html'}")


if __name__ == "__main__":
    main()
