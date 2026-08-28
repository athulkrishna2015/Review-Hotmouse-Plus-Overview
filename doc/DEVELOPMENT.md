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
  - `ankiaddonconfig/`: A library for managing the GUI configuration window (non-modal to allow using Anki while open).
  - `compat/`: Handles compatibility migrations for users upgrading from older versions.
  - `config_tabs/`: Sub-modules representing individual tabs in the configuration GUI:
    - `general.py`: Main settings like smart scrolling.
    - `hotkeys.py`: Keyboard and mouse mapping configurations.
    - `trackpad.py`: Gesture configurations.
    - `tab_support.py`: QR code payment/donation support options.
    - `logs.py`: Real-time viewing of action logs.
  - `web/`: JavaScript files (e.g., `detect_wheel.js`) injected into Anki webviews.
  - `Support/`: QR codes and assets for the Support tab.
  - `event.py`: The heart of the add-on; handles mouse events, shortcuts, and menu integration.
  - `config.py`: Registers and initializes the config tabs.
  - `hotmouse.log`: Log file where all hotmouse actions are written in real-time.
  - `VERSION`: Plain text file containing the current version (e.g., `3.3.0`).
- `tests/`: Unit tests for configuration and compatibility logic.
- `make_ankiaddon.py`: Build script that bundles files (respecting `.gitignore`) and creates the `.ankiaddon` package.
- `bump.py`: Utility script to bump version (major, minor, patch) or set an explicit version (e.g. `python bump.py --set 3.3.0`).

---

## Development Workflow

### 1. Local Testing (Symlinking)
The fastest way to test changes is to symlink the `addon/` folder into your Anki add-ons directory:

**Linux:**
```shell
ln -s "$(pwd)/addon" ~/.local/share/Anki2/addons21/review_hotmouse_plus_overview_dev
```

**Windows (Admin PowerShell):**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:APPDATA\Anki2\addons21\review_hotmouse_plus_overview_dev" -Target "$pwd\addon"
```

### 2. Debugging and Logging
- **Real-Time Logs**: When actions are executed via Hotmouse, they are appended in real-time to `addon/hotmouse.log`. You can tail this file during development or view it in the **Logs** tab of the configuration window.
- **Non-blocking GUI Settings**: The configuration window behaves non-modally, allowing you to trigger mouse wheel and right-click events in the reviewer and see updates in the Logs tab live without needing to close the configuration panel first.

### 3. Building and Releasing

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
