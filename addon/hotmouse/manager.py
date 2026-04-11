from typing import Any, Callable, Dict, List, Optional, Set, Tuple, no_type_check
import datetime
import json
from pathlib import Path

from aqt import mw
from aqt.qt import *
from aqt.utils import tooltip

from .actions import (
    ACTIONS,
    Button,
    WheelDir,
    _HOTMOUSE_UNDO_TRACK_SKIP_ACTIONS,
    _NON_COLLECTION_HOTMOUSE_UNDO_ACTIONS,
    toggle_on_off,
)

config: Dict[str, Any] = {}


def set_config(new_config: Dict[str, Any]) -> None:
    global config
    config = new_config


class HotmouseManager:
    has_wheel_hotkey: bool

    def __init__(self) -> None:
        self.enabled = config.get("default_enabled", True)
        self.last_scroll_time = datetime.datetime.now()
        self.last_click_time = datetime.datetime.now()
        self._suspend_reasons: Set[str] = set()
        self._suspend_prev_enabled: bool = False
        self._track_hotmouse_undo_next: bool = False
        self._track_hotmouse_action: Optional[str] = None
        self._track_hotmouse_undo_set_at: Optional[datetime.datetime] = None
        self._track_hotmouse_undo_prev_step: Optional[int] = None
        self._track_hotmouse_undo_token: int = 0
        self._last_hotmouse_action: Optional[str] = None
        self._last_hotmouse_action_at: Optional[datetime.datetime] = None
        self._last_hotmouse_prev_state: Optional[str] = None
        self._last_hotmouse_prev_enabled: Optional[bool] = None
        self._mouse_session_actions: Set[str] = set()
        self._mouse_undo_history: List[Dict[str, Any]] = []
        self._mouse_undo_chain_until: Optional[datetime.datetime] = None
        self._global_undo_armed_until: Optional[datetime.datetime] = None
        self._wheel_accumulator: float = 0.0
        self._last_wheel_dir: Optional[WheelDir] = None
        self._wheel_action_latched: bool = False
        self._wheel_action_dir: Optional[WheelDir] = None
        self._mid_drag_active: bool = False
        self._mid_drag_origin_y: int = 0
        self._mid_drag_scroll_timer: Optional[QTimer] = None
        self._mid_drag_speed: float = 0.0
        self.refresh_shortcuts()

    def add_menu(self, conf_open: Callable[[], None]) -> None:
        self.conf_action = QAction("Review Hotmouse Config", mw)
        self.conf_action.triggered.connect(conf_open)
        mw.form.menuTools.addAction(self.conf_action)

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def suspend(self, reason: str) -> None:
        if reason in self._suspend_reasons:
            return
        if not self._suspend_reasons:
            self._suspend_prev_enabled = self.enabled
            if self.enabled:
                self.disable()
        self._suspend_reasons.add(reason)

    def resume(self, reason: str) -> None:
        if reason not in self._suspend_reasons:
            return
        self._suspend_reasons.remove(reason)
        if not self._suspend_reasons:
            if self._suspend_prev_enabled:
                self.enable()
            self._suspend_prev_enabled = False

    def refresh_shortcuts(self) -> None:
        self.has_wheel_hotkey = any(
            "wheel" in s for s in config.get("shortcuts", {}).keys()
        )

    @staticmethod
    def _current_undo_step() -> int:
        col = getattr(mw, "col", None)
        if not col:
            return 0
        try:
            status = col.undo_status()
            return int(getattr(status, "last_step", 0))
        except Exception:
            return 0

    def _expire_hotmouse_undo_tracking(self, token: int) -> None:
        if token != self._track_hotmouse_undo_token:
            return
        if not self._track_hotmouse_undo_next:
            return
        self._track_hotmouse_undo_next = False
        self._track_hotmouse_action = None
        self._track_hotmouse_undo_set_at = None
        self._track_hotmouse_undo_prev_step = None

    def _capture_pending_hotmouse_undo(self, token: int) -> None:
        if token != self._track_hotmouse_undo_token:
            return
        if not self._track_hotmouse_undo_next:
            return

        previous_step = self._track_hotmouse_undo_prev_step
        if previous_step is None:
            return

        info = mw.undo_actions_info()
        can_undo = bool(getattr(info, "can_undo", False))
        undo_text = getattr(info, "undo_text", None)
        current_step = self._current_undo_step()
        if (
            can_undo
            and isinstance(undo_text, str)
            and (
                current_step != previous_step
                or (
                    self._track_hotmouse_action is not None
                    and self._track_hotmouse_action
                    not in _NON_COLLECTION_HOTMOUSE_UNDO_ACTIONS
                )
            )
        ):
            tracked_action = self._track_hotmouse_action
            self._track_hotmouse_undo_next = False
            self._track_hotmouse_action = None
            self._track_hotmouse_undo_set_at = None
            self._track_hotmouse_undo_prev_step = None
            if tracked_action and tracked_action not in _NON_COLLECTION_HOTMOUSE_UNDO_ACTIONS:
                self._append_collection_history_entry(
                    tracked_action, current_step, undo_text
                )

    def _global_undo_available(self) -> bool:
        return bool(getattr(mw, "form", None) and mw.form.actionUndo.isEnabled())

    def _append_collection_history_entry(
        self, action: str, step: int, undo_text: Optional[str]
    ) -> None:
        entry: Dict[str, Any] = {
            "kind": "collection",
            "action": action,
            "step": step,
            "at": datetime.datetime.now(),
        }
        if isinstance(undo_text, str) and undo_text:
            entry["undo_text"] = undo_text
        self._mouse_undo_history.append(entry)

    def _append_local_history_entry(
        self,
        action: str,
        prev_state: Optional[str],
        prev_enabled: Optional[bool],
        card_id: Optional[int] = None,
    ) -> None:
        entry: Dict[str, Any] = {
            "kind": "local",
            "action": action,
            "prev_state": prev_state,
            "prev_enabled": prev_enabled,
            "at": datetime.datetime.now(),
        }
        if card_id is not None:
            entry["card_id"] = card_id
        self._mouse_undo_history.append(entry)

    def _prune_mouse_undo_history(self, current_step: int) -> None:
        cutoff = datetime.datetime.now() - datetime.timedelta(minutes=30)
        self._mouse_undo_history = [
            entry
            for entry in self._mouse_undo_history
            if not (
                (
                    entry.get("kind") == "collection"
                    and isinstance(entry.get("step"), int)
                    and int(entry.get("step")) > current_step
                )
                or (
                    isinstance(entry.get("at"), datetime.datetime)
                    and entry.get("at") < cutoff
                )
            )
        ]
        if len(self._mouse_undo_history) > 300:
            self._mouse_undo_history = self._mouse_undo_history[-300:]

    def _undo_local_history_entry(self, entry: Dict[str, Any]) -> str:
        action = entry.get("action")
        prev_state = entry.get("prev_state")
        prev_enabled = entry.get("prev_enabled")

        if action in ("on", "off", "on_off"):
            if prev_enabled is None:
                return "stale"
            if prev_enabled:
                self.enable()
            else:
                self.disable()
            return "done"

        if action == "show_ans":
            if mw.state != "review" or getattr(mw.reviewer, "state", None) != "answer":
                return "stale"
            current_card = getattr(getattr(mw, "reviewer", None), "card", None)
            current_card_id = getattr(current_card, "id", None)
            tracked_card_id = entry.get("card_id")
            if tracked_card_id is not None and current_card_id != tracked_card_id:
                return "stale"
            try:
                mw.reviewer._showQuestion()
                return "done"
            except Exception:
                return "blocked"

        if action == "study_now":
            if mw.state == "review" and hasattr(mw, "moveToState"):
                try:
                    mw.moveToState("overview")
                    return "done"
                except Exception:
                    return "blocked"
            return "stale"

        if action == "return_to_deck_browser":
            if not hasattr(mw, "moveToState"):
                return "stale"
            if mw.state != "overview":
                return "stale"
            try:
                mw.moveToState("deckBrowser")
                return "done"
            except Exception:
                return "blocked"

        if action == "deck_browser":
            if not (prev_state and hasattr(mw, "moveToState")):
                return "stale"
            if mw.state != "deckBrowser":
                return "stale"
            try:
                mw.moveToState(prev_state)
                return "done"
            except Exception:
                return "blocked"

        if action in ("audio", "replay_voice", "record_voice"):
            try:
                from aqt.sound import av_player

                av_player.clear_queue_and_maybe_interrupt()
                return "done"
            except Exception:
                return "blocked"

        return "stale"

    def _undo_from_mouse_history(self, info: Any, current_step: int) -> bool:
        can_undo = bool(getattr(info, "can_undo", False))
        undo_text = getattr(info, "undo_text", None)

        while self._mouse_undo_history:
            entry = self._mouse_undo_history[-1]
            kind = entry.get("kind")

            if kind == "collection":
                entry_step = entry.get("step")
                if isinstance(entry_step, int) and current_step < entry_step:
                    self._mouse_undo_history.pop()
                    continue
                if not can_undo:
                    return False
                if isinstance(entry_step, int) and current_step != entry_step:
                    return False

                expected_text = entry.get("undo_text")
                if (
                    isinstance(expected_text, str)
                    and expected_text
                    and isinstance(undo_text, str)
                    and undo_text != expected_text
                ):
                    self._mouse_undo_history.pop()
                    continue

                self._mouse_undo_history.pop()
                self._clear_global_undo_arm()
                self._arm_mouse_undo_chain()
                mw.undo()
                return True

            if kind == "local":
                state = self._undo_local_history_entry(entry)
                if state == "done":
                    self._mouse_undo_history.pop()
                    self._clear_global_undo_arm()
                    self._arm_mouse_undo_chain()
                    return True
                if state == "stale":
                    self._mouse_undo_history.pop()
                    continue
                return False

            self._mouse_undo_history.pop()

        return False

    def _mouse_undo_unavailable_reason(self) -> str:
        info = mw.undo_actions_info()
        can_undo = bool(getattr(info, "can_undo", False))
        if not can_undo:
            return "no undo entry available"

        undo_text = getattr(info, "undo_text", "")
        if isinstance(undo_text, str) and undo_text.strip():
            return undo_text.strip()
        return "undo entry is not from this add-on"

    def _arm_mouse_undo_chain(self) -> None:
        self._mouse_undo_chain_until = datetime.datetime.now() + datetime.timedelta(
            seconds=10
        )

    def _clear_mouse_undo_chain(self) -> None:
        self._mouse_undo_chain_until = None

    def _is_mouse_undo_chain_active(self) -> bool:
        if self._mouse_undo_chain_until is None:
            return False
        if datetime.datetime.now() > self._mouse_undo_chain_until:
            self._mouse_undo_chain_until = None
            return False
        return True

    def _clear_global_undo_arm(self) -> None:
        self._global_undo_armed_until = None

    def _is_global_undo_armed(self) -> bool:
        if self._global_undo_armed_until is None:
            return False
        if datetime.datetime.now() > self._global_undo_armed_until:
            self._global_undo_armed_until = None
            return False
        return True

    def _is_action_allowed_globally(self, undo_text: str) -> bool:
        if not undo_text:
            return False

        target = undo_text.strip().lower()
        if any(kw in target for kw in ("answer", "review", "rating", "card", "score")):
            return True

        whitelist = config.get("undo_whitelist", [])
        if not isinstance(whitelist, list):
            whitelist = []

        def is_in_list(target_str: str, items: List[Any]) -> bool:
            for item in items:
                if not isinstance(item, str):
                    continue
                normalized_item = item.strip().lower()
                if (
                    normalized_item == target_str
                    or normalized_item in target_str
                    or target_str in normalized_item
                ):
                    return True
            return False

        if is_in_list(target, whitelist):
            return True

        try:
            addon_path = Path(__file__).parent.parent
            meta_path = addon_path / "meta.json"
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    for container in (meta, meta.get("config", {})):
                        if not isinstance(container, dict):
                            continue
                        for key in (
                            "undo_whitelist",
                            "allowed_undo_actions",
                            "undo_actions",
                        ):
                            val = container.get(key)
                            if isinstance(val, list) and is_in_list(target, val):
                                return True
        except Exception:
            pass

        return False

    def mark_next_undo_as_hotmouse(self, action_str: str) -> None:
        if action_str in _HOTMOUSE_UNDO_TRACK_SKIP_ACTIONS:
            return
        if self._track_hotmouse_undo_next:
            current_token = self._track_hotmouse_undo_token
            self._capture_pending_hotmouse_undo(current_token)
            if self._track_hotmouse_undo_next:
                self._track_hotmouse_undo_next = False
                self._track_hotmouse_action = None
                self._track_hotmouse_undo_set_at = None
                self._track_hotmouse_undo_prev_step = None

        self._track_hotmouse_undo_next = True
        self._track_hotmouse_action = action_str
        self._track_hotmouse_undo_set_at = datetime.datetime.now()
        self._track_hotmouse_undo_prev_step = self._current_undo_step()
        self._track_hotmouse_undo_token += 1
        token = self._track_hotmouse_undo_token
        for delay_ms in (80, 220, 600):
            QTimer.singleShot(
                delay_ms, lambda t=token: self._capture_pending_hotmouse_undo(t)
            )
        QTimer.singleShot(2500, lambda t=token: self._expire_hotmouse_undo_tracking(t))

    def remember_last_hotmouse_action(
        self, action_str: str, prev_state: Optional[str], prev_enabled: bool
    ) -> None:
        if action_str in _HOTMOUSE_UNDO_TRACK_SKIP_ACTIONS:
            return
        self._last_hotmouse_action = action_str
        self._last_hotmouse_action_at = datetime.datetime.now()
        self._last_hotmouse_prev_state = prev_state
        self._last_hotmouse_prev_enabled = prev_enabled
        self._mouse_session_actions.add(action_str)
        if action_str in _NON_COLLECTION_HOTMOUSE_UNDO_ACTIONS:
            if action_str == "study_now" and prev_state == "overview":
                self._append_local_history_entry(
                    "return_to_deck_browser", prev_state, prev_enabled
                )
            card_id: Optional[int] = None
            if action_str == "show_ans":
                card = getattr(getattr(mw, "reviewer", None), "card", None)
                card_id = getattr(card, "id", None)
            self._append_local_history_entry(
                action_str, prev_state, prev_enabled, card_id
            )

    def on_undo_state_did_change(self, info: Any) -> None:
        undo_text = getattr(info, "undo_text", None)
        can_undo = bool(getattr(info, "can_undo", False))
        current_step = self._current_undo_step()
        self._prune_mouse_undo_history(current_step)

        if self._track_hotmouse_undo_next:
            tracked_action = self._track_hotmouse_action
            self._track_hotmouse_undo_next = False
            self._track_hotmouse_action = None
            previous_step = self._track_hotmouse_undo_prev_step
            self._track_hotmouse_undo_prev_step = None

            age_ok = True
            if self._track_hotmouse_undo_set_at is not None:
                age = datetime.datetime.now() - self._track_hotmouse_undo_set_at
                age_ok = age.total_seconds() <= 2.5
            self._track_hotmouse_undo_set_at = None
            if (
                age_ok
                and can_undo
                and isinstance(undo_text, str)
                and previous_step is not None
                and (
                    current_step != previous_step
                    or (
                        tracked_action is not None
                        and tracked_action not in _NON_COLLECTION_HOTMOUSE_UNDO_ACTIONS
                    )
                )
            ):
                if tracked_action and tracked_action not in _NON_COLLECTION_HOTMOUSE_UNDO_ACTIONS:
                    self._append_collection_history_entry(
                        tracked_action, current_step, undo_text
                    )
            return

    def undo_last_hotmouse_action(self) -> None:
        self._capture_pending_hotmouse_undo(self._track_hotmouse_undo_token)
        info = mw.undo_actions_info()
        can_undo = bool(getattr(info, "can_undo", False))
        current_step = self._current_undo_step()
        self._prune_mouse_undo_history(current_step)

        if (
            self._track_hotmouse_undo_next
            and self._last_hotmouse_action in self._mouse_session_actions
            and self._track_hotmouse_action == self._last_hotmouse_action
            and mw.state == "review"
            and getattr(mw.reviewer, "state", None) == "question"
        ):
            previous_step = self._track_hotmouse_undo_prev_step
            last_action = self._last_hotmouse_action
            can_capture_now = (
                can_undo
                and previous_step is not None
                and (
                    current_step != previous_step
                    or (
                        last_action is not None
                        and last_action not in _NON_COLLECTION_HOTMOUSE_UNDO_ACTIONS
                    )
                )
            )
            if can_capture_now:
                self._track_hotmouse_undo_next = False
                self._track_hotmouse_action = None
                self._track_hotmouse_undo_set_at = None
                self._track_hotmouse_undo_prev_step = None
                if last_action and last_action not in _NON_COLLECTION_HOTMOUSE_UNDO_ACTIONS:
                    undo_text = getattr(info, "undo_text", None)
                    self._append_collection_history_entry(
                        last_action, current_step, undo_text
                    )

        if self._undo_from_mouse_history(info, current_step):
            return

        if config.get("right_click_global_undo", False):
            if self._global_undo_available():
                self._clear_mouse_undo_chain()
                mw.onUndo()
                return
            else:
                tooltip("No global undo entry available.")
                return

        reason = self._mouse_undo_unavailable_reason()
        undo_text = getattr(info, "undo_text", "")
        if self._is_action_allowed_globally(undo_text):
            if self._global_undo_available():
                self._clear_mouse_undo_chain()
                mw.onUndo()
                return

        if (
            self._is_mouse_undo_chain_active()
            and mw.state == "review"
            and getattr(mw.reviewer, "state", None) == "question"
            and hasattr(mw, "moveToState")
        ):
            lowered = reason.lower()
            if "set deck" in lowered or reason == "no undo entry available":
                try:
                    mw.moveToState("overview")
                    self._clear_mouse_undo_chain()
                    return
                except Exception:
                    pass

        if config.get("right_click_undo_confirmation", False) and self._global_undo_available():
            if self._is_global_undo_armed():
                self._clear_global_undo_arm()
                self._clear_mouse_undo_chain()
                mw.onUndo()
                return
            else:
                self._global_undo_armed_until = datetime.datetime.now() + datetime.timedelta(
                    seconds=6
                )
                tooltip(
                    "Mouse undo unavailable ({}).<br><b>Right-click again</b> for "
                    "global undo or use <b>Ctrl+Z</b>.".format(reason)
                )
                return

        tooltip(
            "Mouse undo unavailable ({}).<br>Use <b>Ctrl+Z</b> for global undo or "
            "enable it in addon settings.".format(reason)
        )
        self._clear_mouse_undo_chain()
        return

    def right_click_bound_in_current_scope(self) -> bool:
        if not self.enabled:
            return False
        if mw.state == "overview":
            return self.uses_btn_in_scope("o", Button.right)
        if mw.state != "review":
            return False
        rstate = getattr(mw.reviewer, "state", None)
        if rstate == "question":
            return self.uses_btn_in_scope("q", Button.right)
        if rstate == "answer":
            return self.uses_btn_in_scope("a", Button.right)
        return self.uses_btn_in_scope("c", Button.right)

    def uses_btn(self, btn: Button) -> bool:
        return any(btn.name in s for s in config.get("shortcuts", {}).keys())

    def uses_btn_in_scope(self, scope: str, btn: Button) -> bool:
        return any(
            k.startswith(f"{scope}_") and btn.name in k
            for k in config.get("shortcuts", {}).keys()
        )

    @staticmethod
    def get_pressed_buttons(qbuttons: "Qt.MouseButton") -> List[Button]:
        buttons: List[Button] = []
        for b in Button:
            if qbuttons & b.value:  # type: ignore
                buttons.append(b)
        return buttons

    @staticmethod
    def build_hotkey(
        btns: List[Button],
        wheel: Optional[WheelDir] = None,
        click: Optional[Button] = None,
    ) -> str:
        if mw.state == "overview":
            scope = "o"
        elif mw.state == "review":
            if mw.reviewer.state == "question":
                scope = "q"
            elif mw.reviewer.state == "answer":
                scope = "a"
            else:
                scope = "c"
        else:
            scope = "x"

        parts: List[str] = [scope]
        for btn in btns:
            parts.append(f"press_{btn.name}")
        if click:
            parts.append(f"click_{click.name}")
        if wheel == WheelDir.UP:
            parts.append("wheel_up")
        elif wheel == WheelDir.DOWN:
            parts.append("wheel_down")
        elif wheel == WheelDir.LEFT:
            parts.append("wheel_left")
        elif wheel == WheelDir.RIGHT:
            parts.append("wheel_right")
        return "_".join(parts)

    def execute_shortcut(self, hotkey_str: str) -> bool:
        if self.enabled and config.get("z_debug", False):
            tooltip(hotkey_str)

        action_str = config.get("shortcuts", {}).get(hotkey_str, "")
        if action_str == "undo" and hotkey_str in ("q_click_right", "a_click_right"):
            action_str = "undo_hotmouse"

        if not self.enabled and action_str not in ("on", "on_off"):
            return False

        if not action_str:
            return False

        if config.get("tooltip", False):
            tooltip(action_str)

        if action_str != "undo_hotmouse":
            self._clear_global_undo_arm()
            self._clear_mouse_undo_chain()

        prev_state = getattr(mw, "state", None)
        prev_enabled = self.enabled
        self.mark_next_undo_as_hotmouse(action_str)
        ACTIONS[action_str]()
        self.remember_last_hotmouse_action(action_str, prev_state, prev_enabled)

        return True

    def on_mouse_press(self, event: QMouseEvent) -> bool:
        curr_time = datetime.datetime.now()
        time_diff = curr_time - self.last_click_time
        click_threshold_ms = config.get("threshold_click_ms", 0)

        if click_threshold_ms > 0 and time_diff.total_seconds() * 1000 < click_threshold_ms:
            return self.enabled

        self.last_click_time = curr_time

        btns = self.get_pressed_buttons(event.buttons())
        btn = event.button()
        try:
            pressed = Button(event.button())
            if pressed in btns:
                btns.remove(pressed)
        except ValueError:
            print(f"Review Hotmouse: Unknown Button Pressed: {btn}")
            return False

        hotkey_str = self.build_hotkey(btns, click=pressed)
        return self.execute_shortcut(hotkey_str)

    def on_mouse_scroll(self, event: QWheelEvent) -> bool:
        invert_x = config.get("natural_scrolling", True)
        wheel_dir, delta = WheelDir.from_qt(event.angleDelta(), invert_x=invert_x)
        if wheel_dir is None:
            return False
        return self.handle_scroll(wheel_dir, delta, event.buttons())

    def handle_scroll(
        self, wheel_dir: WheelDir, delta: float, qbtns: "Qt.MouseButton"
    ) -> bool:
        curr_time = datetime.datetime.now()
        time_diff = (curr_time - self.last_scroll_time).total_seconds() * 1000

        if self._wheel_action_latched:
            if wheel_dir != self._wheel_action_dir or time_diff > 500:
                self._wheel_action_latched = False
                self._wheel_action_dir = None
                self._wheel_accumulator = 0
            else:
                return self.enabled

        # Axis-aware accumulator: only reset when the direction changes or
        # the gesture times out.  Trackpad swipes produce many small events
        # that may oscillate between LEFT/DOWN due to imprecise fingers; by
        # comparing at the axis level we avoid spurious resets.
        if self._last_wheel_dir is None or time_diff > 500:
            self._wheel_accumulator = 0
        elif wheel_dir != self._last_wheel_dir:
            # Only preserve the accumulator if the axis stayed the same
            # (e.g. LEFT→LEFT is fine; LEFT→RIGHT is a reversal → reset)
            same_axis = (
                self._last_wheel_dir in (WheelDir.LEFT, WheelDir.RIGHT)
                and wheel_dir in (WheelDir.LEFT, WheelDir.RIGHT)
            ) or (
                self._last_wheel_dir in (WheelDir.UP, WheelDir.DOWN)
                and wheel_dir in (WheelDir.UP, WheelDir.DOWN)
            )
            if not same_axis:
                self._wheel_accumulator = 0

        self._last_wheel_dir = wheel_dir
        self._wheel_accumulator += abs(float(delta))

        threshold = config.get("scroll_accumulation_threshold", 60)

        if self._wheel_accumulator >= threshold:
            if time_diff > config.get("threshold_wheel_ms", 0):
                self._wheel_accumulator = 0
                self.last_scroll_time = curr_time
                btns = self.get_pressed_buttons(qbtns)
                hotkey_str = self.build_hotkey(btns, wheel=wheel_dir)
                executed = self.execute_shortcut(hotkey_str)
                if executed:
                    self._wheel_action_latched = True
                    self._wheel_action_dir = wheel_dir
                return executed
            else:
                self._wheel_accumulator = threshold
                return self.enabled
        else:
            return self.enabled

    def start_mid_drag(self, y: int) -> None:
        self._mid_drag_active = True
        self._mid_drag_origin_y = y
        self._mid_drag_speed = 0.0
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.SizeAllCursor))
        if self._mid_drag_scroll_timer is None:
            self._mid_drag_scroll_timer = QTimer()
            self._mid_drag_scroll_timer.timeout.connect(self._mid_drag_tick)
        self._mid_drag_scroll_timer.start(16)

    def stop_mid_drag(self) -> None:
        self._mid_drag_active = False
        self._mid_drag_speed = 0.0
        QApplication.restoreOverrideCursor()
        if self._mid_drag_scroll_timer is not None:
            self._mid_drag_scroll_timer.stop()

    def update_mid_drag(self, y: int) -> None:
        delta = y - self._mid_drag_origin_y
        dead_zone = config.get("middle_click_dead_zone", 15)
        if abs(delta) < dead_zone:
            self._mid_drag_speed = 0.0
        else:
            sensitivity = config.get("middle_click_sensitivity", 5) / 10.0
            self._mid_drag_speed = (delta - (dead_zone if delta > 0 else -dead_zone)) * sensitivity

    def _mid_drag_tick(self) -> None:
        if not (QApplication.mouseButtons() & Qt.MouseButton.MiddleButton):
            self.stop_mid_drag()
            return
        if not self._mid_drag_active or self._mid_drag_speed == 0.0:
            return
        px = int(self._mid_drag_speed)
        if px == 0:
            return
        try:
            mw.web.eval(f"window.scrollBy(0, {px});")
        except Exception:
            pass


