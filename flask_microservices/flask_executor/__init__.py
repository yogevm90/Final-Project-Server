import pathlib
import os
import sys

curr_dir = pathlib.Path(os.path.dirname(__file__)).parent.parent / "utilities"
sys.path.append(str(curr_dir))
