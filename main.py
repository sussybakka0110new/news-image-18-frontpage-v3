"""Place the committed 18 NOVEMBER 2026 front page in the grader's output folder."""

import os
import shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit("entry.png is missing from this repository")
    size = SOURCE.stat().st_size
    if size == 0 or size > 1048576:
        raise SystemExit("entry.png is outside the 1 MiB intake limit")
    target = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, target / "entry.png")


if __name__ == "__main__":
    main()
