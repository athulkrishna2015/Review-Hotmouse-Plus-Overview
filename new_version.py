import re
import sys
import json
from pathlib import Path

VERSION_RE = re.compile(r"^(\d+)\.(\d+)(?:\.(\d+))?$")


def normalize_version(version_string: str) -> str:
    match = VERSION_RE.fullmatch(version_string.strip())
    if not match:
        raise ValueError(
            f"Invalid version format '{version_string}'. Use major.minor.patch (e.g. 2.10.1)."
        )

    major, minor, patch = match.groups()
    patch = patch or "0"
    return f"{int(major)}.{int(minor)}.{int(patch)}"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python new_version.py <major.minor.patch> <addon_dir>")

    try:
        version_string = normalize_version(sys.argv[1])
    except ValueError as exc:
        raise SystemExit(str(exc))

    addon_root = Path(sys.argv[2])
    if not addon_root.is_dir():
        raise SystemExit(f"Error: Add-on directory not found: {addon_root}")

    manifest_path = addon_root / "manifest.json"
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    manifest["human_version"] = version_string
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    # human_version is only updated on install.
    # For developing purposes, use VERSION file to check current version
    version_path = addon_root / "VERSION"
    version_path.write_text(f"{version_string}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
