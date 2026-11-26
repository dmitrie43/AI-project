"""
Debug helper for predict_one.

Usage (from ml-api/):
  uv run python scripts/debug_predict.py

Put a breakpoint on predict_one in app/ml/model_store.py (e.g. line with frame = ...)
or on the predict_one(...) call below, then run with the Cursor/VS Code debugger.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ml.model_store import load_model, predict_one  # noqa: E402


def main() -> None:
    load_model()

    features = {
        "category": "vpn",
        "priority": 5,
        "satisfaction": None,
        "tag_count": 2,
    }

    # Breakpoint here (F9) or inside predict_one
    result = predict_one(features)

    print("features:")
    print(json.dumps(features, ensure_ascii=False, indent=2))
    print("result:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
