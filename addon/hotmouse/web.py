from typing import Any, Dict, List, Optional, Tuple
import json

from aqt import mw
from aqt.qt import QContextMenuEvent, QWebEngineView
from aqt.webview import AnkiWebView, WebContent
import aqt

from .actions import WheelDir, _study_now_from_overview

config: Dict[str, Any] = {}
manager: Any = None


def set_config(new_config: Dict[str, Any]) -> None:
    global config
    config = new_config


def set_manager(new_manager: Any) -> None:
    global manager
    manager = new_manager


def WEBVIEW_TARGETS() -> List[AnkiWebView]:
    return [mw.web, mw.bottomWeb]


def _aqt_context_type(module_name: str, class_name: str) -> Optional[type]:
    module = getattr(aqt, module_name, None)
    cls = getattr(module, class_name, None)
    return cls if isinstance(cls, type) else None


def _is_overview_context(context: Any) -> bool:
    overview_type = _aqt_context_type("overview", "Overview")
    return bool(overview_type and isinstance(context, overview_type))


def _is_reviewer_context(context: Any) -> bool:
    reviewer_type = _aqt_context_type("reviewer", "Reviewer")
    return bool(reviewer_type and isinstance(context, reviewer_type))


def _is_review_state() -> bool:
    return getattr(mw, "state", None) == "review"


def _should_inject_wheel_js(context: Optional[Any]) -> bool:
    if _is_reviewer_context(context) or _is_overview_context(context):
        return True
    # Fallback: only inject if the context's webview is actually the main
    # review/overview webview, NOT the editor or other dialog webviews that
    # happen to load while mw.state is still "review".
    if getattr(mw, "state", None) in ("review", "overview"):
        ctx_web = getattr(context, "web", None)
        if ctx_web is not None and ctx_web in (mw.web, mw.bottomWeb):
            return True
        # If there's no web attribute on the context, be conservative and
        # skip injection to avoid breaking editor/browser scrolling.
    return False


def _normalize_web_delta(delta: float) -> float:
    value = float(delta)
    if abs(value) >= 80:
        return 120.0 if value > 0 else -120.0
    return value


def _boost_boundary_delta(delta: float, at_boundary: bool) -> float:
    if not at_boundary:
        return delta
    if abs(delta) < 80:
        return 120.0 if delta > 0 else -120.0
    return delta


def _has_overview_wheel_mappings() -> bool:
    sc = mw.addonManager.getConfig(__name__).get("shortcuts", {})
    return any(k.startswith("o_wheel_") for k in sc.keys())


def _handle_external_editing_message(message: str, context: Any) -> None:
    if not isinstance(message, str):
        return
    normalized = message.strip()
    if normalized.startswith("EFDRC!focuson#"):
        if _is_reviewer_context(context) or _is_review_state():
            manager.suspend("efdr_edit")
    elif normalized == "EFDRC!reload":
        manager.resume("efdr_edit")


def inject_web_content(web_content: WebContent, context: Optional[Any]) -> None:
    if not _should_inject_wheel_js(context):
        return
    smart_scroll_enabled = config.get("smart_scroll", False)
    if _is_overview_context(context) or getattr(mw, "state", None) == "overview":
        smart_scroll_enabled = False
    enabled = bool(manager and manager.enabled)
    cfg_js = (
        "window._hotmouse_config = {"
        f"wheel_ignore_scrollbar: {str(config.get('wheel_ignore_scrollbar', True)).lower()},"
        f"wheel_only_on_bottom_bar: {str(config.get('wheel_only_on_bottom_bar', False)).lower()},"
        f"smart_scroll: {str(smart_scroll_enabled).lower()},"
        f"natural_scrolling: {str(config.get('natural_scrolling', True)).lower()}"
        "};"
        f"window._hotmouse_enabled = {str(enabled).lower()};"
        f"window._hotmouse_shortcuts = {json.dumps(config.get('shortcuts', {}))};"
    )
    if _is_overview_context(context) or getattr(mw, "state", None) == "overview":
        cfg_js += "window._hotmouse_scope = 'o';"
    else:
        cfg_js += "window._hotmouse_scope = 'r';"
    web_content.head += f"<script>{cfg_js}</script>"
    addon_package = mw.addonManager.addonFromModule(__name__)
    web_content.js.append(f"/_addons/{addon_package}/web/detect_wheel.js")


def handle_js_message(
    handled: Tuple[bool, Any], message: str, context: Any
) -> Tuple[bool, Any]:
    _handle_external_editing_message(message, context)
    addon_key = "ReviewHotmouse#"
    if not message.startswith(addon_key):
        return handled

    try:
        req = json.loads(message[len(addon_key) :])
    except ValueError:
        return handled

    if req.get("key") == "wheel":
        if config.get("wheel_ignore_scrollbar", True) and req.get("is_scrollbar"):
            return (False, None)

        if (
            config.get("wheel_only_on_bottom_bar", False)
            and not req.get("is_bottom")
            and mw.state == "review"
        ):
            return (False, None)

        at_boundary = bool(req.get("at_boundary", False))
        dx_raw = float(req.get("valueX", 0) or 0)
        dy_raw = float(req.get("valueY", req.get("value", 0)) or 0)

        smart_scroll_enabled = config.get("smart_scroll", False)
        if getattr(mw, "state", None) == "overview":
            smart_scroll_enabled = False
        if smart_scroll_enabled and at_boundary:
            dy_raw = _boost_boundary_delta(dy_raw, True)

        dx = _normalize_web_delta(dx_raw)
        dy = _normalize_web_delta(dy_raw)

        invert_x = config.get("natural_scrolling", True)
        wheel_dir, raw_delta = WheelDir.from_web(dx, dy, invert_x=invert_x)
        if wheel_dir is None:
            return (False, None)

        qbtns = mw.app.mouseButtons()
        executed = manager.handle_scroll(wheel_dir, raw_delta, qbtns)

        if (
            not executed
            and mw.state == "overview"
            and wheel_dir == WheelDir.DOWN
            and not _has_overview_wheel_mappings()
        ):
            prev_state = getattr(mw, "state", None)
            prev_enabled = manager.enabled
            manager.mark_next_undo_as_hotmouse("study_now")
            _study_now_from_overview()
            manager.remember_last_hotmouse_action("study_now", prev_state, prev_enabled)
            executed = True

        return (executed, executed)

    return handled


def on_context_menu(
    target: QWebEngineView,
    ev: QContextMenuEvent,
    _old: Any = lambda t, e: None,
) -> None:
    if target not in WEBVIEW_TARGETS():
        _old(target, ev)
        return
    if manager.right_click_bound_in_current_scope():
        return None
    _old(target, ev)


__all__ = [
    "WEBVIEW_TARGETS",
    "handle_js_message",
    "inject_web_content",
    "on_context_menu",
    "set_config",
    "set_manager",
]
