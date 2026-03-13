import os
import zipfile
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
ADDON_NAME = "Review_Hotmouse_Plus_Overview"
ADDON_DIR = "addon"

def bump_version():
    version_file = Path(f"{ADDON_DIR}/VERSION")
    if not version_file.exists():
        return

    current_version = version_file.read_text().strip()
    try:
        major, minor = map(int, current_version.split('.'))
        new_version = f"{major}.{minor + 1}"
        print(f"Bumping version: {current_version} → {new_version}")
        subprocess.run(["python", "new_version.py", new_version, ADDON_DIR], check=True)
    except Exception as e:
        print(f"Warning: Could not auto-bump version: {e}")

def create_ankiaddon():
    # Auto-bump version before building
    bump_version()
    
    # Get the project root and addon directory
    root_dir = Path.cwd()
    addon_path = root_dir / ADDON_DIR
    
    if not addon_path.exists():
        print(f"Error: {ADDON_DIR} directory not found.")
        return

    today = datetime.today().strftime('%Y%m%d%H%M')
    zip_name = f'{ADDON_NAME}_{today}.zip'
    final_name = f'{ADDON_NAME}_{today}.ankiaddon'

    # Exclusions
    exclude_dirs = ['__pycache__', '.git', '.vscode', '.github', 'tests']
    exclude_exts = ['.ankiaddon', '.pyc']
    exclude_files = ['meta.json', '.gitignore', '.gitmodules', 'mypy.ini']

    print(f"Creating {final_name} from {ADDON_DIR}...")

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the addon directory specifically
        for root, dirs, files in os.walk(addon_path):
            # Filter directories in-place
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                # Skip excluded files/extensions
                if file in exclude_files or file_path.suffix in exclude_exts:
                    continue
                
                # Calculate the path relative to the 'addon/' folder 
                # so that __init__.py is at the root of the zip
                archive_name = file_path.relative_to(addon_path)
                zipf.write(file_path, archive_name)

    # Rename to .ankiaddon
    if os.path.exists(final_name):
        os.remove(final_name)
    os.rename(zip_name, final_name)
    print(f"Successfully created: {final_name}")

if __name__ == "__main__":
    create_ankiaddon()
