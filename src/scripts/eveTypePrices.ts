interface EveTycoonMarketStats {
    buyAvgFivePercent: number;
    sellAvgFivePercent: number;
}

const ROOT_SELECTOR = "[data-eve-type-price]";
const MOUNTED_ATTR = "data-eve-type-price-mounted";
const STATE_ATTR = "data-eve-type-price-state";

const requestCache = new Map<string, Promise<EveTycoonMarketStats>>();
let pageLoadBound = false;

function buildMarketStatsUrl(regionId: number, typeId: number) {
    return `https://evetycoon.com/api/v1/market/stats/${regionId}/${typeId}`;
}

function getRequestKey(regionId: number, typeId: number) {
    return `${regionId}:${typeId}`;
}

function isMarketStats(value: unknown): value is EveTycoonMarketStats {
    return (
        typeof value === "object" &&
        value !== null &&
        "buyAvgFivePercent" in value &&
        typeof value.buyAvgFivePercent === "number" &&
        Number.isFinite(value.buyAvgFivePercent) &&
        "sellAvgFivePercent" in value &&
        typeof value.sellAvgFivePercent === "number" &&
        Number.isFinite(value.sellAvgFivePercent)
    );
}

function getLocale() {
    return document.documentElement.lang || undefined;
}

function formatPrice(value: number) {
    return new Intl.NumberFormat(getLocale(), {
        maximumFractionDigits: 0,
    }).format(Math.round(value));
}

function setPriceText(root: HTMLElement, kind: "buy" | "sell", value: string) {
    for (const element of root.querySelectorAll<HTMLElement>(
        `[data-eve-type-price-value="${kind}"]`,
    )) {
        element.textContent = value;
    }
}

function updateAriaLabel(root: HTMLElement) {
    const name = root.getAttribute("data-eve-type-price-name") ?? "Type";
    const isk = root.getAttribute("data-eve-type-price-isk-label") ?? "";
    const sellLabel =
        root.getAttribute("data-eve-type-price-sell-label") ?? "Sell";
    const buyLabel =
        root.getAttribute("data-eve-type-price-buy-label") ?? "Buy";
    const sellValue =
        root.querySelector<HTMLElement>('[data-eve-type-price-value="sell"]')
            ?.textContent ?? "";
    const buyValue =
        root.querySelector<HTMLElement>('[data-eve-type-price-value="buy"]')
            ?.textContent ?? "";
    const state = root.getAttribute(STATE_ATTR);
    const includeUnit = state === "ready" && isk.length > 0;
    const sellSummary = includeUnit ? `${sellValue} ${isk}` : sellValue;
    const buySummary = includeUnit ? `${buyValue} ${isk}` : buyValue;

    root.setAttribute(
        "aria-label",
        `${name}: ${sellLabel} ${sellSummary}; ${buyLabel} ${buySummary}`,
    );
}

function setLoadingState(root: HTMLElement) {
    root.setAttribute(STATE_ATTR, "loading");
    const loadingLabel =
        root.getAttribute("data-eve-type-price-loading-label") ?? "...";

    setPriceText(root, "sell", loadingLabel);
    setPriceText(root, "buy", loadingLabel);
    updateAriaLabel(root);
}

function setErrorState(root: HTMLElement) {
    root.setAttribute(STATE_ATTR, "error");
    const unavailableLabel =
        root.getAttribute("data-eve-type-price-unavailable-label") ?? "N/A";

    setPriceText(root, "sell", unavailableLabel);
    setPriceText(root, "buy", unavailableLabel);
    updateAriaLabel(root);
}

function setReadyState(root: HTMLElement, stats: EveTycoonMarketStats) {
    root.setAttribute(STATE_ATTR, "ready");
    setPriceText(root, "sell", formatPrice(stats.sellAvgFivePercent));
    setPriceText(root, "buy", formatPrice(stats.buyAvgFivePercent));
    updateAriaLabel(root);
}

function loadMarketStats(regionId: number, typeId: number) {
    const key = getRequestKey(regionId, typeId);
    const existing = requestCache.get(key);

    if (existing) {
        return existing;
    }

    const request = fetch(buildMarketStatsUrl(regionId, typeId), {
        headers: {
            accept: "application/json",
        },
    })
        .then(async (response) => {
            if (!response.ok) {
                throw new Error(
                    `Unexpected response status ${response.status}`,
                );
            }

            const json = await response.json();

            if (!isMarketStats(json)) {
                throw new Error("Malformed market stats payload");
            }

            return json;
        })
        .catch((error) => {
            requestCache.delete(key);
            throw error;
        });

    requestCache.set(key, request);
    return request;
}

function parsePositiveInt(value: string | null) {
    if (!value) {
        return null;
    }

    const parsed = Number.parseInt(value, 10);
    return Number.isSafeInteger(parsed) && parsed > 0 ? parsed : null;
}

export function initEveTypePrices() {
    const rootsByKey = new Map<string, HTMLElement[]>();

    for (const root of document.querySelectorAll<HTMLElement>(ROOT_SELECTOR)) {
        if (root.getAttribute(MOUNTED_ATTR) === "true") {
            continue;
        }

        root.setAttribute(MOUNTED_ATTR, "true");
        setLoadingState(root);

        const regionId = parsePositiveInt(
            root.getAttribute("data-eve-type-price-region-id"),
        );
        const typeId = parsePositiveInt(
            root.getAttribute("data-eve-type-price-type-id"),
        );

        if (regionId === null || typeId === null) {
            setErrorState(root);
            continue;
        }

        const key = getRequestKey(regionId, typeId);
        const roots = rootsByKey.get(key) ?? [];

        roots.push(root);
        rootsByKey.set(key, roots);
    }

    for (const [key, roots] of rootsByKey) {
        const [regionIdText, typeIdText] = key.split(":");
        const regionId = Number.parseInt(regionIdText, 10);
        const typeId = Number.parseInt(typeIdText, 10);

        void loadMarketStats(regionId, typeId)
            .then((stats) => {
                for (const root of roots) {
                    if (!root.isConnected) {
                        continue;
                    }

                    setReadyState(root, stats);
                }
            })
            .catch(() => {
                for (const root of roots) {
                    if (!root.isConnected) {
                        continue;
                    }

                    setErrorState(root);
                }
            });
    }
}

export function registerEveTypePrices() {
    if (!pageLoadBound) {
        document.addEventListener("astro:page-load", initEveTypePrices);
        pageLoadBound = true;
    }

    initEveTypePrices();
}
