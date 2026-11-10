import os
import math
import numpy as np
import pandas as pd
import scipy.special
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, f1_score, precision_score, recall_score, roc_curve
import matplotlib.pyplot as plt
import joblib

# -------------------------------------------------------------------------
# CONSTANTS & PATHS
# -------------------------------------------------------------------------
EXCEL_PATH = "BCTC_Tu_Dong_Vnstock.xlsx"
ARTIFACT_DIR = "/Users/tungnguyen/.gemini/antigravity/brain/874901a3-2634-40af-9b0d-5d01ef46a6cc"
MODEL_PATH = "best_ews_model.joblib"

# -------------------------------------------------------------------------
# 1. LOAD & PREPARE DATA
# -------------------------------------------------------------------------
print("Loading excel file...")
df_raw = pd.read_excel(EXCEL_PATH, sheet_name="Data_Entry")
print(f"Loaded {len(df_raw)} rows.")

# Map columns
col_mapping = {
    'Mã chứng khoán': 'symbol',
    'Năm tài chính': 'year',
    'Độ tuổi DN': 'age',
    'Có niêm yết?': 'is_listed',
    'Phát hành CK?': 'issue',
    'Nhãn thao túng\n(Fraud)': 'label',
    'Current_Assets\n[100]': 'ca',
    'Cash_Equivalents\n[110]': 'cash',
    'Accounts_Receivable\n[131]': 'rec',
    'Inventories\n[140]': 'inv',
    'Fixed_Assets\n[220]': 'fa',
    'Total_Assets\n[270]': 'ta',
    'Total_Liabilities\n[300]': 'liab',
    'Current_Liabilities\n[310]': 'cl',
    'Equity\n[400]': 'eq',
    'Retained_Earnings\n[421]': 're',
    'Net_Sales\n[10]': 'sales',
    'COGS\n[11]': 'cogs',
    'Interest_Expense\n[23]': 'interest',
    'Selling_Expense\n[25]': 'selling_expense',
    'GA_Expense\n[26]': 'ga_expense',
    'EBT\n[50]': 'ebt',
    'Net_Income\n[60]': 'ni',
    'OCF\n[20 LCTT]': 'ocf'
}

# Rename columns
df = df_raw.rename(columns=col_mapping)[list(col_mapping.values())].copy()

# Sort to calculate lags correctly
df = df.sort_values(by=['symbol', 'year']).reset_index(drop=True)

# -------------------------------------------------------------------------
# 2. FEATURE ENGINEERING (Calculate 10 EWS Metrics & Subcomponents)
# -------------------------------------------------------------------------
print("Calculating EWS metrics & subcomponents...")

# 1. Altman Z'-Score
df['x1'] = ((df['ca'] - df['cl']) / df['ta']).fillna(0)
df['x2'] = (df['re'] / df['ta']).fillna(0)
df['x3'] = ((df['ebt'] + df['interest']) / df['ta']).fillna(0)
df['x4'] = (df['eq'] / df['liab']).fillna(0)
df['x5'] = (df['sales'] / df['ta']).fillna(0)
df['z_prime'] = 0.717 * df['x1'] + 0.847 * df['x2'] + 3.107 * df['x3'] + 0.420 * df['x4'] + 0.998 * df['x5']

# 2. SA Index
df['ta_usd_m'] = (df['ta'] / 25000.0) / 1000000.0
df['size'] = np.log(df['ta_usd_m'].clip(lower=1e-3))
df['size'] = df['size'].clip(upper=np.log(4500.0))
df['capped_age'] = df['age'].clip(upper=37.0)
df['sa_idx'] = -0.737 * df['size'] + 0.043 * (df['size'] ** 2) - 0.040 * df['capped_age']

# Lags (t-1)
df['prev_ta'] = df.groupby('symbol')['ta'].shift(1)
df['prev_ca'] = df.groupby('symbol')['ca'].shift(1)
df['prev_cl'] = df.groupby('symbol')['cl'].shift(1)
df['prev_rec'] = df.groupby('symbol')['rec'].shift(1)
df['prev_inv'] = df.groupby('symbol')['inv'].shift(1)
df['prev_fa'] = df.groupby('symbol')['fa'].shift(1)
df['prev_liab'] = df.groupby('symbol')['liab'].shift(1)
df['prev_sales'] = df.groupby('symbol')['sales'].shift(1)
df['prev_cogs'] = df.groupby('symbol')['cogs'].shift(1)
df['prev_cash'] = df.groupby('symbol')['cash'].shift(1)
df['prev_ni'] = df.groupby('symbol')['ni'].shift(1)
df['sga'] = df['selling_expense'] + df['ga_expense']
df['prev_sga'] = df.groupby('symbol')['sga'].shift(1)

