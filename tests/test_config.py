def test_sort_hotkey_btn() -> None:
    from addon.config import HotkeyTabManager

    h0 = "q_click_right"
    a0 = h0
    assert HotkeyTabManager.sort_hotkey_btn(h0) == a0
    h1 = "q_press_right_press_left_click_middle"
    a1 = "q_press_left_press_right_click_middle"
    assert HotkeyTabManager.sort_hotkey_btn(h1) == a1
    h2 = "a_press_xbutton1_press_right_press_left_wheel_up"
    a2 = "a_press_left_press_right_press_xbutton1_wheel_up"
    assert HotkeyTabManager.sort_hotkey_btn(h2) == a2
    h3 = "q_press_right_click_left"
    a3 = h3
    assert HotkeyTabManager.sort_hotkey_btn(h3) == a3


def test_trackpad_action_helpers() -> None:
    from addon.config import apply_trackpad_actions, get_trackpad_action

    shortcuts = {
        "q_click_right": "undo_hotmouse",
        "a_wheel_left": "hard",
        "a_press_middle_wheel_right": "easy",
    }

    assert get_trackpad_action(shortcuts, "a", "left") == "hard"
    assert get_trackpad_action(shortcuts, "o", "down") == "<none>"

    updated = apply_trackpad_actions(
        shortcuts,
        {
            ("a", "left"): "again",
            ("o", "down"): "study_now",
            ("c", "right"): "<none>",
        },
    )

    assert updated["q_click_right"] == "undo_hotmouse"
    assert updated["a_press_middle_wheel_right"] == "easy"
    assert updated["a_wheel_left"] == "again"
    assert updated["o_wheel_down"] == "study_now"
    assert "c_wheel_right" not in updated


def test_default_scroll_settings() -> None:
    from aqt import mw

    defaults = mw.addonManager.addonConfigDefaults("addon")
    assert defaults["smart_scroll"] is False
    assert defaults["scroll_accumulation_threshold"] == 60
