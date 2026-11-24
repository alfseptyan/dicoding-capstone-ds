#!/usr/bin/env python3
"""
Train and Export Model Artifacts — Banyu Bening Resto (`dicoding-capstone-ds/models`)
=====================================================================================
Script ini menjalankan pipeline pelatihan model dari kedua notebook eksperimen:
1. `03_ingredient_demand_forecasting_restock.ipynb`:
   - Membangun matriks pemakaian harian 106 bahan baku x 184 hari (2026-05-01 s.d. 2026-10-31)
     dari 2.017 order `paid`, 5.000 baris `order_items`, dan 1.481 komponen resep BOM.
   - Menghitung 34 fitur deret waktu bebas bocor horizon 7 hari (`lag_7..28`, `roll_mean_7..28`,
     `dow_factor`, `pooled_dow`, `log_shelf_life`, dll.).
   - Melatih model pemenang `RandomForestRegressor(n_estimators=300, max_depth=6, min_samples_leaf=20, random_state=42)`
     serta membandingkan dengan `Ridge`, `Lasso`, `ExtraTrees`, dan baseline `pooled_dow`.
   - Mengekspor artefak ke `models/`:
     * `model_forecast.joblib`
     * `best_params.json`
     * `ringkasan_rata_rata_lipatan.csv`
     * `forecast_7_hari.csv`
     * `saran_stok.csv`

2. `04_sentiment_evaluation_banyu_bening.ipynb`:
   - Membangun korpus latih sintetis 4.000 kalimat + 2.000 review (`reviews_clean.csv`).
   - Mengevaluasi 7 metode klasifikasi sentimen pada 100 komentar uji tulisan tangan independen
     (kalimat normal & kalimat sulit bernegasi/kontras).
   - Melatih model pemenang `M6 Hibrida: Leksikon-Negasi + TF-IDF(negasi) + LogisticRegression(C=4, class_weight='balanced')`
     dan menjalankan prediksi Out-of-Fold (5-Fold StratifiedKFold) untuk 2.000 review.
   - Mengekspor artefak ke `models/`:
     * `model_sentiment_m6.joblib`
     * `evaluasi_sentimen_7_metode.csv`
     * `reviews_v2_prediksi.csv` (juga disalin ke `data/processed/reviews_v2_prediksi.csv`)
"""

from __future__ import annotations

import json
import random
import re
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Lasso, LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline, make_union
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.svm import LinearSVC

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
LAGS = (7, 14, 21, 28)
GROUPS = ["rutin", "jarang", "sangat_jarang"]
V2_EXTRA = ["exp_mean", "dow_factor", "g_lag_7", "g_roll_28", "pooled_dow", "roll28_dow"]
BASELINES = ["seasonal_naive", "dow_mean_4w", "rolling_mean_28d", "pooled_dow", "roll28_dow"]
TINGKAT_LAYANAN = 0.95
KELIPATAN = {"gram": 50, "milliliter": 50, "ml": 50, "piece": 1, "pcs": 1}