# Lags (t-2)
df['prev_2_rec'] = df.groupby('symbol')['rec'].shift(2)
df['prev_2_sales'] = df.groupby('symbol')['sales'].shift(2)

# 3. Beneish M-Score
df['rec_sales_ratio'] = (df['rec'] / df['sales']).fillna(0)
df['prev_rec_sales_ratio'] = (df['prev_rec'] / df['prev_sales']).fillna(0)
df['dsri'] = (df['rec_sales_ratio'] / df['prev_rec_sales_ratio']).fillna(1.0)
df['dsri'] = df['dsri'].replace([np.inf, -np.inf], 1.0)

df['gp_margin'] = ((df['sales'] - df['cogs']) / df['sales']).fillna(0)
df['prev_gp_margin'] = ((df['prev_sales'] - df['prev_cogs']) / df['prev_sales']).fillna(0)
df['gmi'] = (df['prev_gp_margin'] / df['gp_margin']).fillna(1.0)
df['gmi'] = df['gmi'].replace([np.inf, -np.inf], 1.0)

df['aq_t'] = 1.0 - ((df['ca'] + df['fa']) / df['ta']).fillna(0)
df['aq_t1'] = 1.0 - ((df['prev_ca'] + df['prev_fa']) / df['prev_ta']).fillna(0)
df['aqi'] = (df['aq_t'] / df['aq_t1']).fillna(1.0)
df['aqi'] = df['aqi'].replace([np.inf, -np.inf], 1.0)

df['sgi'] = (df['sales'] / df['prev_sales']).fillna(1.0)
df['sgi'] = df['sgi'].replace([np.inf, -np.inf], 1.0)

df['depi'] = 1.0 # as in fintrust_app.py

df['sga_sales_ratio'] = (df['sga'] / df['sales']).fillna(0)
df['prev_sga_sales_ratio'] = (df['prev_sga'] / df['prev_sales']).fillna(0)
df['sgai'] = (df['sga_sales_ratio'] / df['prev_sga_sales_ratio']).fillna(1.0)
df['sgai'] = df['sgai'].replace([np.inf, -np.inf], 1.0)

df['lvg'] = (df['liab'] / df['ta']).fillna(0)
df['prev_lvg'] = (df['prev_liab'] / df['prev_ta']).fillna(0)
df['lvgi'] = (df['lvg'] / df['prev_lvg']).fillna(1.0)
df['lvgi'] = df['lvgi'].replace([np.inf, -np.inf], 1.0)

df['tata'] = ((df['ni'] - df['ocf']) / df['ta']).fillna(0)

df['m_score'] = -4.84 + 0.920*df['dsri'] + 0.528*df['gmi'] + 0.404*df['aqi'] + 0.892*df['sgi'] + 0.115*df['depi'] - 0.172*df['sgai'] + 4.679*df['tata'] - 0.327*df['lvgi']

# 4. Beneish M-Score Probit (12-variable)
df['pos_accruals'] = (df['tata'] > 0).astype(float)
df['dec_cash'] = ((df['sgi'] < 1.0) & (df['ocf'] < df['ni'])).astype(float)
df['issue_sec'] = df['issue'].astype(float)
df['ab_return'] = 0.0 # baseline

df['z_12'] = -3.5 + 0.920*df['dsri'] + 0.528*df['gmi'] + 0.404*df['aqi'] + 0.892*df['sgi'] + 0.115*df['depi'] - 0.172*df['sgai'] + 4.679*df['tata'] - 0.327*df['lvgi'] - 0.320*df['ab_return'] + 0.35*df['pos_accruals'] + 0.25*df['dec_cash'] + 0.40*df['issue_sec']
df['p_12'] = 0.5 * (1.0 + scipy.special.erf(df['z_12'] / np.sqrt(2.0)))

# 5. Dechow F-Score
df['wc_t'] = df['ca'] - df['cash'] - df['cl']
df['wc_prev'] = df['prev_ca'] - df['prev_cash'] - df['prev_cl']
df['nco_t'] = (df['ta'] - df['ca'] - df['fa']) - (df['liab'] - df['cl'])
df['nco_prev'] = (df['prev_ta'] - df['prev_ca'] - df['prev_fa']) - (df['prev_liab'] - df['prev_cl'])
df['fin_t'] = df['cash'] - (df['liab'] - df['cl'])
df['fin_prev'] = df['prev_cash'] - (df['prev_liab'] - df['prev_cl'])

