[Fork of Review [Hotmouse](https://ankiweb.net/shared/info/1928346827). For more info read original description.

# Changelog

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
](https://github.com/athulkrishna2015/Review-Hotmouse-Plus)
