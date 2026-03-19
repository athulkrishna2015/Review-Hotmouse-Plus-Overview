import subprocess
import sys
from pathlib import Path


def parse_version(version_string: str) -> tuple[int, int, int]:
    parts = version_string.strip().split(".")
    if len(parts) == 2:
        major, minor = map(int, parts)
        return major, minor, 0
    if len(parts) == 3:
        major, minor, patch = map(int, parts)
        return major, minor, patch
    raise ValueError(version_string)


def bump_version():
    version_file = Path("addon/VERSION")
    if not version_file.exists():
        print("Error: addon/VERSION not found")
        return

    # Read current version (e.g., "2.10.0")
    current_version = version_file.read_text().strip()
    try:
        major, minor, patch = parse_version(current_version)
    except ValueError:
        print(f"Error: Invalid version format in VERSION file: {current_version}")
        return

    # Increment patch version
    new_version = f"{major}.{minor}.{patch + 1}"
    
    print(f"Bumping version: {current_version} → {new_version}")
    
    # Use the existing new_version.py to sync everything
    try:
        subprocess.run([sys.executable, "new_version.py", new_version, "addon"], check=True)
        print(f"✅ Successfully updated manifest.json and VERSION to {new_version}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update version: {e}")

if __name__ == "__main__":
    bump_version()
