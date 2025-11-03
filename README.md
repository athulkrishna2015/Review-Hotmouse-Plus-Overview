# [Review Hotmouse Plus Overview](https://github.com/athulkrishna2015/Review-Hotmouse-Plus-Overview/)

[Install via ankiweb](https://ankiweb.net/shared/info/1054369752)

Configurable mouse hotkeys for Anki’s review workflow, now extended to the Overview screen and Congratulations screen with a built‑in deck_browser action to jump to the Decks selector.  
This add-on pairs well with [Deck Centerer](https://ankiweb.net/shared/info/1520580564) and  [Audiovisual Feedback](https://ankiweb.net/shared/info/231569866).

## Configuration

Open Tools → Add‑ons → Review Hotmouse → Config and use the tabs:
- Overview Hotkeys: add/edit `o_*` mappings (for example, `o_click_right → deck_browser`, `o_wheel_down → study_now`).  
- Congratulations Hotkeys: add/edit `c_*` mappings (for example, `c_click_right → deck_browser`).  
- Question/Answer Hotkeys: unchanged; continue to use again/hard/good/easy/undo/etc.  

## Acknowledgments

This project is a fork and extension of the original “[Review Hotmouse](https://github.com/BlueGreenMagick/Review-Hotmouse/)” Anki add‑on; full credit for the concept and foundational code goes to the original author(s)

For more info read original [description](https://ankiweb.net/shared/info/1928346827).

## Screenshots

<img width="1010" height="675" alt="Screenshot_20251103_171312" src="https://github.com/user-attachments/assets/f4d02fcd-1cf1-4af2-9192-6168746bdb96" />
<img width="1010" height="675" alt="Screenshot_20251103_171324" src="https://github.com/user-attachments/assets/6db3f41e-e568-4152-9c51-ba0a65b08d43" />


# Changelog

## [2.4.3] 2025-11-03

- Added Overview Hotkeys tab with full press/click/wheel mapping support (scope: o_*).
- Added Congratulations Hotkeys tab with full press/click/wheel mapping support (scope: c_*).
- Introduced deck_browser action to open the Decks selector (equivalent to key D).
- Set defaults: o_click_right → deck_browser and c_click_right → deck_browser.
- Unified right‑click handling through the shortcut engine and suppressed context menus when right‑click is mapped.
- Kept study_now and overview wheel detection with safe JS injection; preserved fallback when no o_wheel_* mapping is configured.
### Defaults and Reset

- Shipped defaults include `o_click_right → deck_browser` and `c_click_right → deck_browser`.  

## [2.3.0] - 2025-11-01

### Added
- User-configurable Overview hotkeys with a new “o_” scope, e.g., `o_wheel_down` for the deck overview screen. (event.py, config.py)
- New `study_now` action that triggers the Overview “Study Now” button. (event.py)
- A third “Overview Hotkeys” tab in the add-on’s GUI config window so users can add/edit `o_*` shortcuts like other hotkeys. (config.py)

### Changed
- Wheel capture script is now injected into Overview as well as Reviewer, enabling scroll detection on the deck overview screen. (event.py)
- Unified wheel handling: Overview and Reviewer wheel events are routed through the same shortcut engine. (event.py)
- Hotkey builder now emits the correct scope prefix for Overview (`o_`), in addition to Question (`q_`) and Answer (`a_`). (event.py)

### Fixed
- Deck overview scroll-down not triggering “Study Now” in some cases by adding a safe fallback that clicks “Study Now” on `o_wheel_down` when no mapping fires. (event.py)
- Card rating screen not responding to immediate second scroll after “Show Answer” by removing the wheel cooldown right after `show_ans`. (event.py)
- Startup `NameError` by ensuring `install_event_handlers` is defined before hook registration and instantiation is done after definitions. (event.py)

### Compatibility
- Safer class lookups for `Overview` and `Reviewer` to avoid import-timing issues on newer Anki/Qt versions. (event.py)
- Preserved right-click/context-menu and extra-button navigation protections in review, consistent with prior behavior. (event.py)

### Config Defaults
- Added a default mapping example for Overview: `o_wheel_down: "study_now"`. (config.json)

### Notes
- No content changes to `web/detect_wheel.js`; it is now injected for Overview in addition to Reviewer. (event.py)