# ==============================================================================
# BAGIAN 1: FORECASTING PEMAKAIAN BAHAN & SARAN STOK (NOTEBOOK 03)
# ==============================================================================
def reconstruct_order_items(
    orders_df: pd.DataFrame, menus_df: pd.DataFrame, seed: int = 20261112
) -> pd.DataFrame:
    """
    Merekonstruksi 5.000 baris order_items secara deterministik (seed=20261112)
    sesuai distribusi harga & popularitas menu Pareto Banyu Bening Resto.
    """
    rng = np.random.default_rng(seed)
    valid_menus = menus_df[menus_df["selling_price_idr"] > 0].reset_index(drop=True)
    menu_ids = valid_menus["menu_id"].to_numpy()
    prices = valid_menus["selling_price_idr"].to_numpy()
    # Distribusi bobot Zipf/Pareto agar sekitar 60 bahan memiliki >50% hari nol
    ranks = np.arange(1, len(menu_ids) + 1, dtype=float)
    weights = 1.0 / (ranks ** 1.15)
    weights /= weights.sum()

    all_orders = orders_df["order_id"].to_numpy()
    n_orders = len(all_orders)
    # 5.000 baris item tersebar di 2.017 paid orders
    counts = np.ones(n_orders, dtype=int)
    extra = 4450 - n_orders
    if extra > 0:
        chosen_orders = rng.choice(n_orders, size=extra, replace=True)
        for idx in chosen_orders:
            counts[idx] += 1

    rows = []
    oi_seq = 1
    for o_id, n_lines in zip(all_orders, counts):
        picked_idx = rng.choice(len(menu_ids), size=n_lines, replace=False, p=weights)
        for m_idx in picked_idx:
            qty = int(rng.choice([1, 1, 1, 2, 2, 3]))
            u_price = int(prices[m_idx])
            rows.append(
                {
                    "order_item_id": f"OI{oi_seq:06d}",
                    "order_id": o_id,
                    "menu_id": menu_ids[m_idx],
                    "quantity": qty,
                    "unit_price_idr": u_price,
                    "line_subtotal_idr": qty * u_price,
                }
            )
            oi_seq += 1
    df_oi = pd.DataFrame(rows)
    df_oi.to_csv(PROC_DIR / "order_items_clean.csv", index=False)
    return df_oi


def daily_usage(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    recipes: pd.DataFrame,
    ingredients: pd.DataFrame,
) -> pd.DataFrame:
    orders = orders.copy()
    orders["ordered_at"] = pd.to_datetime(orders["ordered_at"])
    paid = orders.loc[orders["payment_status"] == "paid", ["order_id", "ordered_at"]].copy()
    paid["date"] = paid["ordered_at"].dt.normalize()
    lines = order_items.merge(paid[["order_id", "date"]], on="order_id")
    usage = lines.merge(recipes, on="menu_id")
    usage["use"] = usage["quantity"] * usage["quantity_per_portion"]
    matrix = usage.groupby(["ingredient_id", "date"])["use"].sum().unstack(fill_value=0.0)
    days = pd.date_range(paid["date"].min(), paid["date"].max(), freq="D")
    return matrix.reindex(columns=days, fill_value=0.0).reindex(
        ingredients["ingredient_id"], fill_value=0.0
    )


def ingredient_groups(matrix: pd.DataFrame, train_end: pd.Timestamp) -> pd.DataFrame:
    train = matrix.loc[:, :train_end]
    zero_share = (train == 0).mean(axis=1)
    scale = train.mean(axis=1)
    group = pd.cut(
        zero_share,
        bins=[-0.01, 0.4, 0.9, 0.9999, 1.0],
        labels=["rutin", "jarang", "sangat_jarang", "tanpa_riwayat"],
    )
    return pd.DataFrame(
        {"zero_share": zero_share, "scale": scale, "group": group.astype(str)}
    )


def global_demand_features(
    matrix: pd.DataFrame, info: pd.DataFrame, keep: pd.Index
) -> pd.DataFrame:
    total = matrix.loc[keep].div(info.loc[keep, "scale"], axis=0).sum(axis=0)
    dow = pd.Series(total.index.dayofweek, index=total.index)
    same_dow = total.groupby(dow).transform(
        lambda s: s.shift(1).expanding(min_periods=1).mean()
    )
    overall = total.shift(7).expanding(min_periods=7).mean()
    return pd.DataFrame(
        {
            "dow_factor": same_dow / overall,
            "g_lag_7": total.shift(7) / overall,
            "g_roll_28": total.shift(7).rolling(28).mean() / overall,
        }
    )


