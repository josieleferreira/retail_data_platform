from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from retail_data_platform.orchestration.pipeline import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plataforma analítica para varejo multicanal")
    parser.add_argument("--source", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    run(args.source.resolve(), args.root.resolve())