def _get_object_width(obj: QObject) -> int:
    if hasattr(obj, "width") and isinstance(obj.width, (int, float)):
        return int(obj.width)
    if hasattr(obj, "width") and callable(obj.width):
        try:
            return int(obj.width())
        except Exception:
            return 0
    if hasattr(obj, "geometry"):
        try:
            return int(obj.geometry().width())
        except Exception:
            return 0
    return 0


def _event_x(event: QWheelEvent) -> float:
    try:
        return float(event.position().x())
    except AttributeError:
        return float(event.pos().x())


def _is_bottom_web_target(obj: QObject) -> bool:
    curr = obj
    while curr:
        if curr == mw.bottomWeb:
            return True
        try:
            curr = curr.parent()
        except AttributeError:
            break
    return False


def _should_handle_native_wheel(obj: QObject, event: QWheelEvent) -> bool:
    if getattr(mw, "state", None) not in ("review", "overview"):
        return False
    if config.get("smart_scroll", False) and getattr(mw, "state", None) != "overview":
        return False

    if config.get("wheel_ignore_scrollbar", True):
        width = _get_object_width(obj)
        if width > 0 and _event_x(event) > width - 30:
            return False

    if (
        getattr(mw, "state", None) == "review"
        and config.get("wheel_only_on_bottom_bar", False)
        and not _is_bottom_web_target(obj)
    ):
        return False

    return True


