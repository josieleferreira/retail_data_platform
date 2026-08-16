"""Previsão mensal de demanda com validação temporal."""

from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
import joblib


def _features(panel: pd.DataFrame) -> pd.DataFrame:
    x = panel.sort_values(["product_id", "month"]).copy()
    g = x.groupby("product_id")["demand"]
    for lag in (1, 2, 3, 6, 12): x[f"lag_{lag}"] = g.shift(lag)
    x["rolling_3"] = g.transform(lambda s: s.shift(1).rolling(3).mean())
    x["rolling_6"] = g.transform(lambda s: s.shift(1).rolling(6).mean())
    x["month_sin"] = np.sin(2*np.pi*x.month.dt.month/12)
    x["month_cos"] = np.cos(2*np.pi*x.month.dt.month/12)
    x["trend"] = (x.month.dt.year - x.month.dt.year.min())*12 + x.month.dt.month
    return x.dropna().reset_index(drop=True)


def forecast(sales: pd.DataFrame, output_dir: Path, model_dir: Path, top_n=50, horizon=3, test_months=6, seed=42) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True); model_dir.mkdir(parents=True, exist_ok=True)
    s = sales.copy(); s["order_date"] = pd.to_datetime(s.order_date)
    s["effective_qty"] = (s.quantity - s.refunded_qty).clip(lower=0)
    top = s.groupby("product_id").effective_qty.sum().nlargest(top_n).index
    monthly = (s[s.product_id.isin(top)].assign(month=s.order_date.dt.to_period("M").dt.to_timestamp())
               .groupby(["product_id", "product_name", "month"], as_index=False).effective_qty.sum()
               .rename(columns={"effective_qty": "demand"}))
    months = pd.date_range(monthly.month.min(), monthly.month.max(), freq="MS")
    names = monthly[["product_id", "product_name"]].drop_duplicates()
    grid = pd.MultiIndex.from_product([top, months], names=["product_id", "month"]).to_frame(index=False)
    panel = grid.merge(names, on="product_id", how="left").merge(monthly, on=["product_id", "product_name", "month"], how="left")
    panel["demand"] = panel.demand.fillna(0)
    feat = _features(panel)
    cutoff = feat.month.max() - pd.DateOffset(months=test_months-1)
    train, test = feat[feat.month < cutoff], feat[feat.month >= cutoff]
    cols = ["product_id", "lag_1", "lag_2", "lag_3", "lag_6", "lag_12", "rolling_3", "rolling_6", "month_sin", "month_cos", "trend"]
    model = HistGradientBoostingRegressor(loss="poisson", max_iter=250, learning_rate=.06, max_leaf_nodes=24, l2_regularization=1.0, random_state=seed)
    model.fit(train[cols], train.demand)
    pred = np.maximum(0, model.predict(test[cols]))
    naive = test.lag_12.to_numpy()
    denom = test.demand.sum()
    metrics = {
        "cutoff": str(cutoff.date()), "test_months": test_months,
        "mae_model": float(mean_absolute_error(test.demand, pred)),
        "mae_seasonal_naive": float(mean_absolute_error(test.demand, naive)),
        "wape_model": float(np.abs(test.demand-pred).sum()/denom),
        "wape_seasonal_naive": float(np.abs(test.demand-naive).sum()/denom),
        "observations_train": len(train), "observations_test": len(test), "products": len(top),
    }
    evaluation = test[["product_id", "product_name", "month", "demand"]].copy()
    evaluation["prediction"] = pred; evaluation["seasonal_naive"] = naive
    evaluation.to_csv(output_dir / "forecast_backtest.csv", index=False)

    final_model = HistGradientBoostingRegressor(loss="poisson", max_iter=250, learning_rate=.06, max_leaf_nodes=24, l2_regularization=1.0, random_state=seed)
    final_model.fit(feat[cols], feat.demand)
    history = panel.copy(); future_rows = []
    for _ in range(horizon):
        next_month = history.month.max() + pd.DateOffset(months=1)
        new = names.copy(); new["month"] = next_month; new["demand"] = 0.0
        candidate = pd.concat([history, new], ignore_index=True)
        fx = _features(candidate); fx = fx[fx.month == next_month]
        fx["prediction"] = np.maximum(0, final_model.predict(fx[cols]))
        future_rows.append(fx[["product_id", "product_name", "month", "prediction"]])
        new = new.merge(fx[["product_id", "prediction"]], on="product_id"); new["demand"] = new.prediction; new = new.drop(columns="prediction")
        history = pd.concat([history, new], ignore_index=True)
    future = pd.concat(future_rows, ignore_index=True)
    future.to_csv(output_dir / "demand_forecast_3_months.csv", index=False)
    joblib.dump({"model": final_model, "features": cols}, model_dir / "demand_model.joblib")
    (output_dir / "forecast_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"metrics": metrics, "future": future, "evaluation": evaluation}