df['average_ta'] = 0.5 * (df['ta'] + df['prev_ta'])
df['rsst_acc'] = (((df['wc_t'] - df['wc_prev']) + (df['nco_t'] - df['nco_prev']) + (df['fin_t'] - df['fin_prev'])) / df['average_ta']).fillna(0)
df['ch_rec'] = ((df['rec'] - df['prev_rec']) / df['average_ta']).fillna(0)
df['ch_inv'] = ((df['inv'] - df['prev_inv']) / df['average_ta']).fillna(0)
df['soft_assets'] = ((df['ta'] - df['fa'] - df['cash']) / df['ta']).fillna(0)

df['cash_sales_t'] = df['sales'] - (df['rec'] - df['prev_rec'])
df['rec_prev_2_val'] = df['prev_2_rec'].fillna(df['prev_rec'])
df['cash_sales_prev'] = df['prev_sales'] - (df['prev_rec'] - df['rec_prev_2_val'])
df['ch_cs'] = ((df['cash_sales_t'] - df['cash_sales_prev']) / df['cash_sales_prev']).fillna(0)
df['ch_cs'] = df['ch_cs'].replace([np.inf, -np.inf], 0)

df['roa_t'] = (df['ni'] / df['ta']).fillna(0)
df['roa_prev'] = (df['prev_ni'] / df['prev_ta']).fillna(0)
df['ch_roa'] = df['roa_t'] - df['roa_prev']

df['pred_val'] = -7.893 + 0.790*df['rsst_acc'] + 2.518*df['ch_rec'] + 1.191*df['ch_inv'] + 1.979*df['soft_assets'] + 0.171*df['ch_cs'] - 0.932*df['ch_roa'] + 1.029*df['issue_sec']
df['p_dechow'] = np.exp(df['pred_val']) / (1.0 + np.exp(df['pred_val']))
df['f_score'] = (df['p_dechow'] / 0.0037).fillna(0.0)

# 6. Abnormal CFO (Ab_CFO)
df['actual_cfo_ratio'] = (df['ocf'] / df['prev_ta']).fillna(0)
df['normal_cfo_ratio'] = -0.01 * (1.0 / df['prev_ta']) + 0.09 * (df['sales'] / df['prev_ta']) - 0.02 * ((df['sales'] - df['prev_sales']) / df['prev_ta'])
df['ab_cfo'] = df['actual_cfo_ratio'] - df['normal_cfo_ratio']

# 7. Abnormal Production (Ab_PROD)
df['inv_diff'] = df['inv'] - df['prev_inv']
df['prod'] = df['cogs'] + df['inv_diff']
df['actual_prod_ratio'] = (df['prod'] / df['prev_ta']).fillna(0)

df['sales_prev_2_val'] = df['prev_2_sales'].fillna(df['prev_sales'])
df['lag_delta_sales'] = df['prev_sales'] - df['sales_prev_2_val']
df['lag_delta_sales'] = df['lag_delta_sales'].fillna(df['sales'] - df['prev_sales'])

df['normal_prod_ratio'] = 0.03 * (1.0 / df['prev_ta']) + 0.82 * (df['sales'] / df['prev_ta']) + 0.12 * ((df['sales'] - df['prev_sales']) / df['prev_ta']) - 0.05 * (df['lag_delta_sales'] / df['prev_ta'])
df['ab_prod'] = df['actual_prod_ratio'] - df['normal_prod_ratio']

# 8. Abnormal Discretionary Expenses (Ab_DISEXP)
df['actual_disexp_ratio'] = (df['sga'] / df['prev_ta']).fillna(0)
df['normal_disexp_ratio'] = 0.01 * (1.0 / df['prev_ta']) + 0.06 * (df['prev_sales'] / df['prev_ta'])
df['ab_disexp'] = df['actual_disexp_ratio'] - df['normal_disexp_ratio']

# 9. KZ Index
df['k_val'] = df['prev_fa'].apply(lambda x: x if x > 0 else np.nan).fillna(df['prev_ta'])
df['cf_val'] = df['ni'] + 0.05 * df['fa'].clip(lower=0)
df['debt_val'] = df['liab']
df['div_val'] = 0.0 * df['ni'] 
df['cash_val'] = df['cash']
df['kz_score'] = -1.002 * (df['cf_val'] / df['k_val']) + 0.283 * 1.2 + 3.139 * (df['debt_val'] / df['k_val']) - 39.368 * (df['div_val'] / df['k_val']) - 1.315 * (df['cash_val'] / df['k_val'])

