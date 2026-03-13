import subprocess
from pathlib import Path

def bump_version():
    version_file = Path("addon/VERSION")
    if not version_file.exists():
        print("Error: addon/VERSION not found")
        return

    # Read current version (e.g., "2.7")
    current_version = version_file.read_text().strip()
    try:
        major, minor = map(int, current_version.split('.'))
    except ValueError:
        print(f"Error: Invalid version format in VERSION file: {current_version}")
        return

    # Increment minor version
    new_version = f"{major}.{minor + 1}"
    
    print(f"Bumping version: {current_version} → {new_version}")
    
    # Use the existing new_version.py to sync everything
    try:
        subprocess.run(["python", "new_version.py", new_version, "addon"], check=True)
        print(f"✅ Successfully updated manifest.json and VERSION to {new_version}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update version: {e}")

if __name__ == "__main__":
    bump_version()