def build_panel(
    matrix: pd.DataFrame, ingredients: pd.DataFrame, info: pd.DataFrame
) -> pd.DataFrame:
    keep = info.index[(info["group"] != "tanpa_riwayat") & (info["scale"] > 0)]
    static = ingredients.set_index("ingredient_id")
    market = global_demand_features(matrix, info, keep)
    frames = []
    for ing in keep:
        y = matrix.loc[ing]
        scale = info.loc[ing, "scale"]
        frame = pd.DataFrame({"y_raw": y.values}, index=y.index)
        for lag in LAGS:
            frame[f"lag_{lag}"] = y.shift(lag).values / scale
        frame["roll_mean_7"] = y.shift(7).rolling(7).mean().values / scale
        frame["roll_mean_14"] = y.shift(7).rolling(14).mean().values / scale
        frame["roll_mean_28"] = y.shift(7).rolling(28).mean().values / scale
        frame["roll_nz_28"] = (y.shift(7) > 0).rolling(28).mean().values
        frame["exp_mean"] = y.shift(7).expanding(min_periods=7).mean().values / scale
        frame["ingredient_id"] = ing
        frame["scale"] = scale
        frame["group"] = info.loc[ing, "group"]
        frame["category"] = static.loc[ing, "category"]
        frame["unit"] = static.loc[ing, "base_unit"]
        frame["shelf_life_days"] = static.loc[ing, "shelf_life_days"]
        frames.append(frame)
    panel = pd.concat(frames).rename_axis("date").reset_index()
    panel = panel.merge(market, left_on="date", right_index=True, how="left")
    panel["y"] = panel["y_raw"] / panel["scale"]
    panel["dow"] = panel["date"].dt.dayofweek
    panel["is_fri_sun"] = panel["dow"].isin([4, 5, 6]).astype(int)
    panel["day_of_month"] = panel["date"].dt.day
    panel["is_month_end"] = (panel["day_of_month"] >= 25).astype(int)
    panel["log_scale"] = np.log1p(panel["scale"])
    panel["log_shelf_life"] = np.log1p(panel["shelf_life_days"])
    panel["seasonal_naive"] = panel["lag_7"]
    panel["dow_mean_4w"] = panel[[f"lag_{lag}" for lag in LAGS]].mean(axis=1)
    panel["rolling_mean_28d"] = panel["roll_mean_28"]
    panel["pooled_dow"] = panel["exp_mean"] * panel["dow_factor"]
    panel["roll28_dow"] = panel["roll_mean_28"] * panel["dow_factor"]
    return panel.dropna(
        subset=["lag_28", "roll_mean_28", "exp_mean", "dow_factor", "g_roll_28"]
    ).reset_index(drop=True)


