from typing import NamedTuple, Optional, List, Dict, Tuple, Union, Literal

from aqt.qt import *

from ..ankiaddonconfig import ConfigLayout, ConfigWindow
from ..event import ACTION_OPTS, Button


class Options(NamedTuple):
    mode: List[str]
    button: List[str]
    wheel: List[str]
    action: List[str]


OPTS = Options(
    mode=["press", "click", "wheel"],
    button=[b.name for b in Button],
    wheel=["up", "down", "left", "right"],
    action=ACTION_OPTS,
)


class DDConfigLayout(ConfigLayout):
    def __init__(self, conf_window: ConfigWindow):
        super().__init__(conf_window, QBoxLayout.Direction.LeftToRight)
        self.dropdowns: List[QComboBox] = []

    def create_dropdown(
        self, current: str, options: List[str], is_mode: bool = False
    ) -> QComboBox:
        dropdown = QComboBox()
        dropdown.insertItems(0, options)
        dropdown.setCurrentIndex(options.index(current))
        self.addWidget(dropdown)
        self.dropdowns.append(dropdown)

        if is_mode:
            ddidx = len(self.dropdowns) - 1
            dropdown.currentIndexChanged.connect(
                lambda optidx, d=ddidx: self.on_mode_change(optidx, d)
            )

        return dropdown

    def on_mode_change(self, optidx: int, ddidx: int) -> None:
        """Handler for when mode dropdown changes"""
        mode = OPTS.mode[optidx]
        dropdowns = self.dropdowns

        if mode == "press":
            dd = dropdowns.pop(ddidx + 1)
            self.removeWidget(dd)
            dd.deleteLater()
            self.create_dropdown(OPTS.button[0], OPTS.button)
            self.create_dropdown("click", OPTS.mode, is_mode=True)
            self.create_dropdown(OPTS.button[0], OPTS.button)
        else:
            while len(dropdowns) > ddidx + 1:
                dd = dropdowns.pop()
                self.removeWidget(dd)
                dd.deleteLater()

            if mode == "click":
                self.create_dropdown(OPTS.button[0], OPTS.button)
            else:  # mode == "wheel"
                self.create_dropdown(OPTS.wheel[0], OPTS.wheel)


