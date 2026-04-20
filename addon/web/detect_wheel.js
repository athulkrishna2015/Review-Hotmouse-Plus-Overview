if (!window.__reviewHotmouseWheelListenerInstalled) {
window.__reviewHotmouseWheelListenerInstalled = true;
window.__hotmouseBoundaryLatch = window.__hotmouseBoundaryLatch || { down: false, up: false };
window.__hotmouseBoundaryLatchTs = window.__hotmouseBoundaryLatchTs || { down: 0, up: 0 };

// Axis lock for trackpad gestures: once a dominant axis is detected during a
// continuous gesture, commit to it so imprecise finger movement doesn't cause
// axis oscillation between horizontal and vertical.
window.__hotmouseAxisLock = window.__hotmouseAxisLock || {
    axis: null,      // "h" or "v" once locked
    cumX: 0,
    cumY: 0,
    lastTs: 0
};

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

    // If the addon is disabled (e.g. double-click toggle), let the page
    // scroll normally — don't preventDefault or send pycmd.
    if (window._hotmouse_enabled === false) return;

    // If only-bottom-bar mode is active and we're NOT on the bottom bar, allow normal scroll
    if (cfg.wheel_only_on_bottom_bar && !isBottom) return;

    // --- Axis locking for trackpad gestures ---
    // Trackpad two-finger swipes produce many small wheel events with mixed
    // deltaX/deltaY.  We accumulate movement and once a dominant axis emerges
    // (threshold: 10px total), lock to it for the rest of the gesture.
    // A gesture is considered "continuous" if events arrive within 300ms.
    const axL = window.__hotmouseAxisLock;
    const now = Date.now();
    if (now - axL.lastTs > 300) {
        // New gesture – reset
        axL.axis = null;
        axL.cumX = 0;
        axL.cumY = 0;
    }
    axL.lastTs = now;
    axL.cumX += ev.deltaX;
    axL.cumY += ev.deltaY;

    if (!axL.axis) {
        const ax = Math.abs(axL.cumX);
        const ay = Math.abs(axL.cumY);
        if (ax >= 10 || ay >= 10) {
            axL.axis = ax > ay ? "h" : "v";
        }
    }

    // Determine effective deltas: once locked, zero out the non-dominant axis
    let effectiveDX = ev.deltaX;
    let effectiveDY = ev.deltaY;
    if (axL.axis === "h") {
        effectiveDY = 0;
    } else if (axL.axis === "v") {
        effectiveDX = 0;
    }

    // Smart scroll: let the page scroll naturally for long cards, only trigger
    // the hotkey action when the user has reached the boundary and scrolls again.
    // If the mouse is on the bottom bar, bypass this and trigger the hotkey instantly.
    // NOTE: Smart scroll only applies to VERTICAL movement; horizontal gestures bypass it.
    const isHorizontalGesture = axL.axis === "h";
    if (cfg.smart_scroll && !isBottom && !isHorizontalGesture) {
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
            const scrollingDown = effectiveDY > 0;
            const scrollingUp = effectiveDY < 0;
            
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

    // If neither axis has meaningful movement yet, skip
    if (effectiveDX === 0 && effectiveDY === 0) return;

    // Check if there is anything actually mapped to this event.
    // If not, let it through natively.
    let dx = effectiveDX;
    let dy = effectiveDY;
    if (cfg.natural_scrolling !== false) {
        dx = -dx;
    }
    let wheelDir = null;
    if (Math.abs(dy) >= Math.abs(dx) && dy !== 0) {
        wheelDir = dy > 0 ? "down" : "up";
    } else if (Math.abs(dx) > Math.abs(dy) && dx !== 0) {
        wheelDir = dx > 0 ? "right" : "left";
    }

    if (wheelDir && window._hotmouse_shortcuts) {
        let btns = [];
        if (ev.buttons & 1) btns.push("press_left");
        if (ev.buttons & 2) btns.push("press_right");
        if (ev.buttons & 4) btns.push("press_middle");
        if (ev.buttons & 8) btns.push("press_xbutton1");
        if (ev.buttons & 16) btns.push("press_xbutton2");

        let scope = "q";
        if (window._hotmouse_scope === "o") {
            scope = "o";
        } else {
            if (document.body && document.body.classList.contains("answer")) {
                scope = "a";
            } else if (document.getElementById("answer")) {
                scope = "a";
            }
        }

        let parts = [scope].concat(btns);
        parts.push("wheel_" + wheelDir);
        let hotkey_str = parts.join("_");
        
        let action = window._hotmouse_shortcuts[hotkey_str];
        if (!action || action === "" || action === "<none>") {
            // Nothing mapped, let native scrolling take over immediately
            return;
        }
    }

    // Prevent default BEFORE calling pycmd (which is async in modern Anki)
    // so the page doesn't scroll while the hotkey action fires
    ev.preventDefault();
    ev.stopPropagation();

    let req = {
        "key": "wheel",
        "valueX": effectiveDX,
        "valueY": effectiveDY,
        "is_scrollbar": isScrollbar,
        "is_bottom": isBottom,
        "at_boundary": atBoundary
    }
    pycmd("ReviewHotmouse#" + JSON.stringify(req));
}, { passive: false });
}