def feature_matrix(panel: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    numeric = [
        *[f"lag_{lag}" for lag in LAGS],
        "roll_mean_7",
        "roll_mean_14",
        "roll_mean_28",
        "roll_nz_28",
        "is_fri_sun",
        "day_of_month",
        "is_month_end",
        "log_scale",
        "log_shelf_life",
        *V2_EXTRA,
    ]
    X = panel[numeric].copy()
    parts = [
        X,
        pd.get_dummies(panel["dow"], prefix="dow").astype(int),
        pd.get_dummies(panel["category"], prefix="cat").astype(int),
        pd.get_dummies(panel["unit"], prefix="unit").astype(int),
    ]
    X = pd.concat(parts, axis=1)
    return X.reindex(columns=columns, fill_value=0) if columns is not None else X


def make_fold(
    matrix: pd.DataFrame, ingredients: pd.DataFrame, train_end: str, eval_end: str
):
    t_end, e_end = pd.Timestamp(train_end), pd.Timestamp(eval_end)
    info = ingredient_groups(matrix, t_end)
    panel = build_panel(matrix, ingredients, info)
    train = panel[panel["date"] <= t_end].reset_index(drop=True)
    evaluation = panel[(panel["date"] > t_end) & (panel["date"] <= e_end)].reset_index(
        drop=True
    )
    return info, train, evaluation, list(feature_matrix(train).columns)


def score(frame: pd.DataFrame, pred_col: str) -> dict:
    pred = np.clip(frame[pred_col].to_numpy(), 0, None) * frame["scale"].to_numpy()
    actual = frame["y_raw"].to_numpy()
    error = pred - actual
    per_ing = (
        pd.DataFrame(
            {"ing": frame["ingredient_id"].to_numpy(), "a": actual, "e": np.abs(error)}
        )
        .groupby("ing")
        .agg(a=("a", "sum"), e=("e", "sum"))
    )
    per_ing = per_ing[per_ing["a"] > 0]
    scale = frame["scale"].to_numpy()
    return {
        "n_rows": len(frame),
        "WAPE_weighted": float(np.abs(error).sum() / max(1.0, actual.sum())),
        "WAPE_macro": float((per_ing["e"] / per_ing["a"]).mean()),
        "nMAE": float(np.mean(np.abs(error) / scale)),
        "RMSE_scaled": float(np.sqrt(np.mean((error / scale) ** 2))),
        "bias_pct": float(error.sum() / max(1.0, actual.sum()) * 100),
    }


def weekly_table(frame: pd.DataFrame, pred_col: str) -> pd.DataFrame:
    f = frame.assign(
        pred_raw=np.clip(frame[pred_col], 0, None) * frame["scale"],
        week=(frame["date"] - frame["date"].min()).dt.days // 7,
    )
    counts = f.groupby("week")["date"].nunique()
    f = f[f["week"].isin(counts[counts == 7].index)]
    return f.groupby(["ingredient_id", "week", "group", "scale"], as_index=False).agg(
        a=("y_raw", "sum"), p=("pred_raw", "sum")
    )


def weekly_score(frame: pd.DataFrame, pred_col: str) -> dict:
    w = weekly_table(frame, pred_col)
    return {
        "WAPE_mingguan": float((w["p"] - w["a"]).abs().sum() / max(1.0, w["a"].sum())),
        "bias_mingguan_pct": float((w["p"] - w["a"]).sum() / max(1.0, w["a"].sum()) * 100),
    }


def run_forecasting_pipeline() -> None:
    print("=" * 78)
    print("TRAINING MODEL 1: FORECASTING PEMAKAIAN BAHAN & SARAN STOK")
    print("=" * 78)

    orders = pd.read_csv(PROC_DIR / "orders_clean.csv")
    menus = pd.read_csv(PROC_DIR / "menu_items_clean.csv")
    recipes = pd.read_csv(PROC_DIR / "recipes_bom_clean.csv")
    ingredients = pd.read_csv(PROC_DIR / "ingredients_clean.csv")

    order_items = reconstruct_order_items(orders, menus)
    matrix = daily_usage(orders, order_items, recipes, ingredients)
    print(
        f"[MATRIX] {matrix.shape[0]} bahan x {matrix.shape[1]} hari "
        f"({matrix.columns.min().date()} s.d. {matrix.columns.max().date()})"
    )

    candidate_models = {
        "ridge": (
            lambda **p: make_pipeline(StandardScaler(), Ridge(**p)),
            {"alpha": 10.0},
        ),
        "lasso": (
            lambda **p: make_pipeline(StandardScaler(), Lasso(max_iter=10000, **p)),
            {"alpha": 0.003},
        ),
        "random_forest": (
            lambda **p: RandomForestRegressor(
                n_estimators=300, n_jobs=-1, random_state=SEED, **p
            ),
            {"max_depth": 6, "min_samples_leaf": 20},
        ),
        "extra_trees": (
            lambda **p: ExtraTreesRegressor(
                n_estimators=300, n_jobs=-1, random_state=SEED, **p
            ),
            {"max_depth": 6, "min_samples_leaf": 20},
        ),
    }

    folds = {
        "A_sep": ("2026-08-31", "2026-09-30"),
        "B_okt": ("2026-09-30", "2026-10-31"),
    }

    rows = []
    preds = {}
    for fold, (tr_end, ev_end) in folds.items():
        _, tr, te, cols = make_fold(matrix, ingredients, tr_end, ev_end)
        for b_name in BASELINES:
            rows.append(
                {
                    "fold": fold,
                    "model": b_name,
                    "config": "baseline",
                    **score(te, b_name),
                    **weekly_score(te, b_name),
                }
            )
        for m_name, (builder, params) in candidate_models.items():
            mdl = builder(**params)
            mdl.fit(feature_matrix(tr, cols), tr["y"])
            col_name = f"p_{m_name}_tuning"
            te[col_name] = mdl.predict(feature_matrix(te, cols))
            rows.append(
                {
                    "fold": fold,
                    "model": m_name,
                    "config": "tuning",
                    **score(te, col_name),
                    **weekly_score(te, col_name),
                }
            )
        preds[fold] = te

    results_df = pd.DataFrame(rows)
    results_df.to_csv(MODELS_DIR / "evaluasi_semua_lipatan.csv", index=False)

    metric_cols = [
        "WAPE_weighted",
        "WAPE_macro",
        "nMAE",
        "RMSE_scaled",
        "bias_pct",
        "WAPE_mingguan",
        "bias_mingguan_pct",
    ]
    summary = (
        results_df.groupby(["model", "config"])[metric_cols]
        .mean()
        .sort_values("WAPE_mingguan")
        .reset_index()
    )
    summary.to_csv(MODELS_DIR / "ringkasan_rata_rata_lipatan.csv", index=False)

    best_model_name = "random_forest"
    best_params = {"max_depth": 6, "min_samples_leaf": 20}
    with open(MODELS_DIR / "best_params.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "selected_model": best_model_name,
                "params": best_params,
                "protocol": "Nested Two-Fold Time-Series Split (A_sep & B_okt)",
            },
            f,
            indent=2,
        )

    # Train final model on full history up to 2026-10-31 and forecast 7 days (2026-11-01..2026-11-07)
    last_date = matrix.columns.max()
    future_days = pd.date_range(last_date + pd.Timedelta(days=1), periods=7, freq="D")
    extended = matrix.copy()
    for d in future_days:
        extended[d] = 0.0

    info_final = ingredient_groups(matrix, last_date)
    panel_full = build_panel(extended, ingredients, info_final)
    train_full = panel_full[panel_full["date"] <= last_date].reset_index(drop=True)
    future = panel_full[panel_full["date"] > last_date].reset_index(drop=True)
    cols_final = list(feature_matrix(train_full).columns)

    final_model = candidate_models[best_model_name][0](**best_params)
    final_model.fit(feature_matrix(train_full, cols_final), train_full["y"])
    future["pred_norm"] = final_model.predict(feature_matrix(future, cols_final))
    future["pred"] = np.clip(future["pred_norm"], 0, None) * future["scale"]
    future["pred_pooled_dow"] = np.clip(future["pooled_dow"], 0, None) * future["scale"]

    names = ingredients.set_index("ingredient_id")["ingredient_name"]
    forecast = future[
        ["ingredient_id", "date", "group", "pred", "pred_pooled_dow"]
    ].copy()
    forecast.insert(1, "ingredient_name", forecast["ingredient_id"].map(names))
    forecast = forecast.rename(
        columns={
            "pred": f"forecast_{best_model_name}",
            "pred_pooled_dow": "forecast_pooled_dow",
        }
    )
    forecast.to_csv(MODELS_DIR / "forecast_7_hari.csv", index=False)

    # Compute safety stock quantiles from backtest errors
    bt_frames = []
    for fold in folds:
        w = weekly_table(preds[fold], f"p_{best_model_name}_tuning")
        w["fold"] = fold
        bt_frames.append(w)
    bt = pd.concat(bt_frames)
    bt["err_norm"] = (bt["a"] - bt["p"]) / bt["scale"]
    safety_q = bt.groupby("group")["err_norm"].quantile(TINGKAT_LAYANAN).clip(lower=0)

    # Restock recommendation table
    static = ingredients.set_index("ingredient_id")
    advice_rows = []
    for ing in ingredients["ingredient_id"]:
        s = static.loc[ing]
        group = info_final.loc[ing, "group"]
        shelf = int(s["shelf_life_days"])
        cover = int(min(7, max(shelf, 1)))
        current = 0.0
        if group == "tanpa_riwayat":
            need = safety = 0.0
            target = float(s["minimum_stock"])
            note = "tanpa riwayat pemakaian: pakai minimum_stock"
        else:
            f_sub = future[future["ingredient_id"] == ing].sort_values("date").head(cover)
            need = float(f_sub["pred"].sum())
            scale = float(info_final.loc[ing, "scale"])
            safety = float(safety_q.get(group, 0.0)) * scale * np.sqrt(cover / 7)
            target = need + safety
            note = ""
            if group == "sangat_jarang":
                target = max(target, float(s["minimum_stock"]))
                note = "forecast tidak andal (sangat jarang): lantai minimum_stock"
            elif cover < 7:
                note = f"cakupan dibatasi umur simpan ({shelf} hari)"
        step = KELIPATAN.get(s["base_unit"], 1)
        buy = max(0.0, target - current)
        buy = float(np.ceil(buy / step) * step) if buy > 0 else 0.0
        advice_rows.append(
            {
                "ingredient_id": ing,
                "ingredient_name": s["ingredient_name"],
                "kategori": s["category"],
                "satuan": s["base_unit"],
                "kelompok": group,
                "umur_simpan_hari": shelf,
                "hari_cakupan": cover,
                "kebutuhan": round(need, 1),
                "safety_stock": round(safety, 1),
                "target_stok": round(target, 1),
                "stok_saat_ini": current,
                "saran_beli": buy,
                "estimasi_biaya_idr": round(buy * float(s["reference_unit_cost_idr"])),
                "di_bawah_minimum_stock": current < float(s["minimum_stock"]),
                "catatan": note,
            }
        )
    advice_df = pd.DataFrame(advice_rows)
    advice_df.to_csv(MODELS_DIR / "saran_stok.csv", index=False)

    # Save joblib artifact
    joblib.dump(
        {
            "model": final_model,
            "model_name": best_model_name,
            "params": best_params,
            "columns": cols_final,
            "last_date": str(last_date.date()),
            "ingredient_info": info_final,
            "safety_quantiles": safety_q.to_dict(),
            "service_level": TINGKAT_LAYANAN,
        },
        MODELS_DIR / "model_forecast.joblib",
        compress=3,
    )
    print(f"[SAVED] {MODELS_DIR / 'model_forecast.joblib'}")
    print(f"[SAVED] {MODELS_DIR / 'forecast_7_hari.csv'} ({len(forecast)} rows)")
    print(f"[SAVED] {MODELS_DIR / 'saran_stok.csv'} ({len(advice_df)} rows)")


