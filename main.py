#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
from dictra_analyzr.pipeline import DictraPipeline

def main():
    parser = argparse.ArgumentParser(description="Dictra Data Analysis Pipeline")
    parser.add_argument("path", nargs='?', default=".", help="Base directory containing data and settings.json")
    parser.add_argument("--config", default="settings.json", help="Configuration file name (default: settings.json)")
    
    args = parser.parse_args()
    
    base_path = Path(args.path).resolve()
    config_path = base_path / args.config
    
    if not base_path.exists():
        print(f"Error: Path {base_path} does not exist.")
        sys.exit(1)

    if not config_path.exists():
        print(f"Error: Configuration file {config_path} not found.")
        print("Please ensure settings.json exists in the target directory.")
        sys.exit(1)

    try:
        pipeline = DictraPipeline(str(config_path), str(base_path))
        pipeline.run()
    except Exception as e:
        print(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
