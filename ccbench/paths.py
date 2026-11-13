import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE_ROOT = os.path.join(ROOT, "fixture_repo")
FIXTURE_PKG = "frostline"
DATA_DIR = os.path.join(ROOT, "data")
RESULTS_DIR = os.path.join(ROOT, "results")
CONFIG_DIR = os.path.join(ROOT, "configs")