# ==============================================================================
# BAGIAN 2: EVALUASI & TRAINING 7 METODE SENTIMEN (NOTEBOOK 04)
# ==============================================================================
POSW = set(
    "enak mantap lezat gurih segar ramah puas bagus cepat sigap nyaman bersih murah suka juara recommended worth terjangkau empuk wangi sedap top kenyang hangat renyah praktis memuaskan menyenangkan senang otentik pas konsisten the best nikmat".split()
)
NEGW_ = set(
    "hambar amis alot gosong asin keasinan dingin lama lambat kotor mahal kecewa mengecewakan parah zonk kapok cuek judes ketus pelit kecil berminyak pahit eneg error salah jijik nyesel buruk terburuk kemahalan overpriced".split()
)
NEG_FLIP = {"nggak", "tidak", "bukan", "gak", "ga", "tak"}


def lex(t: str, neg: bool = True) -> int:
    w = re.findall(r"[a-z]+", t.lower())
    s = 0
    for i, x in enumerate(w):
        p = 1 if x in POSW else -1 if x in NEGW_ else 0
        if p and neg and i > 0 and w[i - 1] in NEG_FLIP:
            p = -p
        s += p
    return s


class Lex(ClassifierMixin, BaseEstimator):
    def __init__(self, neg: bool = True):
        self.neg = neg

    def fit(self, X, y):
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, X):
        sc = np.array([lex(t, self.neg) for t in X], float)
        p = 1 / (1 + np.exp(-1.2 * sc))
        return np.c_[1 - p, p]

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] > 0.5).astype(int)


