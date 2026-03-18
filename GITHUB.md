# Review Hotmouse Plus Overview - Developer Documentation

This repository contains the source code for the **Review Hotmouse Plus Overview** Anki add-on.

## Quick Links

- **Main Repository**: [https://github.com/athulkrishna2015/Review-Hotmouse-Plus-Overview/](https://github.com/athulkrishna2015/Review-Hotmouse-Plus-Overview/)
- **Install via AnkiWeb**: [Add-on ID 1054369752](https://ankiweb.net/shared/info/1054369752)
- **Report an Issue**: [Issues Page](https://github.com/athulkrishna2015/Review-Hotmouse-Plus-Overview/issues)
- **Latest Releases**: [Releases Page](https://github.com/athulkrishna2015/Review-Hotmouse-Plus-Overview/releases)

---

## Project Structure

- `addon/`: The core add-on code that gets bundled into the `.ankiaddon` file.
  - `ankiaddonconfig/`: A library for managing the GUI configuration window.
  - `compat/`: Handles compatibility migrations for users upgrading from older versions.
  - `web/`: JavaScript files (e.g., `detect_wheel.js`) injected into Anki webviews.
  - `Support/`: QR codes and assets for the Support tab.
  - `event.py`: The heart of the add-on; handles mouse events, shortcuts, and menu integration.
  - `config.py`: Defines the configuration tabs (General, Hotkeys, Support).
  - `VERSION`: Plain text file containing the current version (e.g., `2.8`).
- `tests/`: Unit tests for configuration and compatibility logic.
- `make_ankiaddon.py`: Build script that auto-bumps the version and creates the `.ankiaddon` package.
- `new_version.py`: Utility script to sync version numbers across `manifest.json` and `VERSION`.
- `bump.py`: Standalone script to increment the minor version number.

---

## Development Workflow

### 1. Local Testing (Symlinking)
The fastest way to test changes is to symlink the `addon/` folder into your Anki add-ons directory:

**Linux:**
```shell
ln -s "$(pwd)/addon" ~/.local/share/Anki2/addons21/review_hotmouse_dev
```

**Windows (Admin PowerShell):**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:APPDATA\Anki2\addons21\review_hotmouse_dev" -Target "$pwd\addon"
```

### 2. Building and Releasing

This repository uses **GitHub Actions** to automate builds:

- **Automated Builds**: Every push to `master` automatically builds the `.ankiaddon` file. You can download the latest version from the "Actions" tab under the "Build Addon" workflow artifacts.
- **Official Releases**: To create a formal release, use the GitHub "Actions" tab -> "Create Release" workflow. Enter the version number (e.g., `2.9`), and it will automatically:
  1. Bump the version in all files.
  2. Commit the change.
  3. Create a GitHub Release with the bundled addon.

Alternatively, to build locally:
```shell
python make_ankiaddon.py
```
*Note: Local builds will also increment the minor version number.*


To create a new release on GitHub with both Chrome and Firefox builds:


1.  **Commit and Tag**:
    ```bash
    git add .
    git commit -m "Bump version to v1.x.x"
    git tag v1.x.x
    git push origin master --tags
    ```
2.  **Build and Upload to Releases**:
    Use the GitHub CLI (`gh`) to create a release and attach the ZIP files:
    ```bash
    gh release create v1.x.x addonname.ankiaddon \
        --title "Release v1.x.x" \
        --notes "List your changes here."
    ```


---

## How to Contribute

1. **Fork the Repository**.
2. **Create a Feature Branch**.
3. **Implement Changes** (don't forget to add tests if applicable).
4. **Verify** using symlinking and the code standards tools.
5. **Submit a Pull Request** with a clear description of your improvements.

---

*This project is a fork of the original [Review Hotmouse](https://github.com/BlueGreenMagick/Review-Hotmouse/) by BlueGreenMagick.*