class HotmouseEventFilter(QObject):
    @no_type_check
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if config.get("middle_click_scroll", True):
            if event.type() == QEvent.Type.MouseButtonPress:
                if (
                    isinstance(event, QMouseEvent)
                    and event.button() == Qt.MouseButton.MiddleButton
                    and not self.manager._mid_drag_active
                ):
                    try:
                        y = int(event.position().y())
                    except AttributeError:
                        y = event.pos().y()
                    self.manager.start_mid_drag(y)
                    return True

            if event.type() == QEvent.Type.MouseButtonRelease:
                if (
                    isinstance(event, QMouseEvent)
                    and event.button() == Qt.MouseButton.MiddleButton
                    and self.manager._mid_drag_active
                ):
                    self.manager.stop_mid_drag()
                    return True

            if event.type() == QEvent.Type.MouseMove:
                if isinstance(event, QMouseEvent) and self.manager._mid_drag_active:
                    try:
                        y = int(event.position().y())
                    except AttributeError:
                        y = event.pos().y()
                    self.manager.update_mid_drag(y)
                    return True

        if event.type() == QEvent.Type.MouseButtonDblClick:
            if isinstance(event, QMouseEvent) and event.button() == Qt.MouseButton.MiddleButton:
                toggle_on_off()
                return True

        if event.type() == QEvent.Type.MouseButtonPress:
            if isinstance(event, QMouseEvent) and self.manager.on_mouse_press(event):
                return True

        if event.type() == QEvent.Type.ContextMenu:
            if self.manager.right_click_bound_in_current_scope():
                return True

        if (
            event.type() == QEvent.Type.Wheel
            and isinstance(event, QWheelEvent)
            and self.manager.has_wheel_hotkey
            and _should_handle_native_wheel(obj, event)
        ):
            if self.manager.on_mouse_scroll(event):
                return True

        if event.type() == QEvent.Type.ChildAdded:
            add_event_filter(event.child())

        return False

    def __init__(self, manager: HotmouseManager) -> None:
        super().__init__()
        self.manager = manager


def add_event_filter(object: QObject) -> None:
    object.installEventFilter(hotmouseEventFilter)
    for w in object.children():
        add_event_filter(w)


hotmouseEventFilter: HotmouseEventFilter
