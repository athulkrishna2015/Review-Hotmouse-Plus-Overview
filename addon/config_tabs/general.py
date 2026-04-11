from aqt.qt import *

from ..ankiaddonconfig import ConfigWindow


def general_tab(conf_window: ConfigWindow) -> None:
    tab = conf_window.add_tab("General")

    tab.number_input(
        "threshold_wheel_ms",
        "Mouse scroll threshold (1000 is 1s)",
        tooltip="How long a delay between subsequent scroll actions?",
        maximum=3000,
    )

    tab.number_input(
        "threshold_click_ms",
        "Mouse click threshold (1000 is 1s)",
        tooltip="How long a delay between subsequent click actions? Set to 0 for no delay (instant response).",
        maximum=3000,
        minimum=0,
    )

    tab.number_input(
        "scroll_accumulation_threshold",
        "Wheel/Trackpad distance threshold",
        tooltip=(
            "How much 'scroll distance' (accumulation) is needed to trigger a hotkey. "
            "Lower values make trackpad swipes trigger sooner. 60 is the default; "
            "120 matches the older wheel sensitivity."
        ),
        minimum=1,
        maximum=1200,
    )

    tab.checkbox(
        "default_enabled",
        "add-on is enabled at start",
        "If you uncheck this box, the add-on will start as turned off when Anki is launched",
    )

    tab.checkbox(
        "wheel_ignore_scrollbar",
        "Ignore wheel on side scroll bar",
        "Allow normal scrolling when the mouse is over the side scroll bar area.",
    )

    tab.checkbox(
        "wheel_only_on_bottom_bar",
        "Wheel hotkeys only on bottom bar",
        "Only trigger wheel actions when the mouse is over the bottom rating bar.",
    )

    tab.checkbox(
        "smart_scroll",
        "Smart scroll for long cards",
        "Let the mouse wheel scroll long cards normally. Hotkeys only trigger when you've reached the top or bottom of the page.",
    )

    tab.checkbox(
        "natural_scrolling",
        "Natural scrolling (invert horizontal swipe)",
        "Enable if your trackpad uses natural (reverse) scrolling. "
        "Flips the left/right swipe direction so it matches your finger movement.",
    )

    global_undo_cb = tab.checkbox(
        "right_click_global_undo",
        "Right-click undo can use global undo",
        "If enabled, right-click undo falls back to Anki global undo for any action.",
    )

    undo_confirm_cb = tab.checkbox(
        "right_click_undo_confirmation",
        "Right-click again for global undo",
        "When mouse undo is unavailable, a second right-click can trigger global undo within 6 seconds.",
    )

    def on_global_undo_changed(state: int) -> None:
        if state:
            undo_confirm_cb.setChecked(False)
            conf_window.conf.set("right_click_undo_confirmation", False)

    def on_undo_confirm_changed(state: int) -> None:
        if state:
            global_undo_cb.setChecked(False)
            conf_window.conf.set("right_click_global_undo", False)

    global_undo_cb.stateChanged.connect(on_global_undo_changed)
    undo_confirm_cb.stateChanged.connect(on_undo_confirm_changed)

    tab.hseparator()

    tab.checkbox(
        "middle_click_scroll",
        "Middle-click drag to scroll",
        "Hold the middle mouse button (scroll wheel) and move up/down to scroll the page.",
    )
    tab.number_input(
        "middle_click_dead_zone",
        "Dead zone (pixels)",
        tooltip="Minimum distance from click origin before scrolling starts.",
        minimum=0,
        maximum=100,
    )
    tab.number_input(
        "middle_click_sensitivity",
        "Scroll sensitivity (1–20)",
        tooltip="How fast the page scrolls relative to mouse distance. Higher = faster.",
        minimum=1,
        maximum=20,
    )

    tab.hseparator()

    tab.checkbox("tooltip", "When triggered, show action name")
    tab.checkbox("z_debug", "Debugging: Show hotkey on mouse action")
    tab.stretch()
