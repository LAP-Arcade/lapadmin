import subprocess
import sys
from pathlib import Path

try:
    import app as _
except ModuleNotFoundError as e:
    import os

    print(f"{e}, creating venv and swapping process...")

    subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
    if sys.platform == "win32":
        subprocess.check_call(
            [".venv/Scripts/pip", "install", "-r", "requirements.txt"]
        )
        os.execl(".venv/Scripts/python", ".venv/Scripts/python", *sys.argv)
    else:
        subprocess.check_call(
            [".venv/bin/pip", "install", "-r", "requirements.txt"]
        )
        os.execl(".venv/bin/python", ".venv/bin/python", *sys.argv)

from argparse import ArgumentParser

from app import create_app
from app.db import Visitor

parser = ArgumentParser()
parser.add_argument("--port", type=int, default=5000)
parser.add_argument("--host", default="0.0.0.0")

args = parser.parse_args()
app = create_app(debug=True)

with app.session() as s:
    if not s.query(Visitor).count():
        print("Visitor table is empty, importing visitors from gsheet...")
        subprocess.run(
            [Path(sys.executable).parent / "flask", "import", "visitors"]
        )
app.run(host=args.host, port=args.port)
