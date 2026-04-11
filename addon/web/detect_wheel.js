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
    // If the mouse is on the bottom bar, bypass this and trigger the hotkey instantly.
    if (cfg.smart_scroll && !isBottom) {
        const scrollElem = document.scrollingElement || document.documentElement;
        
        const scrollHeight = Math.round(scrollElem.scrollHeight);
        const clientHeight = Math.round(scrollElem.clientHeight);
        const scrollTop = Math.round(scrollElem.scrollTop || window.scrollY || 0);

        const isScrollable = scrollHeight > clientHeight + 2;

        if (isScrollable) {
            const scrollingDown = ev.deltaY > 0;
            const scrollingUp = ev.deltaY < 0;
            
            // Check boundaries with some margin for fractional DPI scaling
            const atBottom = (scrollTop + clientHeight) >= (scrollHeight - 4);
            const atTop = scrollTop <= 2;

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