class HotkeyTabManager:
    def __init__(
        self, tab: ConfigLayout, side: Union[Literal["q"], Literal["a"], Literal["o"], Literal["c"]]
    ) -> None:
        self.tab = tab
        self.config_window = tab.config_window
        self.side = side

        self.layouts: List[Tuple[DDConfigLayout, DDConfigLayout]] = []
        self.setup_tab()

    def setup_tab(self) -> None:
        tab = self.tab
        self.rows_layout = self.tab.vlayout()
        btn_layout = tab.hlayout()
        add_btn = QPushButton("+ Add New ")

        default_hotkey = {
            "o": "o_wheel_down",
            "q": "q_click_right",
            "a": "a_click_right",
            "c": "c_click_right",
        }.get(self.side, f"{self.side}_click_right")

        add_btn.clicked.connect(lambda _: self.add_row(default_hotkey, ""))
        add_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        btn_layout.addWidget(add_btn)
        btn_layout.stretch()
        btn_layout.setContentsMargins(0, 20, 0, 5)

        tab.setSpacing(0)
        tab.addLayout(btn_layout)
        tab.stretch()
        tab.space(10)
        tab.text("If you set duplicate hotkeys, only the last one will be saved.")

    def create_layout(self) -> DDConfigLayout:
        return DDConfigLayout(self.config_window)

    def clear_rows(self) -> None:
        for _ in range(self.rows_layout.count()):
            widget = self.rows_layout.itemAt(0).widget()
            self.rows_layout.removeWidget(widget)
            widget.deleteLater()
        self.layouts = []

    def setup_rows(self) -> None:
        hotkeys = self.config_window.conf.get("shortcuts")
        for hotkey in hotkeys:
            if hotkey and hotkey[0] == self.side:
                self.add_row(hotkey, hotkeys[hotkey])

    def hotkey_layout(self, hotkey: str) -> Optional[DDConfigLayout]:
        layout = self.create_layout()
        hotkeylist = hotkey[2:].split("_")

        if len(hotkeylist) % 2 != 0:
            return None

        for i in range(0, len(hotkeylist), 2):
            mode = hotkeylist[i]
            btn = hotkeylist[i + 1]

            if mode not in OPTS.mode:
                return None

            if mode == "wheel" and btn not in OPTS.wheel:
                return None

            if mode in ("press", "click") and btn not in OPTS.button:
                return None

            layout.create_dropdown(mode, OPTS.mode, is_mode=True)

            if mode == "wheel":
                layout.create_dropdown(btn, OPTS.wheel)
            else:
                layout.create_dropdown(btn, OPTS.button)

        return layout

    def action_layout(self, action: str) -> Optional[DDConfigLayout]:
        if action not in OPTS.action:
            return None

        layout = self.create_layout()
        layout.stretch()
        layout.text(" → ", html=True)
        layout.create_dropdown(action, OPTS.action)

        return layout

    def add_row(self, hotkey: str, action: str) -> None:
        hlay = self.hotkey_layout(hotkey)
        alay = self.action_layout(action)

        if hlay and alay:
            container = QWidget()
            layout = self.create_layout()
            layout.setContentsMargins(0, 4, 2, 4)
            container.setLayout(layout)
            self.rows_layout.addWidget(container)

            layout.addLayout(hlay)
            layout.addLayout(alay)
            layout_tuple = (hlay, alay)
            self.layouts.append(layout_tuple)

            remove_btn = QPushButton("⌫")
            remove_btn.setToolTip("Delete this shortcut.")
            remove_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            remove_btn.setFlat(True)
            remove_btn.setFixedWidth(28)
            layout.addWidget(remove_btn)

            def remove(layouts: Tuple[DDConfigLayout, DDConfigLayout]) -> None:
                self.rows_layout.removeWidget(container)
                container.deleteLater()
                self.layouts.remove(layouts)

            remove_btn.clicked.connect(lambda _, t=layout_tuple: remove(t))

    def on_update(self) -> None:
        self.clear_rows()
        self.setup_rows()

    def get_data(self, hotkeys_data: Dict[str, str]) -> None:
        for row in self.layouts:
            hotkey_layout = row[0]
            action_layout = row[1]
            hotkey_str = self.side

            for dd in hotkey_layout.dropdowns:
                hotkey_str += "_" + dd.currentText()

            hotkey_str = self.sort_hotkey_btn(hotkey_str)
            action_str = action_layout.dropdowns[0].currentText()
            hotkeys_data[hotkey_str] = action_str

    @staticmethod
    def sort_hotkey_btn(hotkey_str: str) -> str:
        hotkeylist = hotkey_str.split("_")

        if len(hotkeylist) - 1 <= 4:
            return hotkey_str

        btns: List[str] = []
        btn_names = [b.name for b in Button]

        for i in range(1, len(hotkeylist) - 2, 2):
            btn = hotkeylist[i + 1]
            btns.append(btn)

        btns = sorted(btns, key=lambda x: btn_names.index(x))

        new_hotkey_str = "{}_".format(hotkeylist[0])
        for btn in btns:
            new_hotkey_str += "press_"
            new_hotkey_str += "{}_".format(btn)

        new_hotkey_str += "{}_{}".format(hotkeylist[-2], hotkeylist[-1])
        return new_hotkey_str


def hotkey_tabs(conf_window: ConfigWindow) -> None:
    q_tab = conf_window.add_tab("Question Hotkeys")
    q_manager = HotkeyTabManager(q_tab, "q")

    a_tab = conf_window.add_tab("Answer Hotkeys")
    a_manager = HotkeyTabManager(a_tab, "a")

    o_tab = conf_window.add_tab("Overview Hotkeys")
    o_manager = HotkeyTabManager(o_tab, "o")

    c_tab = conf_window.add_tab("Congratulations Hotkeys")
    c_manager = HotkeyTabManager(c_tab, "c")

    conf_window.widget_updates.append(q_manager.on_update)
    conf_window.widget_updates.append(a_manager.on_update)
    conf_window.widget_updates.append(o_manager.on_update)
    conf_window.widget_updates.append(c_manager.on_update)

    def save_hotkeys() -> None:
        hotkeys: Dict[str, str] = {}
        q_manager.get_data(hotkeys)
        a_manager.get_data(hotkeys)
        o_manager.get_data(hotkeys)
        c_manager.get_data(hotkeys)
        conf_window.conf.set("shortcuts", hotkeys)

    conf_window.execute_on_save(save_hotkeys)
