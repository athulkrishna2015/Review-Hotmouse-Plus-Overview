document.addEventListener("wheel", (ev) => {
    const isScrollbar = ev.clientX > document.documentElement.clientWidth;
    const isBottom = window.innerHeight < 150 || !!document.getElementById('checker') || !!document.getElementById('bottombar');

    // Allow normal scrolling on the scrollbar area
    if (isScrollbar) return;

    const cfg = window._hotmouse_config || {};

    // If only-bottom-bar mode is active and we're NOT on the bottom bar, allow normal scroll
    if (cfg.wheel_only_on_bottom_bar && !isBottom) return;

    // Smart scroll: let the page scroll naturally for long cards, only trigger
    // the hotkey action when the user has reached the boundary and scrolls again.
    if (cfg.smart_scroll) {
        const doc = document.documentElement;
        const scrollable = doc.scrollHeight > window.innerHeight + 2;

        if (scrollable) {
            const scrollingDown = ev.deltaY > 0;
            const scrollingUp = ev.deltaY < 0;
            const atBottom = (window.scrollY + window.innerHeight) >= (doc.scrollHeight - 2);
            const atTop = window.scrollY <= 1;

            // Not at the boundary yet — let the page scroll normally
            if (scrollingDown && !atBottom) return;
            if (scrollingUp && !atTop) return;
        }
    }

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