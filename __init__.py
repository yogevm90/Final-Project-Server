import pathlib
import os
import sys

curr_dir = pathlib.Path(os.path.dirname(__file__))
sys.path.append(str(curr_dir))
sys.path.append(str(curr_dir / "flask_microservices"))
sys.path.append(str(curr_dir / "interfaces"))
sys.path.append(str(curr_dir / "server"))
sys.path.append(str(curr_dir / "tests"))
sys.path.append(str(curr_dir / "utilities"))
