export interface EveTypePriceDataEntry {
    buyAvgFivePercent: number | null;
    buyOrders: number | null;
    buyOutliers: number | null;
    buyThreshold: number | null;
    buyVolume: number | null;
    sellAvgFivePercent: number | null;
    sellOrders: number | null;
    sellOutliers: number | null;
    sellThreshold: number | null;
    sellVolume: number | null;
}

export const eveTypePriceGeneratedAt: string | null = "2026-03-29T01:19:38.182460+00:00";

export const eveTypePrices: Record<string, EveTypePriceDataEntry> = {
    "10000002:28665": {
        "buyAvgFivePercent": 946150000.0,
        "buyOrders": 45,
        "buyOutliers": 7,
        "buyThreshold": 94620000.0,
        "buyVolume": 44,
        "sellAvgFivePercent": 1019000000.0,
        "sellOrders": 34,
        "sellOutliers": 0,
        "sellThreshold": 10190000000.0,
        "sellVolume": 59
    }
};