# 10. WW Index
df['cf_ww'] = (df['cf_val'] / df['ta']).fillna(0)
df['divpos_val'] = (df['div_val'] > 0).astype(float)
df['tltd_val'] = ((df['liab'] - df['cl']) / df['ta']).fillna(0)
df['lnta_val'] = np.log((df['ta'] / 25000.0 / 1e6).clip(lower=1e-3))
df['sg_val'] = (df['sales'] / df['prev_sales']).fillna(1.0) - 1.0
df['ww_score'] = -0.091 * df['cf_ww'] - 0.062 * df['divpos_val'] + 0.021 * df['tltd_val'] - 0.044 * df['lnta_val'] + 0.102 * 0.08 - 0.035 * df['sg_val']

# -------------------------------------------------------------------------
# 3. FILTER CLEAN DATASET
# -------------------------------------------------------------------------
print("Filtering valid records for training (removing first year without lags)...")
# Keep records where prev_ta is not null (this drops year 2022 / first year of history)
df_clean = df.dropna(subset=['prev_ta']).copy()

# Features list
features = [
    # EWS Scores
    'z_prime', 'sa_idx', 'm_score', 'p_12', 'f_score', 'ab_cfo', 'ab_prod', 'ab_disexp', 'kz_score', 'ww_score',
    # Model Components & Ratios
    'x1', 'x2', 'x3', 'x4', 'x5', 
    'dsri', 'gmi', 'aqi', 'sgi', 'sgai', 'lvgi', 'tata', 
    'pos_accruals', 'dec_cash', 'rsst_acc', 'ch_rec', 'ch_inv', 'soft_assets', 'ch_cs', 'ch_roa',
    'actual_cfo_ratio', 'actual_prod_ratio', 'actual_disexp_ratio',
    'size', 'capped_age',
    # Context
    'is_listed', 'issue'
]

# Prepare X, y
X = df_clean[features].copy()
y = df_clean['label'].copy()

# Handle inf and nan in features
X = X.replace([np.inf, -np.inf], np.nan)
X = X.fillna(0.0)

print(f"Training dataset size: {len(X)} rows.")
print(f"Class distribution: {np.bincount(y)}")

