# Changelog

## v3.4.0 (2026-06-30)

- **Config Window Resizing**: Fixed the vertical height lock on the configuration GUI by wrapping General and Hotkey tabs inside a scrollable view. Users can now resize the config window to any height, and standard minimize/maximize buttons have been enabled.
- **Non-blocking Configuration Window**: Automatically closes Anki's modal "Add-ons" window when our configuration panel is launched, allowing users to interact with Anki's main screen and review cards while keeping settings open.
- **Configurable Edge Scroll Padding**: Added configurable left and right edge scroll paddings (defaulting to 20px) which allow users to scroll natively near the left and right window margins without triggering hotmouse shortcuts.
- **Instant Save**: Added a dedicated "Save" button to apply settings instantly without closing the configuration window, alongside the standard "Save & Close" button.

## v3.3.1 (2026-06-09)

- **Standard Context Menu on Selection**: Right-clicking now allows the standard context menu when text is selected, enabling easy copying from the review screen or AI hints section.
- **Performance Optimizations**:
    - **Async Logging**: Action logging moved to a background thread to prevent UI freezes on slow filesystems (e.g., portable drives).
    - **Reduced Latency**: Removed/reduced several hardcoded cooldowns and latches that were causing noticeable delays between subsequent mouse actions.
    - **Instant Wheel Reset**: The mouse wheel latch now resets instantly whenever the study state changes (e.g., card flipped or answered), allowing for much faster rapid-fire reviews.

## v3.3.0 (2026-06-05)

- **Non-modal Config Window**: The addon config panel is now non-modal and non-blocking, meaning you can fully use and interact with Anki while keeping the configuration options open.
- **Live Action Logs Tab**: Added a new "Logs" config tab displaying a live stream of executed Hotmouse actions, featuring "Copy" and "Clear" button controls and a setting to clear logs automatically on startup (runs asynchronously 500ms after boot to avoid disturbing Anki's startup process).
- **Unrecognized Undo Fallback**: Prevents rating history eviction and deck overview screen kickbacks when external addon database transactions (e.g., from AI-Hints) are encountered on the undo stack. Unrecognized undos now gracefully fallback to global undo (`Ctrl+Z`).
- **Robust Context Menu Undo**: Added context menu event filter fallback for mouse right-click actions with a 200ms deduplication window, ensuring right-click undo functions reliably even on dynamic webview panels.
- **Support tab & Autostart Welcomer**: Automatically displays the Support tab welcome screen exactly one time after each addon update (respecting donation opt-out metadata). Replaced fragile `addon_manifest` APIs with safe JSON parsing to prevent startup crashes on older Anki versions.

## 2026-04-21

- **Horizontal Scrollbar Exclusion**: Moving the mouse over the bottom horizontal scrollbar will now correctly allow native horizontal scrolling without triggering add-on actions, matching the existing behavior for vertical scrollbars.

## 2026-04-20

- **Multi-directional Middle-Click Drag**: Middle-click drag scrolling now supports both horizontal and vertical axes simultaneously.
- **Unmapped Scroll Pass-Through**: Trackpad swipes and scroll events now gracefully pass through to native scrolling if they are not explicitly mapped to any action in the current screen (e.g., swiping left/right on Question screen).

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
- **Updated right-click `undo_hotmouse` to prioritize only mouse-triggered add-on actions from the current session.**
- **Extended right-click mouse undo chaining for session-triggered actions, including repeated answer-card undos plus non-collection actions like `show_ans`, `study_now`, and `deck_browser`.**
- **Unified mouse undo around a single session history stack of undoable actions (collection + navigation).**
- **Added intuitive navigation unwind after `study_now`: once card-answer undos are exhausted, mouse undo returns to Overview.**
- **Improved EFDRC compatibility handling by making suspend/resume detection more resilient across context/message variations.**
- **Updated version tooling to use semantic `major.minor.patch` format across `bump.py`, `make_ankiaddon.py`, and `new_version.py`.**
- **Fixed `show_ans` to reliably reveal the answer card in review.**
- **Added legacy `<none>` action compatibility as a true no-op action.**
- **Fixed v1 compatibility hotkey validation so shortcuts ending in `_press` are correctly detected and migrated.**

## 2026-03-18

- Auto-suspend Hotmouse while editing fields with [“Edit Field During Review (Cloze)”, then restore it when editing ends.](https://ankiweb.net/shared/info/385888438)

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
- Startup `NameError` by ensuring `install_event_handlers` is defined before hook registration and instantiation is done after definitions. (event.py)

### Compatibility
- Safer class lookups for `Overview` and `Reviewer` to avoid import-timing issues on newer Anki/Qt versions. (event.py)
- Preserved right-click/context-menu and extra-button navigation protections in review, consistent with prior behavior. (event.py)

### Config Defaults
- Added a default mapping example for Overview: `o_wheel_down: "study_now"`. (config.json)

### Notes
- No content changes to `web/detect_wheel.js`; it is now injected for Overview in addition to Reviewer. (event.py)