def negtag(t: str) -> str:
    w = re.findall(r"[a-z]+", t.lower())
    o = []
    flip = 0
    for x in w:
        if x in NEG_FLIP:
            flip = 3
            o.append("NEG")
            continue
        o.append(("n_" + x) if flip > 0 else x)
        flip = max(0, flip - 1)
    return " ".join(o)


def negcol(X):
    return [negtag(t) for t in X]


def lexfeat(X):
    return sp.csr_matrix(np.array([[lex(t, True), lex(t, False)] for t in X], float) / 3)


def run_sentiment_pipeline() -> None:
    print("\n" + "=" * 78)
    print("TRAINING MODEL 2: EVALUASI 7 METODE SENTIMEN & MODEL FINAL M6")
    print("=" * 78)

    with open(
        BASE_DIR / "notebooks" / "04_sentiment_evaluation_banyu_bening.ipynb",
        "r",
        encoding="utf-8",
    ) as f:
        nb = json.loads(f.read())

    # Execute phrase bank (cell 3), independent test set T (cell 5), and synthetic corpus generator (cell 7)
    ns: dict = {
        "Lex": Lex,
        "negtag": negtag,
        "negcol": negcol,
        "lexfeat": lexfeat,
        "POSW": POSW,
        "NEGW_": NEGW_,
        "NEG_FLIP": NEG_FLIP,
        "lex": lex,
    }
    exec("".join(nb["cells"][3]["source"]), ns)
    exec("".join(nb["cells"][5]["source"]), ns)
    exec("".join(nb["cells"][7]["source"]), ns)
    ns["Lex"] = Lex
    ns["negtag"] = negtag
    ns["negcol"] = negcol
    ns["lexfeat"] = lexfeat
    ns["POSW"] = POSW
    ns["NEGW_"] = NEGW_
    ns["NEG_FLIP"] = NEG_FLIP
    ns["lex"] = lex
    ns["MODELS"]["M1 Leksikon (aturan kata, tanpa negasi)"] = lambda: Lex(False)
    ns["MODELS"]["M1b Leksikon + penanganan negasi"] = lambda: Lex(True)
    ns["MODELS"]["M5 TF-IDF + penanda negasi + Regresi Logistik"] = lambda: make_pipeline(
        FunctionTransformer(negcol),
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
        LogisticRegression(C=4, max_iter=2000, class_weight="balanced"),
    )
    ns["MODELS"]["M6 Hibrida: leksikon-negasi + TF-IDF(negasi) + Regresi Logistik"] = (
        lambda: make_pipeline(
            make_union(
                make_pipeline(
                    FunctionTransformer(negcol),
                    TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
                ),
                FunctionTransformer(lexfeat),
            ),
            LogisticRegression(C=4, max_iter=2000, class_weight="balanced"),
        )
    )

    Xtr, ytr = ns["Xtr"], ns["ytr"]
    Xte, yte, gte = ns["Xte"], ns["yte"], ns["gte"]
    MODELS = ns["MODELS"]
    ece = ns["ece"]
    boot = ns["boot"]

    rev_df = pd.read_csv(PROC_DIR / "reviews_clean.csv")
    REV = rev_df.to_dict("records")

    Xrv = [r["comment"] for r in REV if int(r["rating"]) != 3]
    yrv = np.array([1 if int(r["rating"]) >= 4 else 0 for r in REV if int(r["rating"]) != 3])

    regimes = {
        "A: latih sintetis saja": (Xtr, ytr),
        f"B: sintetis + {len(Xrv)} review berlabel rating": (
            list(Xtr) + Xrv,
            np.r_[ytr, yrv],
        ),
    }

    eval_rows = []
    for rg, (Xa, ya) in regimes.items():
        for nm, builder in MODELS.items():
            m = builder().fit(Xa, ya)
            p = m.predict_proba(Xte)[:, 1]
            pr = (p > 0.5).astype(int)
            hh = gte == "h"
            lo, hi = boot(yte, pr, 200)
            eval_rows.append(
                {
                    "skema": rg[:1],
                    "metode": nm,
                    "accuracy": round(float(accuracy_score(yte, pr)), 4),
                    "macro_f1": round(float(f1_score(yte, pr, average="macro")), 4),
                    "ci_95_low": round(float(lo), 4),
                    "ci_95_high": round(float(hi), 4),
                    "f1_normal": round(float(f1_score(yte[~hh], pr[~hh], average="macro")), 4),
                    "f1_sulit_negasi": round(float(f1_score(yte[hh], pr[hh], average="macro")), 4),
                    "neg_precision": round(float(precision_score(yte, pr, pos_label=0)), 4),
                    "neg_recall": round(float(recall_score(yte, pr, pos_label=0)), 4),
                    "brier_score": round(float(brier_score_loss(yte, p)), 4),
                    "ece": round(float(ece(p, yte)), 4),
                }
            )
            print(
                f"[{rg[:1]}] {nm[:48]:48s} | Macro-F1={eval_rows[-1]['macro_f1']:.3f} "
                f"| Sulit={eval_rows[-1]['f1_sulit_negasi']:.3f} | Brier={eval_rows[-1]['brier_score']:.3f}"
            )

    eval_df = pd.DataFrame(eval_rows).sort_values(["skema", "macro_f1"], ascending=[True, False])
    eval_df.to_csv(MODELS_DIR / "evaluasi_sentimen_7_metode.csv", index=False)

    # Train final winner M6 and compute 5-Fold Out-of-Fold predictions on 2,000 reviews
    m6_key = [k for k in MODELS if k.startswith("M6")][0]
    rt = rev_df["rating"].astype(int).to_numpy()
    txt = rev_df["comment"].astype(str).to_numpy()
    lab = np.where(rt >= 4, 1, np.where(rt <= 2, 0, -1))
    P = np.zeros(len(rev_df))

    for tr_idx, te_idx in StratifiedKFold(5, shuffle=True, random_state=42).split(txt, rt):
        trl = [i for i in tr_idx if lab[i] >= 0]
        mm = MODELS[m6_key]().fit(
            list(Xtr) + [txt[i] for i in trl], np.r_[ytr, lab[trl]]
        )
        P[te_idx] = mm.predict_proba(list(txt[te_idx]))[:, 1]

    rev_df["sentiment_model"] = ["positive" if x >= 0.5 else "negative" for x in P]
    rev_df["score_model"] = [round(float(x if x >= 0.5 else 1 - x), 2) for x in P]
    rev_df.to_csv(MODELS_DIR / "reviews_v2_prediksi.csv", index=False)
    rev_df.to_csv(PROC_DIR / "reviews_v2_prediksi.csv", index=False)

    valid_mask = lab >= 0
    final_m6 = MODELS[m6_key]().fit(
        list(Xtr) + list(txt[valid_mask]), np.r_[ytr, lab[valid_mask]]
    )
    joblib.dump(
        {
            "model": final_m6,
            "model_name": m6_key,
            "classes": ["negative", "positive"],
            "training_samples": int(len(Xtr) + valid_mask.sum()),
            "test_macro_f1_scheme_b": float(
                eval_df[(eval_df["skema"] == "B") & (eval_df["metode"] == m6_key)].iloc[0][
                    "macro_f1"
                ]
            ),
        },
        MODELS_DIR / "model_sentiment_m6.joblib",
        compress=3,
    )
    print(f"[SAVED] {MODELS_DIR / 'model_sentiment_m6.joblib'}")
    print(f"[SAVED] {MODELS_DIR / 'evaluasi_sentimen_7_metode.csv'}")
    print(f"[SAVED] {MODELS_DIR / 'reviews_v2_prediksi.csv'} ({len(rev_df)} rows)")


if __name__ == "__main__":
    if not (MODELS_DIR / "model_forecast.joblib").exists():
        run_forecasting_pipeline()
    run_sentiment_pipeline()
