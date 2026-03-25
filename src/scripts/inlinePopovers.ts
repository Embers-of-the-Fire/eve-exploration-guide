interface InlinePopoverController {
    closeTimer: number | null;
    popover: HTMLElement;
    trigger: HTMLElement;
}

const ROOT_SELECTOR = "[data-inline-popover-root]";
const POPOVER_SELECTOR = "[data-inline-popover]";
const PORTAL_ROOT_ID = "inline-popover-layer";
const HOVER_MEDIA_QUERY = "(hover: hover)";
const OPEN_ATTR = "data-inline-popover-open";
const MOUNTED_ATTR = "data-inline-popover-mounted";
const PORTED_ATTR = "data-inline-popover-ported";

const controllers = new Set<InlinePopoverController>();
let activeController: InlinePopoverController | null = null;
let listenersBound = false;
let pageLoadBound = false;
let repositionFrame = 0;

function clamp(value: number, min: number, max: number): number {
    return Math.min(Math.max(value, min), max);
}

function supportsHover(): boolean {
    return window.matchMedia(HOVER_MEDIA_QUERY).matches;
}

function getPortalRoot(): HTMLElement {
    const existing = document.getElementById(PORTAL_ROOT_ID);

    if (existing) {
        return existing;
    }

    const root = document.createElement("div");
    root.id = PORTAL_ROOT_ID;
    document.body.append(root);

    return root;
}

function moveToPortal(controller: InlinePopoverController) {
    const root = getPortalRoot();

    if (controller.popover.parentElement !== root) {
        root.append(controller.popover);
    }

    controller.popover.setAttribute(PORTED_ATTR, "true");
}

function restorePopover(controller: InlinePopoverController) {
    controller.trigger.removeAttribute(OPEN_ATTR);
    controller.trigger.removeAttribute(MOUNTED_ATTR);
    controller.popover.removeAttribute(OPEN_ATTR);
    controller.popover.removeAttribute(PORTED_ATTR);
    controller.popover.setAttribute("aria-hidden", "true");
    controller.popover.style.left = "";
    controller.popover.style.maxHeight = "";
    controller.popover.style.top = "";

    if (controller.popover.parentElement !== controller.trigger) {
        controller.trigger.append(controller.popover);
    }
}

function cancelClose(controller: InlinePopoverController) {
    if (controller.closeTimer === null) {
        return;
    }

    window.clearTimeout(controller.closeTimer);
    controller.closeTimer = null;
}

function scheduleReposition() {
    if (!activeController || repositionFrame !== 0) {
        return;
    }

    repositionFrame = window.requestAnimationFrame(() => {
        repositionFrame = 0;

        if (activeController) {
            positionPopover(activeController);
        }
    });
}

function positionPopover(controller: InlinePopoverController) {
    if (!controller.trigger.isConnected) {
        closePopover(controller);
        return;
    }

    moveToPortal(controller);

    controller.popover.style.left = "0px";
    controller.popover.style.maxHeight = "";
    controller.popover.style.top = "0px";

    const gap = 8;
    const margin = 16;
    const triggerRect = controller.trigger.getBoundingClientRect();
    const initialRect = controller.popover.getBoundingClientRect();
    const spaceAbove = triggerRect.top - gap - margin;
    const spaceBelow = window.innerHeight - triggerRect.bottom - gap - margin;
    const placeBelow =
        spaceBelow >= Math.min(initialRect.height, 240) ||
        spaceBelow >= spaceAbove;
    const availableHeight = Math.max(
        96,
        Math.floor(placeBelow ? spaceBelow : spaceAbove),
    );

    controller.popover.style.maxHeight = `${availableHeight}px`;

    const popoverRect = controller.popover.getBoundingClientRect();
    const maxLeft = Math.max(
        margin,
        window.innerWidth - popoverRect.width - margin,
    );
    const maxTop = Math.max(
        margin,
        window.innerHeight - popoverRect.height - margin,
    );
    const left = clamp(
        triggerRect.left + triggerRect.width / 2 - popoverRect.width / 2,
        margin,
        maxLeft,
    );
    const top = clamp(
        placeBelow
            ? triggerRect.bottom + gap
            : triggerRect.top - popoverRect.height - gap,
        margin,
        maxTop,
    );

    controller.popover.style.left = `${Math.round(left)}px`;
    controller.popover.style.top = `${Math.round(top)}px`;
}

