from pathlib import Path

from aqt import mw
from aqt.qt import *
from aqt.webview import AnkiWebView

from ..ankiaddonconfig import ConfigWindow


def copy_to_clipboard(text: str) -> None:
    QApplication.clipboard().setText(text)
    mw.checkpoint("Copied to clipboard")
    from aqt.utils import tooltip

    tooltip(f"Copied: {text}")


def support_tab(conf_window: ConfigWindow) -> None:
    tab_layout = conf_window.add_tab("Support")
    scroll = tab_layout.vscroll_layout()

    scroll.text("<b>Thank you for using Review Hotmouse!</b>", size=16, html=True)
    scroll.text("If you find this add-on useful, please consider supporting my work.")
    scroll.space(10)

    addon_path = Path(__file__).parent.parent
    support_data = [
        ("UPI", "athulkrishnasv2015-2@okhdfcbank", "UPI.jpg"),
        ("BTC", "bc1qrrek3m7sr33qujjrktj949wav6mehdsk057cfx", "BTC.jpg"),
        ("ETH", "0xce6899e4903EcB08bE5Be65E44549fadC3F45D27", "ETH.jpg"),
    ]
    # Ko-fi Widget (Embedded Script)
    support_webview = AnkiWebView(conf_window)
    support_webview.setFixedHeight(40)  # Enough for the widget button if not floating
    kofi_html = f"""
    <html>
    <head>
    <style>
      body {{ background-color: transparent; margin: 0; padding: 0; overflow: hidden; }}
    </style>
    <script type='text/javascript' src='https://storage.ko-fi.com/cdn/widget/Widget_2.js'></script>
    <script type='text/javascript'>
      kofiwidget2.init('Support me on Ko-fi', '#72a4f2', 'D1D01W6NQT');
      kofiwidget2.draw();
    </script>
    </head>
    <body></body>
    </html>
    """
    support_webview.setHtml(kofi_html)
    scroll.addWidget(support_webview)

    for name, address, qr_file in support_data:
        group = scroll.vcontainer()
        group.text(f"<b>{name}</b>", html=True, size=14)

        # QR Code
        qr_path = addon_path / "Support" / qr_file
        if qr_path.exists():
            pixmap = QPixmap(str(qr_path))
            if not pixmap.isNull():
                label = QLabel()
                label.setPixmap(
                    pixmap.scaled(
                        400,
                        400,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                group.addWidget(label)

        # Address and Copy Button
        addr_row = group.hlayout()
        addr_row.text(address, multiline=True)
        addr_row.space(10)
        copy_btn = QPushButton("Copy")
        copy_btn.setFixedWidth(60)
        copy_btn.clicked.connect(lambda _, a=address: copy_to_clipboard(a))
        addr_row.addWidget(copy_btn)
        addr_row.stretch()

        scroll.hseparator()
        scroll.space(10)

    scroll.stretch()