# -------------------------------------------------------------------------
# 4. TRAIN AND EVALUATE WITH CROSS-VALIDATION
# -------------------------------------------------------------------------
print("Starting Stratified 5-Fold Cross Validation...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

models_to_test = {
    "Logistic Regression": LogisticRegression(class_weight='balanced', max_iter=2000, random_state=42),
    "Random Forest": RandomForestClassifier(class_weight='balanced', n_estimators=200, max_depth=10, random_state=42),
    "XGBoost": xgb.XGBClassifier(
        scale_pos_weight=(len(y) - sum(y)) / sum(y),
        n_estimators=150,
        max_depth=5,
        learning_rate=0.05,
        random_state=42,
        eval_metric='logloss'
    )
}

results = {name: {"roc_auc": [], "pr_auc": [], "f1": [], "precision": [], "recall": []} for name in models_to_test}

# We'll save the fold predictions to plot curves
plot_data = {name: {"y_true": [], "y_prob": []} for name in models_to_test}

for fold, (train_idx, val_idx) in enumerate(cv.split(X, y)):
    print(f"--- Fold {fold+1} ---")
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    for name, model in models_to_test.items():
        if name == "XGBoost":
            model.fit(X_train, y_train)
            probs = model.predict_proba(X_val)[:, 1]
            preds = model.predict(X_val)
        else:
            model.fit(X_train_scaled, y_train)
            probs = model.predict_proba(X_val_scaled)[:, 1]
            preds = model.predict(X_val_scaled)
            
        # Calculate metrics
        roc_auc = roc_auc_score(y_val, probs)
        precision_arr, recall_arr, _ = precision_recall_curve(y_val, probs)
        pr_auc = auc(recall_arr, precision_arr)
        f1 = f1_score(y_val, preds)
        prec = precision_score(y_val, preds, zero_division=0)
        rec = recall_score(y_val, preds)
        
        results[name]["roc_auc"].append(roc_auc)
        results[name]["pr_auc"].append(pr_auc)
        results[name]["f1"].append(f1)
        results[name]["precision"].append(prec)
        results[name]["recall"].append(rec)
        
        plot_data[name]["y_true"].extend(y_val.tolist())
        plot_data[name]["y_prob"].extend(probs.tolist())

# -------------------------------------------------------------------------
# 5. PRINT RESULTS
# -------------------------------------------------------------------------
print("\n================== RESULTS SUMMARY ==================")
best_f1 = -1.0
best_model_name = ""

for name in models_to_test:
    mean_roc = np.mean(results[name]["roc_auc"])
    mean_pr = np.mean(results[name]["pr_auc"])
    mean_f1 = np.mean(results[name]["f1"])
    mean_prec = np.mean(results[name]["precision"])
    mean_rec = np.mean(results[name]["recall"])
    
    print(f"\nModel: {name}")
    print(f"  ROC-AUC:   {mean_roc:.4f}")
    print(f"  PR-AUC:    {mean_pr:.4f}")
    print(f"  F1-Score:  {mean_f1:.4f}")
    print(f"  Precision: {mean_prec:.4f}")
    print(f"  Recall:    {mean_rec:.4f}")
    
    if mean_f1 > best_f1:
        best_f1 = mean_f1
        best_model_name = name

print(f"\nBest Model by F1-Score: {best_model_name}")

# -------------------------------------------------------------------------
# 6. TRAIN FINAL BEST MODEL & SAVE
# -------------------------------------------------------------------------
print(f"\nTraining final {best_model_name} model on full dataset...")
final_scaler = StandardScaler()
X_scaled = final_scaler.fit_transform(X)

if best_model_name == "XGBoost":
    final_model = xgb.XGBClassifier(
        scale_pos_weight=(len(y) - sum(y)) / sum(y),
        n_estimators=150,
        max_depth=5,
        learning_rate=0.05,
        random_state=42,
        eval_metric='logloss'
    )
    final_model.fit(X, y)
elif best_model_name == "Random Forest":
    final_model = RandomForestClassifier(class_weight='balanced', n_estimators=200, max_depth=10, random_state=42)
    final_model.fit(X_scaled, y)
else:
    final_model = LogisticRegression(class_weight='balanced', max_iter=2000, random_state=42)
    final_model.fit(X_scaled, y)

# Save model and scaler
joblib.dump({"model": final_model, "scaler": final_scaler, "features": features}, MODEL_PATH)
print(f"Saved best model package to: {MODEL_PATH}")

# -------------------------------------------------------------------------
# 7. GENERATE EVALUATION PLOTS
# -------------------------------------------------------------------------
print("Generating and saving evaluation plots...")
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# 1. ROC Curves
plt.figure(figsize=(8, 6))
for name in models_to_test:
    fpr, tpr, _ = roc_curve(plot_data[name]["y_true"], plot_data[name]["y_prob"])
    mean_auc = roc_auc_score(plot_data[name]["y_true"], plot_data[name]["y_prob"])
    plt.plot(fpr, tpr, label=f"{name} (AUC = {mean_auc:.3f})")
plt.plot([0, 1], [0, 1], 'k--', label="Random Guess")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curves Comparison")
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(ARTIFACT_DIR, "roc_curve.png"), dpi=300, bbox_inches='tight')
plt.close()

# 2. Precision-Recall Curves
plt.figure(figsize=(8, 6))
for name in models_to_test:
    precision, recall, _ = precision_recall_curve(plot_data[name]["y_true"], plot_data[name]["y_prob"])
    mean_pr_auc = auc(recall, precision)
    plt.plot(recall, precision, label=f"{name} (PR-AUC = {mean_pr_auc:.3f})")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curves Comparison")
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(ARTIFACT_DIR, "pr_curve.png"), dpi=300, bbox_inches='tight')
plt.close()

# 3. Feature Importance
if best_model_name in ["XGBoost", "Random Forest"]:
    importances = final_model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    top_n = min(15, len(features))
    plt.figure(figsize=(10, 6))
    plt.title(f"Top {top_n} Feature Importances ({best_model_name})")
    plt.bar(range(top_n), importances[indices[:top_n]], align="center")
    plt.xticks(range(top_n), [features[i] for i in indices[:top_n]], rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(axis='y')
    plt.savefig(os.path.join(ARTIFACT_DIR, "feature_importance.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("Feature importance plot generated successfully.")
else:
    coefficients = final_model.coef_[0]
    indices = np.argsort(np.abs(coefficients))[::-1]
    
    top_n = min(15, len(features))
    plt.figure(figsize=(10, 6))
    plt.title(f"Top {top_n} Feature Coefficients (Logistic Regression)")
    plt.bar(range(top_n), coefficients[indices[:top_n]], align="center")
    plt.xticks(range(top_n), [features[i] for i in indices[:top_n]], rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(axis='y')
    plt.savefig(os.path.join(ARTIFACT_DIR, "feature_importance.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("Feature coefficient plot generated successfully.")

print("All plots saved successfully in the artifact directory.")
