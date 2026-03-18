# [Review Hotmouse Plus Overview](https://github.com/athulkrishna2015/Review-Hotmouse-Plus-Overview/)

[Install via ankiweb](https://ankiweb.net/shared/info/1054369752)

Configurable mouse hotkeys for Anki’s review workflow, now extended to the Overview screen and Congratulations screen with a built‑in deck_browser action to jump to the Decks selector.  
**Pro Tip**: Double-click the middle mouse button (scroll wheel) to quickly enable or disable the add-on at any time.

This add-on pairs well with [Deck Centerer]
(https://ankiweb.net/shared/info/1520580564) and  [Audiovisual Feedback](https://ankiweb.net/shared/info/231569866).
It also plays nicely with “Edit Field During Review (Cloze)” by automatically pausing Hotmouse while a field is being edited and restoring it after the edit completes.

## Configuration

Open Tools → Add‑ons → Review Hotmouse → Config and use the tabs:
- General: Configure thresholds and scrolling behavior.
    - **Mouse scroll threshold**: Delay between subsequent scroll actions.
    - **Mouse click threshold**: Delay between subsequent clicks (0 for instant).
    - **Ignore wheel on side scroll bar**: If enabled, allows normal scrolling when the mouse is over the side scrollbar area.
    - **Wheel hotkeys only on bottom bar**: If enabled, mouse wheel actions only trigger hotkeys when the pointer is over the bottom rating bar, allowing normal scrolling everywhere else.
- Overview Hotkeys: add/edit `o_*` mappings.
- Congratulations Hotkeys: add/edit `c_*` mappings.
- Question/Answer Hotkeys: unchanged; continue to use again/hard/good/easy/undo/etc.  
- Edit‑During‑Review: If you use “Edit Field During Review (Cloze)”, Hotmouse temporarily suspends while you edit a field and resumes when the edit finishes.

## Acknowledgments

This project is a fork and extension of the original “[Review Hotmouse](https://github.com/BlueGreenMagick/Review-Hotmouse/)” Anki add‑on; full credit for the concept and foundational code goes to the original author(s)

For more info read original [description](https://ankiweb.net/shared/info/1928346827).

**Developers**: For setup and building instructions, please see **[DEVELOPMENT.md](./DEVELOPMENT.md)**.

## Screenshots

<img width="1010" height="675" alt="Screenshot_20251103_171312" src="https://github.com/user-attachments/assets/f4d02fcd-1cf1-4af2-9192-6168746bdb96" />
<img width="1010" height="675" alt="Screenshot_20251103_171324" src="https://github.com/user-attachments/assets/6db3f41e-e568-4152-9c51-ba0a65b08d43" />


# Changelog

## [2.8.1] 2026-03-18

- Auto-suspend Hotmouse while editing fields with [“Edit Field During Review (Cloze)](https://ankiweb.net/shared/info/385888438)”, then restore it when editing ends.

## [2.8] 2026-03-13

- Automated the **Build and Release** process for faster updates.
- Updated internal **Compatibility Layer** and version tracking.

## [2.7] 2026-03-13

- Added **Support Tab** with scan-friendly QR codes and copyable donation IDs.
- Added **Tools Menu Entry** for easier access to the configuration window.
- Added **Double-Click Toggle** on the middle mouse button to quickly enable/disable the addon.
- Fixed circular import issues causing crashes on Anki startup.
- Fixed missing `Path` and `simplejson` library errors.

## [2.6] 2026-02-14

- Added optional support for mouse scrolling in the Reviewer and Overview.
- New setting: **Ignore wheel on side scroll bar** allows normal scrolling when the pointer is over the scrollbar area.
- New setting: **Wheel hotkeys only on bottom bar** restricts hotmouse actions to the bottom rating bar, allowing normal scrolling in the main card area.
- Updated `detect_wheel.js` to intelligently detect mouse position and element context.

## [2.5.3] 2025-11-06

- Added threshold_click_ms setting (milliseconds) with a new “Mouse click threshold (1000 is 1 s)” control in the General tab; default 0 ms to disable click debouncing for maximum responsiveness.
- Introduced a separate click debounce clock (last_click_time) and filtering in on_mouse_press that respects threshold_click_ms to prevent accidental rapid double‑activations when desired.
- After show_ans, the add‑on now clears both wheel and click cooldowns and briefly forces the scope to Answer so the very next click can immediately rate without waiting, removing the perceived second‑click delay.
- Backward compatibility: if threshold_click_ms is missing it behaves as 0 ms; the config manager tolerates unknown keys, so existing setups remain stable.
- Refined General tab copy to use SI phrasing (“1000 is 1 s”) and kept existing wheel behavior; wheel cooldown continues to be cleared after show_ans as before.


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
