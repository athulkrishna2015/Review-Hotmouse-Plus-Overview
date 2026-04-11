if (!window.__reviewHotmouseWheelListenerInstalled) {
window.__reviewHotmouseWheelListenerInstalled = true;
window.__hotmouseBoundaryLatch = window.__hotmouseBoundaryLatch || { down: false, up: false };
window.__hotmouseBoundaryLatchTs = window.__hotmouseBoundaryLatchTs || { down: 0, up: 0 };

function isScrollableContainer(node) {
    if (!(node instanceof Element)) return false;
    const style = window.getComputedStyle(node);
    const overflowY = style.overflowY;
    const canScroll = overflowY === "auto" || overflowY === "scroll" || overflowY === "overlay";
    return canScroll && node.scrollHeight > node.clientHeight + 2;
}

document.addEventListener("wheel", (ev) => {
    const target = ev.target instanceof Element ? ev.target : null;
    const isScrollbar = ev.clientX > document.documentElement.clientWidth;
    const isBottom = window.innerHeight < 150 || !!(target && target.closest("#checker, #bottombar"));
    let atBoundary = false;

    // Allow normal scrolling on the scrollbar area
    if (isScrollbar) return;

    const cfg = window._hotmouse_config || {};

    // If only-bottom-bar mode is active and we're NOT on the bottom bar, allow normal scroll
    if (cfg.wheel_only_on_bottom_bar && !isBottom) return;

    // Smart scroll: let the page scroll naturally for long cards, only trigger
    // the hotkey action when the user has reached the boundary and scrolls again.
    // If the mouse is on the bottom bar, bypass this and trigger the hotkey instantly.
    // NOTE: Smart scroll currently only applies to VERTICAL movement.
    if (cfg.smart_scroll && !isBottom) {
        let scrollElem = target;
        while (scrollElem instanceof Element) {
            if (isScrollableContainer(scrollElem)) {
                break;
            }
            scrollElem = scrollElem.parentElement;
        }
        if (!(scrollElem instanceof Element)) {
            scrollElem = document.scrollingElement || document.documentElement;
        }
        
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
            // Only block vertical gestures if we're not at the bounds
            if (scrollingDown && !atBottom) {
                window.__hotmouseBoundaryLatch.down = false;
                return;
            }
            if (scrollingUp && !atTop) {
                window.__hotmouseBoundaryLatch.up = false;
                return;
            }
            atBoundary = (scrollingDown && atBottom) || (scrollingUp && atTop);

            // Require another scroll after first reaching a boundary on scrollable cards.
            if (scrollingDown && atBottom && !window.__hotmouseBoundaryLatch.down) {
                window.__hotmouseBoundaryLatch.down = true;
                window.__hotmouseBoundaryLatchTs.down = Date.now();
                ev.preventDefault();
                ev.stopPropagation();
                return;
            }
            if (scrollingUp && atTop && !window.__hotmouseBoundaryLatch.up) {
                window.__hotmouseBoundaryLatch.up = true;
                window.__hotmouseBoundaryLatchTs.up = Date.now();
                ev.preventDefault();
                ev.stopPropagation();
                return;
            }

            // If we hit the boundary in the same continuous gesture, keep swallowing
            // until the user scrolls again after a short pause.
            if (scrollingDown && atBottom && window.__hotmouseBoundaryLatch.down) {
                if (Date.now() - window.__hotmouseBoundaryLatchTs.down < 200) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    return;
                }
            }
            if (scrollingUp && atTop && window.__hotmouseBoundaryLatch.up) {
                if (Date.now() - window.__hotmouseBoundaryLatchTs.up < 200) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    return;
                }
            }
        } else {
            atBoundary = true;
        }
    }

    // Prevent default BEFORE calling pycmd (which is async in modern Anki)
    // so the page doesn't scroll while the hotkey action fires
    ev.preventDefault();
    ev.stopPropagation();

    let req = {
        "key": "wheel",
        "valueX": ev.deltaX,
        "valueY": ev.deltaY,
        "is_scrollbar": isScrollbar,
        "is_bottom": isBottom,
        "at_boundary": atBoundary
    }
    pycmd("ReviewHotmouse#" + JSON.stringify(req));
}, { passive: false });
}
