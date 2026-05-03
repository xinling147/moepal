import sys
from pathlib import Path

# Ensure companion_app is importable
_project_root = Path(__file__).parent.parent
sys.path.insert(0, str(_project_root))
