from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_SPLITS = ("train/good", "test/good")


def validate_category(root: Path, category: str) -> list[str]:
    errors: list[str] = []
    category_dir = root / category
    if not category_dir.exists():
        return [f"missing category: {category}"]

    for relative in REQUIRED_SPLITS:
        path = category_dir / relative
        if not path.exists():
            errors.append(f"{category}: missing {relative}")

    test_dir = category_dir / "test"
    defect_dirs = [p for p in test_dir.iterdir() if p.is_dir() and p.name != "good"] if test_dir.exists() else []
    if not defect_dirs:
        errors.append(f"{category}: no defect test folders found")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the expected MVTec AD folder layout.")
    parser.add_argument("root", type=Path, help="Path to the MVTec AD root directory")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["bottle", "cable", "metal_nut", "transistor", "zipper"],
    )
    args = parser.parse_args()

    errors: list[str] = []
    for category in args.categories:
        errors.extend(validate_category(args.root, category))

    if errors:
        print("Dataset validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Dataset layout is valid for selected categories.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
