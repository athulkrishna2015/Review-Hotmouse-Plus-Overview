# [Review Hotmouse Plus Overview](https://github.com/athulkrishna2015/Review-Hotmouse-Plus-Overview/)

[Install via ankiweb](https://ankiweb.net/shared/info/1054369752)

Configurable mouse hotkeys for Anki’s review workflow, now extended to the Overview screen and Congratulations screen with a built‑in deck_browser action to jump to the Decks selector.  
**Pro Tip**: Double-click the middle mouse button (scroll wheel) to quickly enable or disable the add-on at any time.  
**New**: Hold the middle mouse button and move up/down to scroll long cards — like browser autoscroll.

This add-on pairs well with [Deck Centerer]
(https://ankiweb.net/shared/info/1520580564) and  [Audiovisual Feedback](https://ankiweb.net/shared/info/231569866).
It also plays nicely with “[Edit Field During Review (Cloze)](https://ankiweb.net/shared/info/385888438)” by automatically pausing Hotmouse while a field is being edited and restoring it after the edit completes.

## Configuration

Open Tools → Add‑ons → Review Hotmouse Plus Overview → Config and use the tabs:
- General: Configure thresholds and scrolling behavior.
    - **Mouse scroll threshold**: Delay (ms) between subsequent scroll actions.
    - **Mouse click threshold**: Delay (ms) between subsequent click actions (0 for instant).
    - **Wheel/Trackpad distance threshold**: Amount of "scroll distance" accumulated before a hotkey fires. Lower values make trackpad swipes more sensitive. Default is **60**; **120** matches the older wheel sensitivity.
    - **Horizontal Trackpad Swipes**: Support for swiping left/right on trackpads (horizontal scroll). Configurable just like vertical scroll. Default mapping: **Swipe Left = Hard**, **Swipe Right = Easy** during the answer phase.
    - **Natural scrolling (invert horizontal swipe)**: Enable if your trackpad uses natural (reverse) scrolling. Flips the left/right swipe direction so it matches your finger movement. Enabled by default.
    - **Ignore wheel on side scroll bar**: If enabled, allows normal scrolling when the mouse is over the side scrollbar area.
    - **Wheel hotkeys only on bottom bar**: If enabled, mouse wheel actions only trigger hotkeys when the pointer is over the bottom rating bar, allowing normal scrolling everywhere else.
    - **Smart scroll for long cards**: If enabled, allows the mouse wheel to scroll long cards normally. Wheel hotkeys (e.g. scroll down to show answer) only trigger when you reach the top or bottom of the page and scroll again. **If your mouse is over the bottom rating bar, hotkeys will always trigger instantly, bypassing this.** Disabled by default, and always off on the Overview screen.
    - **Mouse wheel fallback**: When Smart scroll is off, Review and Overview wheel hotkeys use the native Qt wheel path for more reliable mouse-wheel triggering. Trackpads still work through the wheel/scroll accumulation path.
    - **Middle-click drag to scroll**: Hold the middle mouse button and move up/down to scroll the page (like browser autoscroll). The cursor changes to a scroll icon while active. Enabled by default.
        - **Dead zone** (default 15 px): The area around the click origin where no scrolling occurs — prevents accidental scrolling from small hand movements. Increase for more stability, decrease for quicker response.
        - **Scroll sensitivity** (default 5, range 1–20): Controls how fast the page scrolls relative to mouse distance. The farther you move from the click point (beyond the dead zone), the faster it scrolls. Higher values = faster scrolling with less mouse movement.
    - **Mouse undo behavior**: Right-click undo prioritizes add-on actions triggered by mouse in the current session.
    - **Right-click undo can use global undo**: If enabled, right-click undo falls back to Anki global undo for any action. If disabled, it only falls back for whitelisted actions (like "Undo Answer Card" or actions in meta.json).
    - **Right-click again for global undo**: If enabled, when mouse undo is unavailable, a second right-click within 6 seconds will trigger global undo.
- Trackpad Actions: Configure swipe up/down/left/right actions for Question, Answer, Overview, and Congratulations screens.
- Overview Hotkeys: add/edit `o_*` mappings.
- Congratulations Hotkeys: add/edit `c_*` mappings.
- Question/Answer Hotkeys: unchanged; continue to use again/hard/good/easy/undo/etc.  
- Edit‑During‑Review: If you use “Edit Field During Review (Cloze)”, Hotmouse temporarily suspends while you edit a field and resumes when the edit finishes.

If you are upgrading from an older release: changing the shipped defaults does not rewrite your already-saved Anki config. If Smart scroll still seems enabled, turn it off once in the General tab or use Restore Defaults.

## Acknowledgments

This project is a fork and extension of the original “[Review Hotmouse](https://github.com/BlueGreenMagick/Review-Hotmouse/)” Anki add‑on; full credit for the concept and foundational code goes to the original author(s)

For more info read original [description](https://ankiweb.net/shared/info/1928346827).

**Developers**: For setup and building instructions, please see **[DEVELOPMENT.md](./DEVELOPMENT.md)**.

## Screenshots

<img width="1010" height="675" alt="Screenshot_20251103_171312" src="https://github.com/user-attachments/assets/f4d02fcd-1cf1-4af2-9192-6168746bdb96" />
<img width="1010" height="675" alt="Screenshot_20251103_171324" src="https://github.com/user-attachments/assets/6db3f41e-e568-4152-9c51-ba0a65b08d43" />

## Support

If you find this add-on useful, please consider supporting its development:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/D1D01W6NQT)

# Changelog

## 2026-04-11

- **Trackpad axis locking**: Fixed horizontal two-finger swipes not triggering on trackpads. Added gesture-level axis locking in the JS wheel handler — once a dominant axis (horizontal/vertical) is detected during a continuous swipe, the add-on commits to it and filters out cross-axis noise. The Python-side scroll accumulator is now also axis-aware and no longer resets when imprecise finger movement causes momentary direction jitter.
- **Natural scrolling option**: Added a `natural_scrolling` config toggle (General tab). When enabled (default), horizontal swipe direction matches physical finger movement — needed for systems with natural/reverse scrolling. Disable it if left/right swipe actions appear reversed on your setup.
- **Scrolling restored when addon disabled**: Disabling the addon via double-click toggle (middle mouse) no longer blocks page scrolling. The JS wheel handler now checks the addon's enabled state and skips `preventDefault` when disabled.
- **Editor/browser scrolling fix**: Fixed scrolling being blocked in the Edit Note dialog, browser, and other non-review windows. The wheel-interception JS was being injected into any webview loading while `mw.state` was "review" — now it only injects into the actual review/overview webview. The native event filter also only intercepts events during review/overview states.
- **Mouse wheel fallback restored**: Review and Overview wheel hotkeys now work natively again when smart scroll is off, fixing cases where only trackpad gestures were firing.
- **Overview wheel fix**: Overview hotkeys now use the same non-smart native fallback path as review when smart scroll is disabled.
- **More sensitive trackpad default**: Reduced the default wheel/trackpad threshold from 120 to 80 so swipes trigger sooner.
- **Review/Overview smart scroll fix**: When Smart scroll is enabled, wheel gestures stay on the webview JS path so long cards can scroll naturally before Show Answer or rating actions fire.
- **Trackpad delta fix**: Preserved fractional wheel deltas from the webview so smooth trackpad swipes can accumulate reliably, including left/right gestures.
- **New Trackpad Actions tab**: Added a dedicated config tab for swipe up/down/left/right actions across Question, Answer, Overview, and Congratulations screens.
- **Fixed scroll debounce bug**: Continuous scrolling could both show the answer and rate the card in a single scroll gesture. Now requires two separate scroll actions — one to show the answer and another to rate.
- **Middle-click drag scroll**: Hold the middle mouse button and move up/down to smoothly scroll long cards. Configurable dead zone and sensitivity in the General tab. Enabled by default.
- **Smart scroll for long cards**: Added an option to let the mouse wheel scroll long cards normally. Wheel hotkeys only trigger when you've reached the end of the content. Disabled by default in the current release.
- **Improved Trackpad Support**: Implemented a scroll accumulator and **Horizontal Swipe support**. You can now swipe left/right on your trackpad to rate cards (Default: Left = Hard, Right = Easy).

## 2026-03-19

- **Optional Undo Guard**: Re-introduced the two-step undo confirmation as a toggle: **"Right-click again for global undo"**.
- **Simplified Mouse Undo**: Unified undo handling to prioritize session history before falling back to global/whitelisted undo.
- **Global Undo Fallback**: When `right_click_global_undo` is enabled, right-click undo falls back to global Anki undo.
- **Undo Whitelisting**: When global undo is disabled, right-click undo now only falls back for whitelisted actions (default keywords: "answer", "review", "rating", "card", "score") or actions specified in `meta.json`. This prevents accidentally undoing card edits or other non-review actions.
- **Smart Tooltips**: Improved notifications to suggest using **Ctrl+Z** for global undo or right-clicking again if the undo guard is enabled.
- **Custom Whitelist**: Added `undo_whitelist` config key for custom allowed global undo actions.
- Updated right-click `undo_hotmouse` to prioritize only mouse-triggered add-on actions from the current session.
- Extended right-click mouse undo chaining for session-triggered actions, including repeated answer-card undos plus non-collection actions like `show_ans`, `study_now`, and `deck_browser`.
- Unified mouse undo around a single session history stack of undoable actions (collection + navigation).
- Added intuitive navigation unwind after `study_now`: once card-answer undos are exhausted, mouse undo returns to Overview.
- Improved EFDRC compatibility handling by making suspend/resume detection more resilient across context/message variations.
- Updated version tooling to use semantic `major.minor.patch` format across `bump.py`, `make_ankiaddon.py`, and `new_version.py`.
- Fixed `show_ans` to reliably reveal the answer card in review.
- Added legacy `<none>` action compatibility as a true no-op action.
- Fixed v1 compatibility hotkey validation so shortcuts ending in `_press` are correctly detected and migrated.

## 2026-03-18

- Auto-suspend Hotmouse while editing fields with [“Edit Field During Review (Cloze)](https://ankiweb.net/shared/info/385888438)”, then restore it when editing ends.

## 2026-03-13

- Automated the **Build and Release** process for faster updates.
- Updated internal **Compatibility Layer** and version tracking.

## 2026-03-13

- Added **Support Tab** with scan-friendly QR codes and copyable donation IDs.
- Added **Tools Menu Entry** for easier access to the configuration window.
- Added **Double-Click Toggle** on the middle mouse button to quickly enable/disable the addon.
- Fixed circular import issues causing crashes on Anki startup.
- Fixed missing `Path` and `simplejson` library errors.

## 2026-02-14

- Added optional support for mouse scrolling in the Reviewer and Overview.
- New setting: **Ignore wheel on side scroll bar** allows normal scrolling when the pointer is over the scrollbar area.
- New setting: **Wheel hotkeys only on bottom bar** restricts hotmouse actions to the bottom rating bar, allowing normal scrolling in the main card area.
- Updated `detect_wheel.js` to intelligently detect mouse position and element context.

## 2025-11-06

- Added threshold_click_ms setting (milliseconds) with a new “Mouse click threshold (1000 is 1 s)” control in the General tab; default 0 ms to disable click debouncing for maximum responsiveness.
- Introduced a separate click debounce clock (last_click_time) and filtering in on_mouse_press that respects threshold_click_ms to prevent accidental rapid double‑activations when desired.
- ~~After show_ans, the add‑on now clears both wheel and click cooldowns~~ (removed in 2026-04-11 to prevent accidental single-scroll rating).
- Backward compatibility: if threshold_click_ms is missing it behaves as 0 ms; the config manager tolerates unknown keys, so existing setups remain stable.
- Refined General tab copy to use SI phrasing (“1000 is 1 s”).


## 2025-11-03

- Added Overview Hotkeys tab with full press/click/wheel mapping support (scope: o_*).
- Added Congratulations Hotkeys tab with full press/click/wheel mapping support (scope: c_*).
- Introduced deck_browser action to open the Decks selector (equivalent to key D).
- Set defaults: o_click_right → deck_browser and c_click_right → deck_browser.
- Unified right‑click handling through the shortcut engine and suppressed context menus when right‑click is mapped.
- Kept study_now and overview wheel detection with safe JS injection; preserved fallback when no o_wheel_* mapping is configured.
### Defaults and Reset

- Shipped defaults include `o_click_right → deck_browser` and `c_click_right → deck_browser`.  

## 2025-11-01

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
- ~~Card rating screen not responding to immediate second scroll after “Show Answer” by removing the wheel cooldown right after `show_ans`~~ (reverted in 2026-04-11; scroll threshold now enforced between show_ans and rating). (event.py)
- Startup `NameError` by ensuring `install_event_handlers` is defined before hook registration and instantiation is done after definitions. (event.py)

### Compatibility
- Safer class lookups for `Overview` and `Reviewer` to avoid import-timing issues on newer Anki/Qt versions. (event.py)
- Preserved right-click/context-menu and extra-button navigation protections in review, consistent with prior behavior. (event.py)

### Config Defaults
- Added a default mapping example for Overview: `o_wheel_down: "study_now"`. (config.json)

### Notes
- No content changes to `web/detect_wheel.js`; it is now injected for Overview in addition to Reviewer. (event.py)
