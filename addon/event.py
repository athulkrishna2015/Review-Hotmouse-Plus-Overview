from typing import Any

from anki.hooks import wrap
from aqt import mw, gui_hooks
from aqt.webview import AnkiWebView

from . import config as config_module
from .hotmouse import actions, manager as hm_manager, web as hm_web

config = mw.addonManager.getConfig(__name__)
hm_manager.set_config(config)
hm_web.set_config(config)

manager = hm_manager.HotmouseManager()
actions.set_manager(manager)
hm_web.set_manager(manager)
hm_manager.hotmouseEventFilter = hm_manager.HotmouseEventFilter(manager)

ACTION_OPTS = actions.ACTION_OPTS
Button = actions.Button


def refresh_config() -> None:
    global config
    config = mw.addonManager.getConfig(__name__)
    hm_manager.set_config(config)
    hm_web.set_config(config)
    manager.refresh_shortcuts()


def turn_on() -> None:
    actions.turn_on()


def turn_off() -> None:
    actions.turn_off()


def toggle_on_off() -> None:
    actions.toggle_on_off()


def check_show_support_on_update() -> None:
    addon_package = mw.addonManager.addonFromModule(__name__)
    meta = mw.addonManager.addonMeta(addon_package)
    if meta.get("supporter_opt_out", False):
        return

    try:
        import json
        import os
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        manifest_path = os.path.join(addon_dir, "manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        current_version = manifest.get("version", "0.0.0")
    except Exception:
        current_version = "0.0.0"

    last_version = meta.get("last_showed_support_version", "")

    if last_version != current_version:
        meta["last_showed_support_version"] = current_version
        mw.addonManager.writeAddonMeta(addon_package, meta)

        def open_config_at_support():
            from .ankiaddonconfig import ConfigWindow
            config_window = ConfigWindow(config_module.conf)
            config_module.conf.config_window = config_window
            for fn in config_module.conf.window_open_hook:
                fn(config_window)
            config_window.on_open()

            tab_widget = config_window.main_tab
            for i in range(tab_widget.count()):
                if tab_widget.tabText(i) == "Support":
                    tab_widget.setCurrentIndex(i)
                    break

            config_window.exec()

        from aqt.qt import QTimer
        QTimer.singleShot(1000, open_config_at_support)


def install_event_handlers() -> None:
    manager.add_menu(config_module.conf.open_config)
    for target in hm_web.WEBVIEW_TARGETS():
        hm_manager.add_event_filter(target)

    if hasattr(AnkiWebView, "contextMenuEvent"):
        AnkiWebView.contextMenuEvent = wrap(
            AnkiWebView.contextMenuEvent, hm_web.on_context_menu, "around"
        )
    else:
        AnkiWebView.contextMenuEvent = hm_web.on_context_menu

    check_show_support_on_update()


mw.addonManager.setWebExports(__name__, r"web/.*\.(css|js)")
gui_hooks.main_window_did_init.append(install_event_handlers)
gui_hooks.webview_will_show_context_menu.append(
    lambda wv, m: (
        not manager.enabled
        and mw.state == "review"
        and m.addAction("Enable Hotmouse").triggered.connect(turn_on)
    )
)
gui_hooks.webview_will_set_content.append(hm_web.inject_web_content)
gui_hooks.webview_did_receive_js_message.append(hm_web.handle_js_message)
if hasattr(gui_hooks, "undo_state_did_change"):
    gui_hooks.undo_state_did_change.append(manager.on_undo_state_did_change)