function openPopover(controller: InlinePopoverController) {
    cancelClose(controller);

    if (activeController && activeController !== controller) {
        closePopover(activeController);
    }

    activeController = controller;
    controller.trigger.setAttribute(OPEN_ATTR, "true");
    positionPopover(controller);
    controller.popover.setAttribute("aria-hidden", "false");
    controller.popover.setAttribute(OPEN_ATTR, "true");
}

function closePopover(controller: InlinePopoverController) {
    cancelClose(controller);

    controller.trigger.removeAttribute(OPEN_ATTR);
    controller.popover.removeAttribute(OPEN_ATTR);
    controller.popover.setAttribute("aria-hidden", "true");

    if (activeController === controller) {
        activeController = null;
    }
}

function scheduleClose(controller: InlinePopoverController, delay = 80) {
    cancelClose(controller);

    controller.closeTimer = window.setTimeout(() => {
        controller.closeTimer = null;
        closePopover(controller);
    }, delay);
}

function bindController(trigger: HTMLElement, popover: HTMLElement) {
    const controller: InlinePopoverController = {
        closeTimer: null,
        popover,
        trigger,
    };

    controllers.add(controller);
    trigger.setAttribute(MOUNTED_ATTR, "true");
    popover.setAttribute("aria-hidden", "true");
    moveToPortal(controller);

    trigger.addEventListener("pointerenter", () => {
        openPopover(controller);
    });
    trigger.addEventListener("pointerleave", () => {
        scheduleClose(controller);
    });
    trigger.addEventListener("focusin", () => {
        openPopover(controller);
    });
    trigger.addEventListener("focusout", (event) => {
        const nextTarget = event.relatedTarget;

        if (
            nextTarget instanceof Node &&
            (trigger.contains(nextTarget) || popover.contains(nextTarget))
        ) {
            return;
        }

        scheduleClose(controller, 0);
    });
    trigger.addEventListener("click", () => {
        if (!supportsHover()) {
            openPopover(controller);
        }
    });
    popover.addEventListener("pointerenter", () => {
        cancelClose(controller);
    });
    popover.addEventListener("pointerleave", () => {
        scheduleClose(controller);
    });
    popover.addEventListener("focusin", () => {
        cancelClose(controller);
    });
    popover.addEventListener("focusout", (event) => {
        const nextTarget = event.relatedTarget;

        if (
            nextTarget instanceof Node &&
            (trigger.contains(nextTarget) || popover.contains(nextTarget))
        ) {
            return;
        }

        scheduleClose(controller, 0);
    });
}

function resetInlinePopovers() {
    if (repositionFrame !== 0) {
        window.cancelAnimationFrame(repositionFrame);
        repositionFrame = 0;
    }

    activeController = null;

    for (const controller of controllers) {
        cancelClose(controller);
        restorePopover(controller);
    }

    controllers.clear();
}

function bindGlobalListeners() {
    if (listenersBound) {
        return;
    }

    listenersBound = true;

    document.addEventListener(
        "pointerdown",
        (event) => {
            if (!activeController) {
                return;
            }

            const target = event.target;

            if (
                target instanceof Node &&
                (activeController.trigger.contains(target) ||
                    activeController.popover.contains(target))
            ) {
                return;
            }

            closePopover(activeController);
        },
        true,
    );
    document.addEventListener(
        "keydown",
        (event) => {
            if (event.key !== "Escape" || !activeController) {
                return;
            }

            const trigger = activeController.trigger;
            closePopover(activeController);

            if (trigger instanceof HTMLElement && trigger.isConnected) {
                trigger.focus();
            }
        },
        true,
    );
    document.addEventListener("scroll", scheduleReposition, true);
    window.addEventListener("resize", scheduleReposition, { passive: true });
    document.addEventListener("astro:before-swap", resetInlinePopovers);
}

export function initInlinePopovers() {
    bindGlobalListeners();

    for (const trigger of document.querySelectorAll<HTMLElement>(
        ROOT_SELECTOR,
    )) {
        if (trigger.getAttribute(MOUNTED_ATTR) === "true") {
            continue;
        }

        const popover = trigger.querySelector<HTMLElement>(POPOVER_SELECTOR);

        if (!popover) {
            continue;
        }

        bindController(trigger, popover);
    }
}

export function registerInlinePopovers() {
    if (!pageLoadBound) {
        document.addEventListener("astro:page-load", initInlinePopovers);
        pageLoadBound = true;
    }

    initInlinePopovers();
}
