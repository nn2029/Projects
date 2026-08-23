from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.simulation import compile_bundle, validate_spec


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile a simulation spec into a runnable bundle.")
    parser.add_argument("session_dir", type=Path, help="Path to an existing session directory.")
    parser.add_argument("spec", type=Path, help="Path to simulation-spec.json")
    args = parser.parse_args()

    session_dir = args.session_dir.resolve()
    static_dir = Path(__file__).resolve().parents[1] / "app" / "static"
    spec = validate_spec(json.loads(args.spec.read_text(encoding="utf-8")))
    result = compile_bundle(session_dir, spec, static_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
