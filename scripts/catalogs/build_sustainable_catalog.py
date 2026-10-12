"""Build Sustainable using the latest user-supplied plant-based source."""
import runpy,sys
from pathlib import Path
if "--author" not in sys.argv: sys.argv.append("--author")
runpy.run_path(str(Path(__file__).with_name("build_sustainable_plantbased.py")),run_name="__main__")
