import os
import pathlib
import sys

templates = pathlib.Path(os.path.dirname(__file__)) / "templates"
sys.path.append(str(templates))
