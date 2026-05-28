"""
AN6105 Causal Inference - Graded Individual Assignment
Part A: Causal Inference on Diabetes
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

# ─────────────────────────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────────────────────────
df = pd.read_csv('/home/user/2025-AN6001B/diabetes_data.csv')
print("=" * 70)
print("DATASET OVERVIEW")
print("=" * 70)
print(f"Shape: {df.shape}")
print(f"\nColumn names:\n{list(df.columns)}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nMissing values:\n{df.isnull().sum().sum()} total missing")

# ─────────────────────────────────────────────────────────────────────────────
# Q1: DATA EXPLORATION – THREE KEY FINDINGS
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("Q1: DATA EXPLORATION")
print("=" * 70)

print("\n--- Descriptive Statistics ---")
print(df.describe().round(3))

print("\n--- Diabetes Prevalence ---")
print(df['Diabetes'].value_counts())
print(f"Diabetes rate: {df['Diabetes'].mean():.1%}")

# Key Finding 1: Risk factor prevalence comparison
print("\n--- FINDING 1: Risk Factor Prevalence by Diabetes Status ---")
risk_factors = ['HighBP', 'HighChol', 'Smoker', 'Stroke',
                'HeartDiseaseorAttack', 'PhysActivity', 'DiffWalk']
for col in risk_factors:
    no_diab = df.loc[df['Diabetes'] == 0, col].mean()
    yes_diab = df.loc[df['Diabetes'] == 1, col].mean()
    print(f"  {col:25s}  No Diabetes: {no_diab:.1%}   Diabetes: {yes_diab:.1%}")

# Key Finding 2: BMI distribution
print("\n--- FINDING 2: BMI Statistics by Diabetes Status ---")
bmi_stats = df.groupby('Diabetes')['BMI'].agg(['mean', 'median', 'std'])
bmi_stats.index = ['No Diabetes', 'Diabetes']
print(bmi_stats.round(2))

# Key Finding 3: Age distribution
print("\n--- FINDING 3: Age Category Distribution by Diabetes Status ---")
age_ct = df.groupby(['Diabetes', 'Age']).size().unstack(fill_value=0)
age_pct = age_ct.div(age_ct.sum(axis=1), axis=0).round(3)
print("Age category proportions (1=18-24, 13=80+):")
print(age_pct)

# ─────────────────────────────────────────────────────────────────────────────
# FIGURES FOR Q1
# ─────────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 12))
fig.suptitle('Figure 1: Exploratory Data Analysis — Diabetes Health Indicators',
             fontsize=14, fontweight='bold', y=1.01)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

# (a) Diabetes prevalence
ax0 = fig.add_subplot(gs[0, 0])
counts = df['Diabetes'].value_counts().sort_index()
bars = ax0.bar(['No Diabetes\n(0)', 'Diabetes\n(1)'], counts.values,
               color=['#4C72B0', '#DD8452'], edgecolor='white', width=0.5)
ax0.set_title('(a) Diabetes Prevalence', fontweight='bold')
ax0.set_ylabel('Count')
for bar, val in zip(bars, counts.values):
    ax0.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
             f'{val:,}\n({val/len(df):.1%})', ha='center', va='bottom', fontsize=9)
ax0.set_ylim(0, max(counts.values) * 1.18)

# (b) Key Finding 1 – Risk factor prevalence
ax1 = fig.add_subplot(gs[0, 1])
factors = ['HighBP', 'HighChol', 'Smoker', 'HeartDiseaseorAttack', 'DiffWalk']
labels = ['High BP', 'High Chol', 'Smoker', 'Heart\nDisease', 'Diff Walk']
no_d = [df.loc[df['Diabetes']==0, f].mean()*100 for f in factors]
yes_d = [df.loc[df['Diabetes']==1, f].mean()*100 for f in factors]
x = np.arange(len(factors))
w = 0.35
ax1.bar(x - w/2, no_d, w, label='No Diabetes', color='#4C72B0', edgecolor='white')
ax1.bar(x + w/2, yes_d, w, label='Diabetes', color='#DD8452', edgecolor='white')
ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontsize=8)
ax1.set_ylabel('Prevalence (%)')
ax1.set_title('(b) Finding 1: Risk Factor\nPrevalence by Diabetes Status', fontweight='bold')
ax1.legend(fontsize=8)
ax1.set_ylim(0, 100)

# (c) Key Finding 2 – BMI distributions
ax2 = fig.add_subplot(gs[0, 2])
bmi_no = df.loc[df['Diabetes']==0, 'BMI']
bmi_yes = df.loc[df['Diabetes']==1, 'BMI']
ax2.hist(bmi_no, bins=40, alpha=0.6, label=f'No Diabetes\n(mean={bmi_no.mean():.1f})',
         color='#4C72B0', density=True)
ax2.hist(bmi_yes, bins=40, alpha=0.6, label=f'Diabetes\n(mean={bmi_yes.mean():.1f})',
         color='#DD8452', density=True)
ax2.axvline(bmi_no.mean(), color='#4C72B0', linestyle='--', linewidth=1.5)
ax2.axvline(bmi_yes.mean(), color='#DD8452', linestyle='--', linewidth=1.5)
ax2.axvline(30, color='green', linestyle=':', linewidth=1.5, label='Obesity cutoff (30)')
ax2.set_xlabel('BMI')
ax2.set_ylabel('Density')
ax2.set_title('(c) Finding 2: BMI Distribution\nby Diabetes Status', fontweight='bold')
ax2.legend(fontsize=7)

# (d) Key Finding 3 – Age distribution
ax3 = fig.add_subplot(gs[1, 0])
age_no = df.loc[df['Diabetes']==0, 'Age'].value_counts().sort_index()
age_yes = df.loc[df['Diabetes']==1, 'Age'].value_counts().sort_index()
age_labels = {1:'18-24',2:'25-29',3:'30-34',4:'35-39',5:'40-44',
              6:'45-49',7:'50-54',8:'55-59',9:'60-64',10:'65-69',
              11:'70-74',12:'75-79',13:'80+'}
x_ages = sorted(age_no.index)
ax3.plot(x_ages, [age_no.get(a,0)/len(bmi_no)*100 for a in x_ages],
         'o-', color='#4C72B0', label='No Diabetes', linewidth=2)
ax3.plot(x_ages, [age_yes.get(a,0)/len(bmi_yes)*100 for a in x_ages],
         's-', color='#DD8452', label='Diabetes', linewidth=2)
ax3.set_xticks(x_ages[::2])
ax3.set_xticklabels([age_labels[a] for a in x_ages[::2]], rotation=30, fontsize=7)
ax3.set_ylabel('% within group')
ax3.set_title('(c) Finding 3: Age Distribution\nby Diabetes Status', fontweight='bold')
ax3.legend(fontsize=8)

# (e) Correlation heatmap
ax4 = fig.add_subplot(gs[1, 1:])
corr_cols = ['Diabetes', 'HighBP', 'HighChol', 'BMI', 'Age',
             'Stroke', 'HeartDiseaseorAttack', 'GenHlth', 'DiffWalk', 'PhysActivity']
corr = df[corr_cols].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            ax=ax4, annot_kws={'size': 8}, linewidths=0.3)
ax4.set_title('(e) Correlation Matrix of Key Variables', fontweight='bold')
ax4.tick_params(axis='x', rotation=30, labelsize=8)
ax4.tick_params(axis='y', rotation=0, labelsize=8)

plt.savefig('/home/user/2025-AN6001B/fig1_eda.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nFig 1 saved: fig1_eda.png")


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: Propensity Score Matching
# ─────────────────────────────────────────────────────────────────────────────
def propensity_score_matching(df, treatment_col, outcome_col, confounders, caliper=0.02):
    """
    1:1 Nearest-Neighbour PSM with caliper.
    Returns (ATE, SE, matched_df)
    """
    df_clean = df[confounders + [treatment_col, outcome_col]].dropna().copy()

    # Logistic regression for propensity score
    X = df_clean[confounders]
    T = df_clean[treatment_col]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    logit = LogisticRegression(max_iter=1000)
    logit.fit(X_scaled, T)
    df_clean['ps'] = logit.predict_proba(X_scaled)[:, 1]

    # Nearest-neighbour matching
    treated = df_clean[df_clean[treatment_col] == 1].copy()
    control = df_clean[df_clean[treatment_col] == 0].copy()
    nn = NearestNeighbors(n_neighbors=1)
    nn.fit(control[['ps']])
    distances, indices = nn.kneighbors(treated[['ps']])
    mask = distances.flatten() <= caliper
    treated_matched = treated[mask].copy()
    control_matched = control.iloc[indices.flatten()[mask]].copy()

    matched = pd.concat([treated_matched, control_matched], ignore_index=True)
    ate = (treated_matched[outcome_col].mean() - control_matched[outcome_col].mean())
    n_matched = len(treated_matched)
    # Bootstrap SE
    boot_ates = []
    np.random.seed(42)
    for _ in range(200):
        idx = np.random.choice(len(treated_matched), len(treated_matched), replace=True)
        boot_ates.append(
            treated_matched.iloc[idx][outcome_col].mean() -
            control_matched.iloc[idx][outcome_col].mean()
        )
    se = np.std(boot_ates)
    return ate, se, matched, df_clean


def ipw_estimate(df, treatment_col, outcome_col, confounders):
    """Inverse Probability Weighting (Horvitz-Thompson) estimator."""
    df_clean = df[confounders + [treatment_col, outcome_col]].dropna().copy()
    X = df_clean[confounders]
    T = df_clean[treatment_col]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    logit = LogisticRegression(max_iter=1000)
    logit.fit(X_scaled, T)
    ps = logit.predict_proba(X_scaled)[:, 1]
    ps = np.clip(ps, 0.01, 0.99)
    # Stabilised weights
    w1 = T / ps
    w0 = (1 - T) / (1 - ps)
    y = df_clean[outcome_col].values
    mu1 = np.sum(w1 * y) / np.sum(w1)
    mu0 = np.sum(w0 * y) / np.sum(w0)
    ate = mu1 - mu0
    return ate, ps, df_clean


def regression_adjustment(df, treatment_col, outcome_col, confounders):
    """OLS regression adjustment / doubly-robust style estimate."""
    formula_vars = ' + '.join([treatment_col] + confounders)
    formula = f'{outcome_col} ~ {formula_vars}'
    model = smf.ols(formula, data=df).fit()
    coef = model.params[treatment_col]
    se = model.bse[treatment_col]
    pval = model.pvalues[treatment_col]
    conf = model.conf_int().loc[treatment_col]
    return coef, se, pval, conf, model


# ─────────────────────────────────────────────────────────────────────────────
# CONFOUNDERS (variables that affect both treatment and outcome)
# Based on causal DAG: Age, BMI, Sex, Education, Income affect both BP/Chol and Diabetes
# Also including smoking, physical activity as confounders
# ─────────────────────────────────────────────────────────────────────────────
confounders_bp = ['Age', 'BMI', 'Sex', 'Education', 'Income',
                  'Smoker', 'PhysActivity', 'Fruits', 'Veggies',
                  'HvyAlcoholConsump', 'HeartDiseaseorAttack', 'GenHlth']

confounders_chol = ['Age', 'BMI', 'Sex', 'Education', 'Income',
                    'Smoker', 'PhysActivity', 'Fruits', 'Veggies',
                    'HvyAlcoholConsump', 'HeartDiseaseorAttack', 'GenHlth']

# ─────────────────────────────────────────────────────────────────────────────
# Q2: CAUSAL EFFECT OF HIGH BP ON DIABETES
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("Q2: CAUSAL EFFECT OF HIGH BP ON DIABETES")
print("=" * 70)

# Naive / unadjusted association
naive_bp = df.groupby('HighBP')['Diabetes'].mean()
naive_ate_bp = naive_bp[1] - naive_bp[0]
print(f"\nNaïve (unadjusted) diabetes rate:")
print(f"  HighBP=0 (no high BP): {naive_bp[0]:.3f} ({naive_bp[0]:.1%})")
print(f"  HighBP=1 (high BP):    {naive_bp[1]:.3f} ({naive_bp[1]:.1%})")
print(f"  Naïve ATE:             {naive_ate_bp:.3f} ({naive_ate_bp:.1%})")

# Chi-square test
ct_bp = pd.crosstab(df['HighBP'], df['Diabetes'])
chi2, p_chi2, dof, _ = stats.chi2_contingency(ct_bp)
or_bp = (ct_bp.iloc[1,1] * ct_bp.iloc[0,0]) / (ct_bp.iloc[1,0] * ct_bp.iloc[0,1])
print(f"\n  Chi-square: {chi2:.1f}, p-value: {p_chi2:.2e}")
print(f"  Crude Odds Ratio: {or_bp:.3f}")

# Method 1: Regression Adjustment
print("\n--- Method 1: Regression Adjustment ---")
coef_bp, se_bp, pval_bp, ci_bp, ols_bp = regression_adjustment(
    df, 'HighBP', 'Diabetes', confounders_bp)
print(f"  Adjusted ATE (OLS):  {coef_bp:.4f}")
print(f"  Std Error:           {se_bp:.4f}")
print(f"  95% CI:              [{ci_bp[0]:.4f}, {ci_bp[1]:.4f}]")
print(f"  p-value:             {pval_bp:.2e}")

# Method 2: IPW
print("\n--- Method 2: Inverse Probability Weighting ---")
ate_ipw_bp, ps_bp, df_bp = ipw_estimate(df, 'HighBP', 'Diabetes', confounders_bp)
print(f"  IPW ATE:             {ate_ipw_bp:.4f}")

# Method 3: Propensity Score Matching
print("\n--- Method 3: Propensity Score Matching ---")
ate_psm_bp, se_psm_bp, matched_bp, df_bp2 = propensity_score_matching(
    df, 'HighBP', 'Diabetes', confounders_bp)
print(f"  PSM ATE:             {ate_psm_bp:.4f}")
print(f"  Std Error:           {se_psm_bp:.4f}")
print(f"  95% CI:              [{ate_psm_bp - 1.96*se_psm_bp:.4f}, {ate_psm_bp + 1.96*se_psm_bp:.4f}]")

# Summary
print(f"\n  SUMMARY – Effect of HighBP on Diabetes:")
print(f"  {'Method':<30} {'ATE':>8}")
print(f"  {'-'*40}")
print(f"  {'Naïve (unadjusted)':<30} {naive_ate_bp:>8.4f}")
print(f"  {'Regression Adjustment':<30} {coef_bp:>8.4f}")
print(f"  {'IPW':<30} {ate_ipw_bp:>8.4f}")
print(f"  {'PSM':<30} {ate_psm_bp:>8.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# Q3: CAUSAL EFFECT OF HIGH CHOL ON DIABETES
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("Q3: CAUSAL EFFECT OF HIGH CHOL ON DIABETES")
print("=" * 70)

naive_chol = df.groupby('HighChol')['Diabetes'].mean()
naive_ate_chol = naive_chol[1] - naive_chol[0]
print(f"\nNaïve (unadjusted) diabetes rate:")
print(f"  HighChol=0: {naive_chol[0]:.3f} ({naive_chol[0]:.1%})")
print(f"  HighChol=1: {naive_chol[1]:.3f} ({naive_chol[1]:.1%})")
print(f"  Naïve ATE:  {naive_ate_chol:.3f} ({naive_ate_chol:.1%})")

ct_chol = pd.crosstab(df['HighChol'], df['Diabetes'])
chi2c, p_chi2c, _, _ = stats.chi2_contingency(ct_chol)
or_chol = (ct_chol.iloc[1,1]*ct_chol.iloc[0,0]) / (ct_chol.iloc[1,0]*ct_chol.iloc[0,1])
print(f"\n  Chi-square: {chi2c:.1f}, p-value: {p_chi2c:.2e}")
print(f"  Crude Odds Ratio: {or_chol:.3f}")

print("\n--- Method 1: Regression Adjustment ---")
coef_chol, se_chol, pval_chol, ci_chol, ols_chol = regression_adjustment(
    df, 'HighChol', 'Diabetes', confounders_chol)
print(f"  Adjusted ATE (OLS):  {coef_chol:.4f}")
print(f"  Std Error:           {se_chol:.4f}")
print(f"  95% CI:              [{ci_chol[0]:.4f}, {ci_chol[1]:.4f}]")
print(f"  p-value:             {pval_chol:.2e}")

print("\n--- Method 2: IPW ---")
ate_ipw_chol, ps_chol, df_chol = ipw_estimate(df, 'HighChol', 'Diabetes', confounders_chol)
print(f"  IPW ATE:             {ate_ipw_chol:.4f}")

print("\n--- Method 3: PSM ---")
ate_psm_chol, se_psm_chol, matched_chol, df_chol2 = propensity_score_matching(
    df, 'HighChol', 'Diabetes', confounders_chol)
print(f"  PSM ATE:             {ate_psm_chol:.4f}")
print(f"  Std Error:           {se_psm_chol:.4f}")
print(f"  95% CI:              [{ate_psm_chol - 1.96*se_psm_chol:.4f}, {ate_psm_chol + 1.96*se_psm_chol:.4f}]")

print(f"\n  SUMMARY – Effect of HighChol on Diabetes:")
print(f"  {'Method':<30} {'ATE':>8}")
print(f"  {'-'*40}")
print(f"  {'Naïve (unadjusted)':<30} {naive_ate_chol:>8.4f}")
print(f"  {'Regression Adjustment':<30} {coef_chol:>8.4f}")
print(f"  {'IPW':<30} {ate_ipw_chol:>8.4f}")
print(f"  {'PSM':<30} {ate_psm_chol:>8.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURES FOR Q2 & Q3
# ─────────────────────────────────────────────────────────────────────────────

# Figure 2: Causal inference – HighBP
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Figure 2: Causal Effect of High BP on Diabetes', fontsize=13, fontweight='bold')

# (a) Naive comparison
ax = axes[0]
rates = [naive_bp[0]*100, naive_bp[1]*100]
bars = ax.bar(['No High BP', 'High BP'], rates, color=['#4C72B0', '#DD8452'], width=0.5)
ax.set_ylabel('Diabetes Rate (%)')
ax.set_title('(a) Unadjusted Diabetes Rates')
for bar, rate in zip(bars, rates):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
ax.set_ylim(0, max(rates)*1.2)

# (b) Propensity score distribution before/after matching
ax = axes[1]
df_bp2['group'] = df_bp2['HighBP'].map({1: 'Treated (HighBP)', 0: 'Control'})
ax.hist(df_bp2.loc[df_bp2['HighBP']==0, 'ps'], bins=30, alpha=0.6,
        label='Control (before)', color='#4C72B0', density=True)
ax.hist(df_bp2.loc[df_bp2['HighBP']==1, 'ps'], bins=30, alpha=0.6,
        label='Treated (before)', color='#DD8452', density=True)
ax.set_xlabel('Propensity Score')
ax.set_ylabel('Density')
ax.set_title('(b) Propensity Score Distribution\n(Before Matching)')
ax.legend(fontsize=8)

# (c) ATE comparison across methods
ax = axes[2]
methods = ['Naïve', 'Regression\nAdjustment', 'IPW', 'PSM']
ates = [naive_ate_bp, coef_bp, ate_ipw_bp, ate_psm_bp]
colors = ['gray', '#2196F3', '#4CAF50', '#FF5722']
bars = ax.bar(methods, [a*100 for a in ates], color=colors, width=0.5, edgecolor='white')
ax.axhline(0, color='black', linestyle='-', linewidth=0.8)
ax.set_ylabel('ATE (percentage points)')
ax.set_title('(c) ATE Estimates\nAcross Methods')
for bar, ate in zip(bars, ates):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + (0.2 if ate >= 0 else -0.5),
            f'{ate*100:.1f}pp', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_ylim(-2, max([a*100 for a in ates])*1.3)

plt.tight_layout()
plt.savefig('/home/user/2025-AN6001B/fig2_highbp_causal.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nFig 2 saved: fig2_highbp_causal.png")


# Figure 3: Causal inference – HighChol
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Figure 3: Causal Effect of High Cholesterol on Diabetes', fontsize=13, fontweight='bold')

ax = axes[0]
rates = [naive_chol[0]*100, naive_chol[1]*100]
bars = ax.bar(['No High Chol', 'High Chol'], rates, color=['#4C72B0', '#DD8452'], width=0.5)
ax.set_ylabel('Diabetes Rate (%)')
ax.set_title('(a) Unadjusted Diabetes Rates')
for bar, rate in zip(bars, rates):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
ax.set_ylim(0, max(rates)*1.2)

ax = axes[1]
df_chol['ps'] = ps_chol
ax.hist(df_chol.loc[df_chol['HighChol']==0, 'ps'], bins=30, alpha=0.6,
        label='Control (no High Chol)', color='#4C72B0', density=True)
ax.hist(df_chol.loc[df_chol['HighChol']==1, 'ps'], bins=30, alpha=0.6,
        label='Treated (High Chol)', color='#DD8452', density=True)
ax.set_xlabel('Propensity Score')
ax.set_ylabel('Density')
ax.set_title('(b) Propensity Score Distribution\n(Before Matching)')
ax.legend(fontsize=8)

ax = axes[2]
methods = ['Naïve', 'Regression\nAdjustment', 'IPW', 'PSM']
ates = [naive_ate_chol, coef_chol, ate_ipw_chol, ate_psm_chol]
bars = ax.bar(methods, [a*100 for a in ates], color=colors, width=0.5, edgecolor='white')
ax.axhline(0, color='black', linestyle='-', linewidth=0.8)
ax.set_ylabel('ATE (percentage points)')
ax.set_title('(c) ATE Estimates\nAcross Methods')
for bar, ate in zip(bars, ates):
    ypos = bar.get_height() + (0.1 if ate >= 0 else -0.5)
    ax.text(bar.get_x() + bar.get_width()/2, ypos,
            f'{ate*100:.1f}pp', ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('/home/user/2025-AN6001B/fig3_highchol_causal.png', dpi=150, bbox_inches='tight')
plt.close()
print("Fig 3 saved: fig3_highchol_causal.png")


# ─────────────────────────────────────────────────────────────────────────────
# Additional checks: Love plot / Standardised Mean Differences
# ─────────────────────────────────────────────────────────────────────────────
def standardised_md(df_all, df_matched, treatment, covars):
    """Compute standardised mean differences before and after matching."""
    results = []
    for col in covars:
        t_all = df_all.loc[df_all[treatment]==1, col].mean()
        c_all = df_all.loc[df_all[treatment]==0, col].mean()
        pooled_sd_all = np.sqrt((df_all.loc[df_all[treatment]==1, col].std()**2 +
                                 df_all.loc[df_all[treatment]==0, col].std()**2) / 2)
        smd_before = (t_all - c_all) / (pooled_sd_all + 1e-9)

        t_m = df_matched.loc[df_matched[treatment]==1, col].mean()
        c_m = df_matched.loc[df_matched[treatment]==0, col].mean()
        pooled_sd_m = np.sqrt((df_matched.loc[df_matched[treatment]==1, col].std()**2 +
                                df_matched.loc[df_matched[treatment]==0, col].std()**2) / 2)
        smd_after = (t_m - c_m) / (pooled_sd_m + 1e-9)
        results.append({'Covariate': col, 'SMD_before': smd_before, 'SMD_after': smd_after})
    return pd.DataFrame(results)

# ─────────────────────────────────────────────────────────────────────────────
# Figure 4: Love plots (covariate balance)
# ─────────────────────────────────────────────────────────────────────────────
smd_bp = standardised_md(df, matched_bp, 'HighBP', confounders_bp)
smd_chol = standardised_md(df, matched_chol, 'HighChol', confounders_chol)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Figure 4: Covariate Balance — Love Plots (PSM)',
             fontsize=13, fontweight='bold')

for ax, smd, title in zip(axes, [smd_bp, smd_chol],
                          ['HighBP Treatment', 'HighChol Treatment']):
    smd_sorted = smd.reindex(smd['SMD_before'].abs().sort_values().index)
    y = np.arange(len(smd_sorted))
    ax.scatter(smd_sorted['SMD_before'], y, marker='o', color='#DD8452',
               s=60, label='Before matching', zorder=3)
    ax.scatter(smd_sorted['SMD_after'], y, marker='D', color='#4C72B0',
               s=60, label='After matching', zorder=3)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.axvline(0.1, color='red', linestyle='--', linewidth=1, label='|SMD|=0.1 threshold')
    ax.axvline(-0.1, color='red', linestyle='--', linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(smd_sorted['Covariate'], fontsize=8)
    ax.set_xlabel('Standardised Mean Difference')
    ax.set_title(f'({chr(97+list(axes).index(ax))}) {title}', fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('/home/user/2025-AN6001B/fig4_love_plots.png', dpi=150, bbox_inches='tight')
plt.close()
print("Fig 4 saved: fig4_love_plots.png")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("FINAL RESULTS SUMMARY")
print("=" * 70)
print(f"""
HighBP → Diabetes:
  Naïve ATE:           {naive_ate_bp:.4f} ({naive_ate_bp*100:.1f} pp)
  Regression-adjusted: {coef_bp:.4f}  (SE={se_bp:.4f}, p={pval_bp:.2e})
  IPW:                 {ate_ipw_bp:.4f}
  PSM:                 {ate_psm_bp:.4f}  (SE={se_psm_bp:.4f})

HighChol → Diabetes:
  Naïve ATE:           {naive_ate_chol:.4f} ({naive_ate_chol*100:.1f} pp)
  Regression-adjusted: {coef_chol:.4f}  (SE={se_chol:.4f}, p={pval_chol:.2e})
  IPW:                 {ate_ipw_chol:.4f}
  PSM:                 {ate_psm_chol:.4f}  (SE={se_psm_chol:.4f})
""")
