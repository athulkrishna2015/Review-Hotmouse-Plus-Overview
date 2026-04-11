document.addEventListener("wheel", (ev) => {
    const isScrollbar = ev.clientX > document.documentElement.clientWidth;
    const isBottom = window.innerHeight < 150 || !!document.getElementById('checker') || !!document.getElementById('bottombar');

    // Allow normal scrolling on the scrollbar area
    if (isScrollbar) return;

    // If only-bottom-bar mode is active and we're NOT on the bottom bar, allow normal scroll
    const cfg = window._hotmouse_config || {};
    if (cfg.wheel_only_on_bottom_bar && !isBottom) return;

    // Prevent default BEFORE calling pycmd (which is async in modern Anki)
    // so the page doesn't scroll while the hotkey action fires
    ev.preventDefault();
    ev.stopPropagation();

    let req = {
        "key": "wheel",
        "value": ev.deltaY,
        "is_scrollbar": isScrollbar,
        "is_bottom": isBottom
    }
    pycmd("ReviewHotmouse#" + JSON.stringify(req));
}, { passive: false })