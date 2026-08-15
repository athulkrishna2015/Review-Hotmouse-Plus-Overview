# Review Hotmouse Plus Overview - Full Documentation

**Version**: 3.4.0
**Package**: `review-hotmouse`
**AnkiWeb ID**: [1054369752](https://ankiweb.net/shared/info/1054369752)

---

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [JSON Configuration Files](#json-configuration-files)
   - [config.json (Default Configuration)](#configjson-default-configuration)
   - [manifest.json](#manifestjson)
   - [meta.json](#metajson)
4. [Configuration Settings Reference](#configuration-settings-reference)
   - [Shortcuts Object](#shortcuts-object)
   - [General Settings](#general-settings)
   - [Scrolling & Wheel Settings](#scrolling--wheel-settings)
   - [Middle-Click Scroll Settings](#middle-click-scroll-settings)
   - [Undo Behavior Settings](#undo-behavior-settings)
   - [Debug & Display Settings](#debug--display-settings)
   - [Log Settings](#log-settings)
5. [Available Actions](#available-actions)
6. [Hotkey String Format](#hotkey-string-format)
   - [Scopes](#scopes)
   - [Input Modes](#input-modes)
   - [Buttons](#buttons)
   - [Wheel Directions](#wheel-directions)
   - [Building a Hotkey String](#building-a-hotkey-string)
7. [Config Window Tabs](#config-window-tabs)
   - [General Tab](#general-tab)
   - [Question Hotkeys Tab](#question-hotkeys-tab)
   - [Answer Hotkeys Tab](#answer-hotkeys-tab)
   - [Overview Hotkeys Tab](#overview-hotkeys-tab)
   - [Congratulations Hotkeys Tab](#congratulations-hotkeys-tab)
   - [Trackpad Actions Tab](#trackpad-actions-tab)
   - [Support Tab](#support-tab)
   - [Logs Tab](#logs-tab)
8. [Source Code Architecture](#source-code-architecture)
   - [addon/\_\_init\_\_.py](#addon__init__py)
   - [addon/config.py](#addonconfigpy)
   - [addon/event.py](#addoneventpy)
   - [addon/hotmouse/actions.py](#addonhotmouseactionspy)
   - [addon/hotmouse/manager.py](#addonhotmousemanagerpy)
   - [addon/hotmouse/web.py](#addonhotmousewebpy)
   - [addon/compat/](#addoncompat)
   - [addon/config_tabs/](#addonconfig_tabs)
   - [addon/ankiaddonconfig/](#addonankiaddonconfig)
   - [addon/web/detect_wheel.js](#addonwebdetect_wheeljs)
9. [Internal Variables & State](#internal-variables--state)
10. [Event Hooks & Integration](#event-hooks--integration)
11. [Third-Party Addon Compatibility](#third-party-addon-compatibility)

---

## Overview

Review Hotmouse Plus Overview is an Anki addon that provides configurable mouse hotkeys for Anki's review workflow. It extends functionality to the Overview screen, Congratulations screen, and provides deck browser navigation. The addon intercepts mouse button clicks, scroll wheel events, and trackpad gestures and maps them to Anki review actions like answering cards, showing answers, undoing, flagging, and more.

Key features:
- Mouse button click and scroll wheel mapping to review actions
- Trackpad swipe gesture support (horizontal and vertical)
- Smart scroll for long cards
- Middle-click drag-to-scroll
- Hotmouse-aware undo system that tracks addon-triggered actions
- Overview and Congratulations screen support
- Compatibility with "Edit Field During Review (Cloze)" addon

---

## Project Structure

```
Review-Hotmouse-plus-overview/
|-- addon/                          # Main addon package
|   |-- __init__.py                 # Entry point, loads config/event/compat
|   |-- config.py                   # ConfigManager setup and tab registration
|   |-- config.json                 # Default configuration values
|   |-- event.py                    # Event handler registration and hooks
|   |-- manifest.json               # Addon metadata (name, version)
|   |-- meta.json                   # User-saved configuration (Anki-managed)
|   |-- VERSION                     # Plain-text version string
|   |-- hotmouse.log                # Runtime log file
|   |-- hotmouse/                   # Core hotmouse engine
|   |   |-- __init__.py             # Package exports
|   |   |-- actions.py              # Action definitions and button/wheel enums
|   |   |-- manager.py              # HotmouseManager and HotmouseEventFilter
|   |   |-- web.py                  # JS injection and webview message handling
|   |-- config_tabs/                # GUI config tabs
|   |   |-- __init__.py             # Package exports
|   |   |-- general.py              # General settings tab
|   |   |-- hotkeys.py              # Hotkey editor tabs (Q/A/O/C)
|   |   |-- trackpad.py             # Trackpad swipe actions tab
|   |   |-- tab_support.py          # Support/donation tab
|   |   |-- logs.py                 # Log viewer tab
|   |-- ankiaddonconfig/            # Custom config management framework
|   |   |-- __init__.py             # Exports ConfigManager, ConfigWindow
|   |   |-- manager.py              # ConfigManager class
|   |   |-- window.py               # ConfigWindow and ConfigLayout classes
|   |   |-- errors.py               # InvalidConfigValueError
|   |-- web/                        # Web assets injected into Anki webviews
|   |   |-- detect_wheel.js         # JS wheel event interceptor
|   |-- Support/                    # Support tab assets
|       |-- BTC.jpg                 # Bitcoin QR code
|       |-- ETH.jpg                 # Ethereum QR code
|       |-- UPI.jpg                 # UPI QR code
|-- tests/                          # Test suite
|-- doc/                            # Documentation
|-- bump.py                         # Version bump script
|-- make_ankiaddon.py               # .ankiaddon package builder
|-- CHANGELOG.md                    # Release history
|-- DEVELOPMENT.md                  # Developer setup guide
|-- README.md                       # Project README
|-- LICENSE                         # License file
```

---

## JSON Configuration Files

### config.json (Default Configuration)

**File**: `addon/config.json`

This file defines the **default values** for all configuration settings. Anki reads this file to provide defaults when no user configuration exists. Users can override these values through the config window or by editing the JSON directly.

```json
{
    "shortcuts": {
        "q_wheel_down": "show_ans",
        "q_press_left_click_right": "off",
        "a_press_left_click_right": "off",
        "a_click_right": "undo_hotmouse",
        "q_click_right": "undo_hotmouse",
        "a_wheel_up": "again",
        "a_wheel_down": "good",
        "a_wheel_left": "hard",
        "a_wheel_right": "easy",
        "a_press_middle_wheel_up": "hard",
        "a_press_middle_wheel_down": "easy",
        "o_wheel_down": "study_now",
        "o_click_right": "deck_browser",
        "c_click_right": "deck_browser"
    },
    "default_enabled": true,
    "threshold_wheel_ms": 350,
    "threshold_click_ms": 0,
    "wheel_ignore_scrollbar": true,
    "wheel_only_on_bottom_bar": false,
    "right_click_global_undo": false,
    "right_click_undo_confirmation": true,
    "tooltip": false,
    "z_debug": false,
    "undo_whitelist": [
        "Undo Answer Card"
    ],
    "middle_click_scroll": true,
    "middle_click_dead_zone": 15,
    "middle_click_sensitivity": 5,
    "smart_scroll": false,
    "natural_scrolling": true,
    "natural_scrolling_vertical": false,
    "scroll_accumulation_threshold": 60,
    "state_change_cooldown_ms": 300,
    "clear_logs_on_startup": true,
    "wheel_edge_padding_left": 20,
    "wheel_edge_padding_right": 20
}
```

### manifest.json

**File**: `addon/manifest.json`

Addon identification metadata. Used by the addon to read its own version for the support-tab update check.

```json
{
  "package": "review-hotmouse",
  "name": "Review Hotmouse Plus Overview",
  "human_version": "3.4.0",
  "version": "3.4.0"
}
```

| Key | Type | Description |
|-----|------|-------------|
| `package` | string | Internal package identifier |
| `name` | string | Human-readable addon name |
| `human_version` | string | Display version string |
| `version` | string | Semantic version string |

### meta.json

**File**: `addon/meta.json`

Anki-managed file that stores the **user's saved configuration** and addon metadata. This file is written by Anki when the user saves config changes. It merges the user's overridden values with the defaults from `config.json`.

| Key | Type | Description |
|-----|------|-------------|
| `config` | object | Complete user configuration (same schema as config.json) |
| `last_showed_support_version` | string | Version string when the Support tab was last auto-shown |
| `supporter_opt_out` | boolean | If `true`, the Support tab will not auto-open on updates |

---

## Configuration Settings Reference

### Shortcuts Object

**Key**: `shortcuts`
**Type**: `object` (Dictionary of hotkey string to action string)
**Default**: See [config.json section](#configjson-default-configuration)

Maps hotkey strings to action strings. Each key is a hotkey string following the [Hotkey String Format](#hotkey-string-format), and each value is an action string from [Available Actions](#available-actions).

#### Default Shortcut Mappings

| Hotkey String | Action | Description |
|---|---|---|
| `q_wheel_down` | `show_ans` | Scroll down on Question screen shows the answer |
| `q_press_left_click_right` | `off` | Hold left + right-click on Question disables hotmouse |
| `a_press_left_click_right` | `off` | Hold left + right-click on Answer disables hotmouse |
| `a_click_right` | `undo_hotmouse` | Right-click on Answer undoes last hotmouse action |
| `q_click_right` | `undo_hotmouse` | Right-click on Question undoes last hotmouse action |
| `a_wheel_up` | `again` | Scroll up on Answer rates "Again" |
| `a_wheel_down` | `good` | Scroll down on Answer rates "Good" |
| `a_wheel_left` | `hard` | Scroll/swipe left on Answer rates "Hard" |
| `a_wheel_right` | `easy` | Scroll/swipe right on Answer rates "Easy" |
| `a_press_middle_wheel_up` | `hard` | Hold middle + scroll up on Answer rates "Hard" |
| `a_press_middle_wheel_down` | `easy` | Hold middle + scroll down on Answer rates "Easy" |
| `o_wheel_down` | `study_now` | Scroll down on Overview starts studying |
| `o_click_right` | `deck_browser` | Right-click on Overview goes to deck browser |
| `c_click_right` | `deck_browser` | Right-click on Congratulations goes to deck browser |

### General Settings

| Key | Type | Default | Range | Description |
|-----|------|---------|-------|-------------|
| `default_enabled` | boolean | `true` | - | Whether the addon is enabled when Anki starts. If `false`, must be manually enabled via double-click middle mouse or context menu. |

### Scrolling & Wheel Settings

| Key | Type | Default | Range | Description |
|-----|------|---------|-------|-------------|
| `threshold_wheel_ms` | integer | `350` | 0-3000 | Minimum delay in milliseconds between subsequent scroll-triggered actions. Prevents accidental double-triggers from fast scrolling. |
| `threshold_click_ms` | integer | `0` | 0-3000 | Minimum delay in milliseconds between subsequent click-triggered actions. `0` means instant response with no delay. |
| `scroll_accumulation_threshold` | integer | `60` | 1-1200 | Amount of "scroll distance" (pixel delta accumulation) needed before a hotkey fires. Lower values make trackpad swipes more sensitive. `60` is the default; `120` matches older wheel-only sensitivity. |
| `state_change_cooldown_ms` | integer | `300` | 0-2000 | Ignore scroll events for this many milliseconds after a card question or answer is shown. Prevents double-triggering from trackpad inertia continuing after a state change. |
| `wheel_ignore_scrollbar` | boolean | `true` | - | When `true`, allows normal scrolling when the mouse pointer is within 30px of the right edge or bottom edge (scrollbar area). |
| `wheel_only_on_bottom_bar` | boolean | `false` | - | When `true`, wheel hotkeys only trigger when the mouse pointer is over the bottom rating bar. Normal scrolling works everywhere else. |
| `wheel_edge_padding_left` | integer | `20` | 0-500 | Number of pixels from the left edge of the Anki window where normal scrolling is allowed (hotkeys are not intercepted). |
| `wheel_edge_padding_right` | integer | `20` | 0-500 | Number of pixels from the right edge of the Anki window where normal scrolling is allowed (hotkeys are not intercepted). |
| `smart_scroll` | boolean | `false` | - | When `true`, allows the mouse wheel to scroll long cards normally. Hotkeys only trigger when the user reaches the top or bottom of the page and scrolls again. Always off on the Overview screen. If the mouse is over the bottom bar, hotkeys trigger instantly regardless of this setting. |
| `natural_scrolling` | boolean | `true` | - | When `true`, inverts horizontal scroll/swipe direction to match natural (reverse) scrolling used by most trackpads. Affects how `wheel_left` and `wheel_right` map to physical finger movements. |
| `natural_scrolling_vertical` | boolean | `false` | - | When `true`, inverts vertical scroll/swipe direction to match natural (reverse) scrolling used by most trackpads. Affects how `wheel_up` and `wheel_down` map to physical finger movements. |

### Middle-Click Scroll Settings

| Key | Type | Default | Range | Description |
|-----|------|---------|-------|-------------|
| `middle_click_scroll` | boolean | `true` | - | When `true`, holding the middle mouse button and moving the mouse scrolls the page (like browser autoscroll). The cursor changes to a scroll icon while active. |
| `middle_click_dead_zone` | integer | `15` | 0-100 | Minimum distance in pixels from the click origin before scrolling starts. Prevents accidental scrolling from small hand movements. |
| `middle_click_sensitivity` | integer | `5` | 1-20 | Controls how fast the page scrolls relative to mouse distance. The value is divided by 10 internally (so `5` = `0.5x` multiplier). Higher values = faster scrolling with less mouse movement. |

### Undo Behavior Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `right_click_global_undo` | boolean | `false` | When `true`, right-click undo falls back to Anki's global undo for **any** action when mouse undo history is exhausted. Mutually exclusive with `right_click_undo_confirmation`. |
| `right_click_undo_confirmation` | boolean | `true` | When `true` and mouse undo is unavailable, shows a tooltip and allows a **second** right-click within 6 seconds to trigger global undo. Mutually exclusive with `right_click_global_undo`. |
| `undo_whitelist` | array of strings | `["Undo Answer Card"]` | List of undo action text strings that are allowed to be undone by right-click even when they weren't triggered by the mouse. Matching is case-insensitive and supports partial/substring matching. Can also be set in `meta.json` under keys `undo_whitelist`, `allowed_undo_actions`, or `undo_actions`. |

### Debug & Display Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `tooltip` | boolean | `false` | When `true`, shows a tooltip with the action name each time a hotkey action is triggered. |
| `z_debug` | boolean | `false` | When `true`, shows a tooltip with the raw hotkey string on every mouse action. Useful for debugging hotkey mappings. The `z_` prefix keeps it sorted last in the JSON. |

### Log Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `clear_logs_on_startup` | boolean | `true` | When `true`, the `hotmouse.log` file is cleared each time Anki starts. When `false`, logs accumulate across sessions. |

---

## Available Actions

These are all the valid action strings that can be assigned to hotkey mappings:

| Action String | Description | Scope |
|---|---|---|
| *(empty string)* | No action (does nothing) | Any |
| `<none>` | No action (explicit no-op) | Any |
| `on` | Enable hotmouse | Any |
| `off` | Disable hotmouse | Any |
| `on_off` | Toggle hotmouse on/off | Any |
| `undo` | Trigger Anki's global undo | Review |
| `undo_hotmouse` | Undo last hotmouse-triggered action (smart undo) | Review |
| `show_ans` | Show the answer side of the current card | Question |
| `again` | Answer the card as "Again" (button 1) | Answer |
| `hard` | Answer the card as "Hard" (button 2, only with 4 buttons) | Answer |
| `good` | Answer the card as "Good" (button 2 or 3 depending on count) | Answer |
| `easy` | Answer the card as "Easy" (button 3 or 4 depending on count) | Answer |
| `delete` | Delete the current note | Review |
| `suspend_card` | Suspend the current card | Review |
| `suspend_note` | Suspend the entire note | Review |
| `bury_card` | Bury the current card | Review |
| `bury_note` | Bury the entire note | Review |
| `mark` | Toggle mark on the current note | Review |
| `red` | Set flag 1 (red) | Review |
| `orange` | Set flag 2 (orange) | Review |
| `green` | Set flag 3 (green) | Review |
| `blue` | Set flag 4 (blue) | Review |
| `audio` | Replay audio on the current card | Review |
| `record_voice` | Record voice for the current card | Review |
| `replay_voice` | Replay recorded voice | Review |
| `study_now` | Start studying from the Overview screen | Overview |
| `deck_browser` | Navigate to the deck browser | Any |

---

## Hotkey String Format

Hotkey strings encode the complete input combination: the screen scope, held buttons, and the triggering action (click or wheel).

### Scopes

The first character of a hotkey string defines which Anki screen it applies to:

| Prefix | Scope | Description |
|--------|-------|-------------|
| `q` | Question | When reviewing, on the question side |
| `a` | Answer | When reviewing, on the answer side |
| `o` | Overview | On the deck overview screen |
| `c` | Congratulations | On the congratulations/finished screen |
| `x` | Other | Any other Anki state (not normally mapped) |

### Input Modes

| Mode | Description |
|------|-------------|
| `press` | A button that is held down (modifier) |
| `click` | A button that is clicked (trigger) |
| `wheel` | A scroll wheel or trackpad gesture (trigger) |

### Buttons

| Button Name | Description |
|-------------|-------------|
| `left` | Left mouse button |
| `right` | Right mouse button |
| `middle` | Middle mouse button (scroll wheel click) |
| `xbutton1` | Extra mouse button 1 (side button, back) |
| `xbutton2` | Extra mouse button 2 (side button, forward) |

### Wheel Directions

| Direction | Description |
|-----------|-------------|
| `up` | Scroll up / swipe up |
| `down` | Scroll down / swipe down |
| `left` | Scroll left / swipe left |
| `right` | Scroll right / swipe right |

### Building a Hotkey String

Format: `{scope}_{press_button1}_..._{click_button|wheel_direction}`

Examples:
- `q_wheel_down` - Question screen, scroll wheel down
- `a_click_right` - Answer screen, right-click
- `a_press_middle_wheel_up` - Answer screen, hold middle button + scroll up
- `q_press_left_click_right` - Question screen, hold left + right-click
- `o_wheel_down` - Overview screen, scroll wheel down
- `c_click_right` - Congratulations screen, right-click

A hotkey must end with either a `click_{button}` or `wheel_{direction}` trigger. Zero or more `press_{button}` modifiers can precede the trigger. Multiple held buttons are sorted by the `Button` enum order (`left`, `right`, `middle`, `xbutton1`, `xbutton2`).

---

## Config Window Tabs

The addon provides a custom configuration window accessible via Tools > Add-ons > Review Hotmouse Plus Overview > Config.

### General Tab

Contains all non-hotkey settings organized as checkboxes and number inputs:

| Widget | Config Key | Type | Description |
|--------|-----------|------|-------------|
| Number input | `threshold_wheel_ms` | int (0-3000) | Mouse scroll threshold |
| Number input | `state_change_cooldown_ms` | int (0-2000) | State change cooldown |
| Number input | `threshold_click_ms` | int (0-3000) | Mouse click threshold |
| Number input | `scroll_accumulation_threshold` | int (1-1200) | Wheel/Trackpad distance threshold |
| Checkbox | `default_enabled` | bool | Addon enabled at start |
| Checkbox | `wheel_ignore_scrollbar` | bool | Ignore wheel on scrollbar |
| Number input | `wheel_edge_padding_left` | int (0-500) | Left edge scroll padding |
| Number input | `wheel_edge_padding_right` | int (0-500) | Right edge scroll padding |
| Checkbox | `wheel_only_on_bottom_bar` | bool | Wheel only on bottom bar |
| Checkbox | `smart_scroll` | bool | Smart scroll for long cards |
| Checkbox | `natural_scrolling` | bool | Natural scrolling (invert horizontal) |
| Checkbox | `natural_scrolling_vertical` | bool | Natural scrolling (invert vertical) |
| Checkbox | `right_click_global_undo` | bool | Right-click global undo |
| Checkbox | `right_click_undo_confirmation` | bool | Right-click again for global undo |
| Checkbox | `middle_click_scroll` | bool | Middle-click drag to scroll |
| Number input | `middle_click_dead_zone` | int (0-100) | Dead zone pixels |
| Number input | `middle_click_sensitivity` | int (1-20) | Scroll sensitivity |
| Checkbox | `tooltip` | bool | Show action name tooltip |
| Checkbox | `z_debug` | bool | Debug mode (show hotkey string) |

Note: `right_click_global_undo` and `right_click_undo_confirmation` are mutually exclusive. Enabling one automatically disables the other.

### Question Hotkeys Tab

Editable list of hotkeys prefixed with `q_`. Users can add/remove rows, each with dropdown selectors for input mode, button/direction, and action.

### Answer Hotkeys Tab

Editable list of hotkeys prefixed with `a_`. Same UI as Question tab.

### Overview Hotkeys Tab

Editable list of hotkeys prefixed with `o_`. Same UI as Question tab.

### Congratulations Hotkeys Tab

Editable list of hotkeys prefixed with `c_`. Same UI as Question tab.

### Trackpad Actions Tab

Simplified interface for configuring swipe actions. Provides dropdown selectors for each combination of screen context (Question, Answer, Overview, Congratulations) and direction (Swipe Up, Swipe Down, Swipe Left, Swipe Right). These map to the `{scope}_wheel_{direction}` hotkey entries under the hood.

### Support Tab

Displays donation options (Ko-fi widget, UPI, BTC, ETH QR codes). Contains a checkbox "I have supported this addon" that sets `supporter_opt_out` in `meta.json` to prevent the tab from auto-opening on future updates.

### Logs Tab

Displays the contents of `hotmouse.log` in real-time (refreshed every 1 second). Provides:
- **Copy** button to copy log contents to clipboard
- **Clear** button to empty the log file
- **Clear logs on startup** checkbox (maps to `clear_logs_on_startup` config key)

---

## Source Code Architecture

### addon/\_\_init\_\_.py

**Purpose**: Entry point for the addon. Loaded by Anki when the addon starts.

**Behavior**:
1. Imports `config` module (initializes ConfigManager and registers config tabs)
2. Imports `event` module (sets up all event handlers and hooks)
3. Imports and runs `compat()` with `"-1.-1"` (compatibility layer for upgrades from older versions)

### addon/config.py

**Purpose**: Initializes the configuration management system and registers all GUI config tabs.

**Key objects**:
- `conf` (`ConfigManager`): The global config manager instance
- `on_window_open()`: Hooks `refresh_config` to run on save and close

**Registered tabs** (in order):
1. `general_tab` - General settings
2. `hotkey_tabs` - Question/Answer/Overview/Congratulations hotkey editors
3. `trackpad_tab` - Trackpad swipe actions
4. `support_tab` - Support/donation
5. `logs_tab` - Log viewer

### addon/event.py

**Purpose**: Registers all Anki event hooks and initializes the runtime hotmouse engine.

**Key objects**:
- `config`: The raw config dictionary from Anki's addon manager
- `manager` (`HotmouseManager`): The central hotmouse state and event handler
- `hotmouseEventFilter` (`HotmouseEventFilter`): Qt event filter installed on webviews

**Functions**:
- `refresh_config()`: Reloads config from disk and pushes it to manager and web modules
- `turn_on()` / `turn_off()` / `toggle_on_off()`: Enable/disable hotmouse with tooltip feedback
- `check_show_support_on_update()`: After addon update, auto-opens config at Support tab (unless opted out)
- `maybe_clear_logs_on_startup()`: Clears `hotmouse.log` if `clear_logs_on_startup` is `true`
- `install_event_handlers()`: Main initialization function called when Anki's main window is ready

**Registered Anki hooks**:
| Hook | Handler | Description |
|------|---------|-------------|
| `main_window_did_init` | `install_event_handlers` | Install all handlers after main window is ready |
| `webview_will_show_context_menu` | Lambda | Adds "Enable Hotmouse" to context menu when disabled |
| `webview_will_set_content` | `inject_web_content` | Injects detect_wheel.js into webviews |
| `webview_did_receive_js_message` | `handle_js_message` | Processes messages from detect_wheel.js |
| `undo_state_did_change` | `on_undo_state_did_change` | Tracks undo state for hotmouse undo system |
| `reviewer_did_show_question` | `on_reviewer_did_show_question` | Resets wheel accumulator on question shown |
| `reviewer_did_show_answer` | `on_reviewer_did_show_answer` | Resets wheel accumulator on answer shown |

### addon/hotmouse/actions.py

**Purpose**: Defines all available actions, the `Button` and `WheelDir` enums, and the action registry.

**Key types**:

#### `Button` (Enum)
Maps mouse button names to Qt button constants:
- `left` = `Qt.MouseButton.LeftButton`
- `right` = `Qt.MouseButton.RightButton`
- `middle` = `Qt.MouseButton.MiddleButton`
- `xbutton1` = `Qt.MouseButton.XButton1`
- `xbutton2` = `Qt.MouseButton.XButton2`

#### `WheelDir` (Enum)
Scroll/swipe directions:
- `DOWN` = `-1`
- `UP` = `1`
- `LEFT` = `2`
- `RIGHT` = `3`

Methods:
- `from_qt(angle_delta, invert_x)`: Converts Qt wheel angle delta to WheelDir
- `from_web(dx, dy, invert_x)`: Converts JS wheel event deltas to WheelDir

#### `ACTIONS` (Dict[str, Callable])
Maps action name strings to callable functions. All 27 available actions are registered here.

#### Internal action sets:
- `_HOTMOUSE_UNDO_TRACK_SKIP_ACTIONS`: Actions that should NOT be tracked for undo (`""`, `"<none>"`, `"undo"`, `"undo_hotmouse"`)
- `_NON_COLLECTION_HOTMOUSE_UNDO_ACTIONS`: Actions that don't create collection-level undo entries (`"on"`, `"off"`, `"on_off"`, `"show_ans"`, `"study_now"`, `"deck_browser"`, `"audio"`, `"replay_voice"`, `"record_voice"`)

### addon/hotmouse/manager.py

**Purpose**: The core engine. Contains `HotmouseManager` (state management, event processing, undo tracking) and `HotmouseEventFilter` (Qt event filter).

**Module-level features**:
- Background logging thread (`_log_queue`, `_logger_thread_worker`)
- Custom exception hook that catches hotmouse-related crashes to the log
- `log_message(msg)`: Thread-safe logging function

#### `HotmouseManager` Class

**Instance variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `enabled` | bool | `config["default_enabled"]` | Whether hotmouse is currently active |
| `last_scroll_time` | datetime | `now()` | Timestamp of last processed scroll event |
| `last_click_time` | datetime | `now()` | Timestamp of last processed click event |
| `last_state_change_time` | datetime or None | `None` | Timestamp of last reviewer state change |
| `last_wheel_was_momentum` | bool | `False` | Whether the last wheel event was trackpad momentum/inertia |
| `has_wheel_hotkey` | bool | computed | Whether any shortcut contains "wheel" |
| `_suspend_reasons` | Set[str] | `set()` | Active reasons why hotmouse is suspended (e.g. `"efdr_edit"`) |
| `_suspend_prev_enabled` | bool | `False` | Was hotmouse enabled before suspension? |
| `_track_hotmouse_undo_next` | bool | `False` | Is the next undo entry expected to be from hotmouse? |
| `_track_hotmouse_action` | str or None | `None` | The action string being tracked for undo |
| `_track_hotmouse_undo_set_at` | datetime or None | `None` | When undo tracking was armed |
| `_track_hotmouse_undo_prev_step` | int or None | `None` | Undo step number before the tracked action |
| `_track_hotmouse_undo_token` | int | `0` | Monotonic token to invalidate stale undo captures |
| `_last_hotmouse_action` | str or None | `None` | Last action string executed by hotmouse |
| `_last_hotmouse_action_at` | datetime or None | `None` | When the last hotmouse action was executed |
| `_last_hotmouse_prev_state` | str or None | `None` | Anki state before last hotmouse action |
| `_last_hotmouse_prev_enabled` | bool or None | `None` | Whether hotmouse was enabled before last action |
| `_mouse_session_actions` | Set[str] | `set()` | All action strings executed in this session |
| `_mouse_undo_history` | List[Dict] | `[]` | Undo history entries (max 300, pruned after 30 min) |
| `_mouse_undo_chain_until` | datetime or None | `None` | Multi-undo chain timeout (10 seconds) |
| `_global_undo_armed_until` | datetime or None | `None` | Double-right-click global undo timeout (6 seconds) |
| `_wheel_accumulator` | float | `0.0` | Accumulated scroll distance since last trigger |
| `_last_wheel_dir` | WheelDir or None | `None` | Direction of last wheel event |
| `_wheel_action_latched` | bool | `False` | Whether a wheel action was just triggered (latch to prevent re-trigger) |
| `_wheel_action_dir` | WheelDir or None | `None` | Direction of the latched wheel action |
| `_mid_drag_active` | bool | `False` | Whether middle-click drag scrolling is active |
| `_mid_drag_origin_x` | int | `0` | X coordinate of middle-click drag origin |
| `_mid_drag_origin_y` | int | `0` | Y coordinate of middle-click drag origin |
| `_mid_drag_scroll_timer` | QTimer or None | `None` | Timer for continuous mid-drag scroll ticks (16ms interval) |
| `_mid_drag_speed_x` | float | `0.0` | Current horizontal scroll speed for mid-drag |
| `_mid_drag_speed_y` | float | `0.0` | Current vertical scroll speed for mid-drag |
| `_last_right_click_action_time` | datetime or None | `None` | Timestamp of last right-click action (for deduplication) |

**Key methods**:
- `enable()` / `disable()`: Toggle hotmouse state and sync to JS webview
- `suspend(reason)` / `resume(reason)`: Temporarily disable hotmouse for a given reason
- `refresh_shortcuts()`: Recalculate `has_wheel_hotkey` from current config
- `build_hotkey(btns, wheel, click)`: Construct a hotkey string from current state and input
- `execute_shortcut(hotkey_str)`: Look up and execute the action for a hotkey string
- `on_mouse_press(event)`: Handle mouse button press events
- `on_mouse_scroll(event)`: Handle wheel/scroll events
- `handle_scroll(wheel_dir, delta, qbtns)`: Core scroll processing with accumulation and thresholds
- `undo_last_hotmouse_action()`: Smart undo system for hotmouse-triggered actions
- `mark_next_undo_as_hotmouse(action_str)`: Arm undo tracking before an action executes
- `start_mid_drag(x, y)` / `stop_mid_drag()` / `update_mid_drag(x, y)`: Middle-click drag scroll

#### `HotmouseEventFilter` Class

Qt `QObject` event filter installed on Anki's webview widgets. Intercepts:
- `QEvent.Type.Wheel`: Scroll/wheel events (with momentum filtering)
- `QEvent.Type.MouseButtonPress`: Click events
- `QEvent.Type.MouseButtonRelease`: Release events (for mid-drag)
- `QEvent.Type.MouseMove`: Move events (for mid-drag)
- `QEvent.Type.MouseButtonDblClick`: Middle double-click to toggle on/off
- `QEvent.Type.ContextMenu`: Suppress context menu when right-click is bound
- `QEvent.Type.ChildAdded`: Auto-install filter on new child widgets

Only active during `review` and `overview` states.

#### Helper functions:
- `_should_handle_native_wheel(obj, event)`: Determines whether a native Qt wheel event should be processed based on edge padding, scrollbar position, bottom-bar-only mode, and smart scroll settings
- `_get_object_width(obj)` / `_get_object_height(obj)`: Cross-version widget dimension helpers
- `_event_x(event)` / `_event_y(event)`: Cross-version event position helpers
- `_is_bottom_web_target(obj)`: Checks if an object is part of the bottom webview
- `add_event_filter(object)`: Recursively installs the event filter on a widget and all children

### addon/hotmouse/web.py

**Purpose**: Handles JavaScript injection into Anki webviews and processes messages from the injected JS.

**Functions**:
- `WEBVIEW_TARGETS()`: Returns `[mw.web, mw.bottomWeb]` - the webviews to intercept
- `inject_web_content(web_content, context)`: Injects configuration and `detect_wheel.js` into reviewer/overview webviews
- `handle_js_message(handled, message, context)`: Processes `ReviewHotmouse#` prefixed messages from JS
- `on_context_menu(target, ev, _old)`: Wraps the webview context menu to suppress it when right-click is bound
- `_handle_external_editing_message(message, context)`: Detects "Edit Field During Review" messages to suspend/resume hotmouse

**Injected JS variables** (set via `<script>` tag in `<head>`):
| Variable | Source | Description |
|----------|--------|-------------|
| `window._hotmouse_config` | config | Object with scroll/wheel settings |
| `window._hotmouse_enabled` | manager.enabled | Boolean - is hotmouse active? |
| `window._hotmouse_shortcuts` | config.shortcuts | Full shortcuts object |
| `window._hotmouse_scope` | context | `'o'` for overview, `'r'` for review |

### addon/compat/

**Purpose**: Backward compatibility with older addon versions.

#### `__init__.py`
- `compat(prev_version_str)`: Runs `v1_compat()` if the previous version was `< 2.x`

#### `v1.py`
- `v1_compat()`: Migrates v1 config format:
  - Moves top-level shortcut keys into the `shortcuts` sub-object
  - Changes `""` actions to `"<none>"`
  - Renames hotkeys ending with `_press` to `_click`
  - Removes hotkeys using invalid buttons (xbutton 2-9) or invalid action strings
  - Notifies the user of any changes

### addon/config_tabs/

**Purpose**: Defines the GUI tabs for the config window.

#### `general.py`
Builds the General settings tab with all number inputs and checkboxes. Implements the mutual exclusion between `right_click_global_undo` and `right_click_undo_confirmation`.

#### `hotkeys.py`
- `HotkeyTabManager`: Manages a dynamic list of hotkey editor rows for a given scope
- `DDConfigLayout`: Custom layout with cascading dropdown menus for hotkey construction
- `hotkey_tabs()`: Creates four tabs (Question, Answer, Overview, Congratulations) each with their own `HotkeyTabManager`
- Hotkeys with duplicate key strings: only the last one is saved

#### `trackpad.py`
- Simplified swipe action configuration for trackpad users
- `TRACKPAD_CONTEXTS`: `[("q", "Question"), ("a", "Answer"), ("o", "Overview"), ("c", "Congratulations")]`
- `TRACKPAD_DIRECTIONS`: `[("up", "Swipe Up"), ("down", "Swipe Down"), ("left", "Swipe Left"), ("right", "Swipe Right")]`
- Maps to `{scope}_wheel_{direction}` shortcuts internally
- Only saves changes for dropdowns the user actually modified (dirty tracking)

#### `tab_support.py`
- Displays Ko-fi widget, UPI/BTC/ETH QR codes with copy-to-clipboard addresses
- `supporter_opt_out` checkbox persisted in `meta.json`

#### `logs.py`
- Real-time log viewer (1-second refresh interval)
- Reads from `addon/hotmouse.log`
- Auto-scrolls to bottom when already at bottom
- Clear and Copy buttons

### addon/ankiaddonconfig/

**Purpose**: Generic configuration management framework (can be reused by other addons).

#### `manager.py` - `ConfigManager`
- `load()`: Reads config from Anki's addon manager
- `save()`: Writes config to disk
- `load_defaults()`: Resets config to `config.json` defaults
- `get(key, default)`: Dot-notation key access (e.g. `"shortcuts.q_wheel_down"`)
- `set(key, value)`: Dot-notation key setting
- `open_config()`: Opens the custom config window
- `use_custom_window()`: Registers the custom window as the config action
- `add_config_tab(fn)`: Alias for `on_window_open(fn)` - registers a tab builder function

#### `window.py` - `ConfigWindow` and `ConfigLayout`
- `ConfigWindow`: QDialog with tabbed interface, Save/Cancel/Restore Defaults/Advanced buttons
- `ConfigLayout`: QBoxLayout subclass with convenience methods for building config UIs:
  - `checkbox(key, description, tooltip)` - Boolean toggle
  - `number_input(key, description, tooltip, min, max, step, decimal)` - Integer/float spinner
  - `dropdown(key, labels, values, description, tooltip)` - Dropdown selector
  - `text_input(key, description, tooltip)` - Text field
  - `color_input(key, description, tooltip, opacity)` - Color picker
  - `path_input(key, description, tooltip, get_directory, filter)` - File/directory browser
  - `shortcut_input(key, description, tooltip)` - Keyboard shortcut editor
  - Layout helpers: `text()`, `hlayout()`, `vlayout()`, `hseparator()`, `vseparator()`, `space()`, `stretch()`, `hcontainer()`, `vcontainer()`, `hscroll_layout()`, `vscroll_layout()`

#### `errors.py` - `InvalidConfigValueError`
Exception raised when a config value doesn't match its expected type. Shows the key name, expected type, and actual value.

### addon/web/detect_wheel.js

**Purpose**: JavaScript injected into Anki's webview to intercept wheel/scroll events and forward them to the Python backend.

**Key features**:
- Installs once per page load (guarded by `__reviewHotmouseWheelListenerInstalled`)
- Axis locking for trackpad gestures (accumulates 10px before locking to horizontal or vertical)
- Boundary latching for smart scroll (requires a second scroll after reaching top/bottom)
- Edge padding detection (left and right margins where events pass through)
- Scrollbar detection (events on scrollbar area pass through)
- Bottom bar detection (checks for `#checker` or `#bottombar` elements, or `innerHeight < 150`)
- Scrollable container detection (walks up DOM to find scrollable parents)
- Constructs hotkey strings and checks against `window._hotmouse_shortcuts` before intercepting
- Sends `pycmd("ReviewHotmouse#" + JSON.stringify(req))` with:
  - `key`: `"wheel"`
  - `valueX`: Effective horizontal delta
  - `valueY`: Effective vertical delta
  - `is_scrollbar`: Whether the event was on a scrollbar
  - `is_bottom`: Whether the event was on the bottom bar
  - `at_boundary`: Whether smart scroll boundary was reached

**Global JS variables used**:
| Variable | Type | Description |
|----------|------|-------------|
| `window._hotmouse_config` | Object | Scroll/wheel configuration |
| `window._hotmouse_enabled` | Boolean | Whether hotmouse is active |
| `window._hotmouse_shortcuts` | Object | Shortcut mappings |
| `window._hotmouse_scope` | String | `"o"` or `"r"` |
| `window.__reviewHotmouseWheelListenerInstalled` | Boolean | Guard against double-install |
| `window.__hotmouseBoundaryLatch` | Object | `{down: bool, up: bool}` boundary latch state |
| `window.__hotmouseBoundaryLatchTs` | Object | `{down: number, up: number}` boundary latch timestamps |
| `window.__hotmouseAxisLock` | Object | `{axis, cumX, cumY, lastTs}` axis lock state |

---

## Internal Variables & State

### Undo History Entry Format

Each entry in `_mouse_undo_history` is a dictionary with one of two shapes:

**Collection undo entry** (for actions that modify the Anki collection):
```python
{
    "kind": "collection",
    "action": "good",           # The action string
    "step": 42,                 # Anki undo step number
    "at": datetime.datetime,    # When the action was executed
    "undo_text": "Answer Card"  # Optional: Anki's undo description
}
```

**Local undo entry** (for actions that don't modify the collection):
```python
{
    "kind": "local",
    "action": "show_ans",       # The action string
    "prev_state": "review",     # Anki state before the action
    "prev_enabled": True,       # Whether hotmouse was enabled
    "at": datetime.datetime,    # When the action was executed
    "card_id": 123456           # Optional: card ID (for show_ans)
}
```

### Undo History Pruning

- Entries older than 30 minutes are removed
- Entries with step numbers greater than the current step (orphaned by external undo) are removed
- Maximum 300 entries retained

---

## Event Hooks & Integration

### Startup Sequence

1. Anki loads `addon/__init__.py`
2. `config` module initializes `ConfigManager` and registers config tabs
3. `event` module reads config, creates `HotmouseManager` and `HotmouseEventFilter`
4. `compat()` runs (no-op for fresh installs)
5. `main_window_did_init` fires:
   - Menu item added to Tools menu
   - Event filter installed on `mw.web` and `mw.bottomWeb`
   - Context menu handler wrapped on `AnkiWebView`
   - Support tab update check runs
   - Log clearing runs (after 500ms delay)

### Wheel Event Flow

1. **JS path** (primary for webview content):
   - `detect_wheel.js` captures `wheel` event
   - Applies axis locking, smart scroll, edge padding checks
   - Sends `pycmd("ReviewHotmouse#...")` to Python
   - `handle_js_message()` receives and processes the message
   - Calls `manager.handle_scroll()` with normalized direction and delta

2. **Native Qt path** (fallback for events not caught by JS):
   - `HotmouseEventFilter.eventFilter()` catches `QEvent.Type.Wheel`
   - `_should_handle_native_wheel()` validates the event
   - Calls `manager.on_mouse_scroll()` then `manager.handle_scroll()`

Both paths use the same accumulation and threshold logic in `handle_scroll()`.

### Click Event Flow

1. `HotmouseEventFilter.eventFilter()` catches `QEvent.Type.MouseButtonPress`
2. Calls `manager.on_mouse_press(event)`
3. Manager builds hotkey string and calls `execute_shortcut()`
4. For right-clicks, context menu is also handled via `QEvent.Type.ContextMenu`

---

## Third-Party Addon Compatibility

### Edit Field During Review (Cloze)

The addon detects messages from the "Edit Field During Review (Cloze)" addon:
- `EFDRC!focuson#*`: Suspends hotmouse with reason `"efdr_edit"`
- `EFDRC!reload`: Resumes hotmouse by removing the `"efdr_edit"` suspension

This prevents accidental hotkey triggers while editing card fields inline.

### Suspend/Resume System

Any addon can integrate with the hotmouse suspend system by calling:
```python
manager.suspend("my_reason")  # Temporarily disable hotmouse
manager.resume("my_reason")   # Re-enable hotmouse
```

Multiple suspend reasons can be active simultaneously. Hotmouse only re-enables when all reasons are cleared.
