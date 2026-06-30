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

See [CHANGELOG.md](CHANGELOG.md) for the full release history.
