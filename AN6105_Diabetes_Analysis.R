# =============================================================================
# AN6105 Causal Inference — Graded Individual Assignment
# Part A: Causal Inference on Diabetes
# Dataset: CDC BRFSS 2015 Diabetes Health Indicators (diabetes_data.csv)
#          https://www.kaggle.com/datasets/prosperchuks/health-dataset/data
# =============================================================================
# Run in RStudio: Session > Set Working Directory > To Source File Location
# Then: Source (Ctrl+Shift+S) or run section by section

# ── 0. Setup ──────────────────────────────────────────────────────────────────
required_pkgs <- c("tidyverse", "ggplot2", "gridExtra", "patchwork",
                   "MatchIt", "scales", "MASS")
new_pkgs <- required_pkgs[!required_pkgs %in% installed.packages()[, "Package"]]
if (length(new_pkgs)) install.packages(new_pkgs)

library(tidyverse)
library(ggplot2)
library(gridExtra)
library(patchwork)
library(MatchIt)
library(scales)

set.seed(42)

# ── 1. Load data ──────────────────────────────────────────────────────────────
# Place diabetes_data.csv in the same folder as this script,
# or update the path below.
df <- read.csv("diabetes_data.csv")

# Variable labels (for readable plots)
age_labels <- c("18-24","25-29","30-34","35-39","40-44","45-49",
                "50-54","55-59","60-64","65-69","70-74","75-79","80+")

df <- df %>%
  mutate(
    Diabetes_f  = factor(Diabetes,  levels = c(0,1), labels = c("No Diabetes","Diabetes")),
    HighBP_f    = factor(HighBP,    levels = c(0,1), labels = c("No High BP","High BP")),
    HighChol_f  = factor(HighChol,  levels = c(0,1), labels = c("No High Chol","High Chol")),
    Age_label   = factor(Age, levels = 1:13, labels = age_labels)
  )

cat("==================================================\n")
cat("DATASET OVERVIEW\n")
cat("==================================================\n")
cat(sprintf("Rows: %d   Columns: %d\n", nrow(df), ncol(df)))
cat(sprintf("Missing values: %d\n", sum(is.na(df))))
cat("\nDiabetes prevalence:\n")
print(table(df$Diabetes_f))
cat(sprintf("Diabetes rate: %.1f%%\n", mean(df$Diabetes)*100))


# =============================================================================
# Q1: DATA EXPLORATION — THREE KEY FINDINGS
# =============================================================================
cat("\n==================================================\n")
cat("Q1: DATA EXPLORATION\n")
cat("==================================================\n")

# ── Finding 1: Risk factor prevalence by diabetes status ──────────────────────
risk_vars <- c("HighBP","HighChol","Smoker","Stroke","HeartDiseaseorAttack",
               "PhysActivity","DiffWalk")
rf_table <- df %>%
  group_by(Diabetes_f) %>%
  summarise(across(all_of(risk_vars), ~ round(mean(.x)*100, 1)), .groups="drop")

cat("\nFINDING 1 — Risk Factor Prevalence (%) by Diabetes Status:\n")
print(as.data.frame(rf_table))

# ── Finding 2: BMI ────────────────────────────────────────────────────────────
bmi_stats <- df %>%
  group_by(Diabetes_f) %>%
  summarise(Mean = round(mean(BMI),2), Median = median(BMI),
            SD = round(sd(BMI),2), .groups="drop")
cat("\nFINDING 2 — BMI by Diabetes Status:\n")
print(bmi_stats)

# ── Finding 3: Age ────────────────────────────────────────────────────────────
cat("\nFINDING 3 — Age distribution (proportion within group):\n")
age_dist <- df %>%
  count(Diabetes_f, Age_label) %>%
  group_by(Diabetes_f) %>%
  mutate(pct = round(n/sum(n)*100, 1)) %>%
  ungroup()
print(age_dist %>% pivot_wider(id_cols=Age_label, names_from=Diabetes_f,
                               values_from=pct), n=13)

# ── Correlation matrix ────────────────────────────────────────────────────────
cor_vars <- c("Diabetes","HighBP","HighChol","BMI","Age",
              "Stroke","HeartDiseaseorAttack","GenHlth","DiffWalk","PhysActivity")
cor_mat  <- round(cor(df[, cor_vars]), 2)
cat("\nCorrelation Matrix (key variables):\n")
print(cor_mat)


# ── FIGURE 1: EDA ─────────────────────────────────────────────────────────────
pal2 <- c("No Diabetes" = "#4C72B0", "Diabetes" = "#DD8452")

# (a) Prevalence bar
p_prev <- ggplot(df, aes(x = Diabetes_f, fill = Diabetes_f)) +
  geom_bar(width = 0.5, colour = "white") +
  geom_text(stat = "count",
            aes(label = paste0(after_stat(count) %>% scales::comma(), "\n(",
                               round(after_stat(count)/nrow(df)*100,1),"%)")),
            vjust = -0.3, size = 3.2) +
  scale_fill_manual(values = pal2) +
  scale_y_continuous(labels = scales::comma, expand = expansion(mult = c(0,.15))) +
  labs(title = "(a) Diabetes Prevalence", x = NULL, y = "Count") +
  theme_bw(base_size = 10) + theme(legend.position = "none")

# (b) Risk factor prevalence
rf_long <- df %>%
  select(Diabetes_f, HighBP, HighChol, Smoker, HeartDiseaseorAttack, DiffWalk) %>%
  pivot_longer(-Diabetes_f, names_to = "Factor", values_to = "val") %>%
  group_by(Diabetes_f, Factor) %>%
  summarise(pct = mean(val)*100, .groups="drop") %>%
  mutate(Factor = recode(Factor,
    HighBP="High BP", HighChol="High Chol", Smoker="Smoker",
    HeartDiseaseorAttack="Heart\nDisease", DiffWalk="Diff Walk"))

p_rf <- ggplot(rf_long, aes(x = Factor, y = pct, fill = Diabetes_f)) +
  geom_col(position = "dodge", width = 0.65, colour = "white") +
  scale_fill_manual(values = pal2) +
  scale_y_continuous(limits = c(0,100)) +
  labs(title = "(b) Finding 1: Risk Factor\nPrevalence by Diabetes Status",
       x = NULL, y = "Prevalence (%)", fill = NULL) +
  theme_bw(base_size = 10) +
  theme(legend.position = "bottom", axis.text.x = element_text(size=8))

# (c) BMI density
p_bmi <- ggplot(df, aes(x = BMI, fill = Diabetes_f, colour = Diabetes_f)) +
  geom_density(alpha = 0.55, linewidth = 0.8) +
  geom_vline(data = bmi_stats, aes(xintercept = Mean, colour = Diabetes_f),
             linetype = "dashed", linewidth = 1) +
  geom_vline(xintercept = 30, colour = "darkgreen", linetype = "dotted", linewidth = 1) +
  annotate("text", x = 31.5, y = 0.065, label = "BMI=30\n(Obese)", size = 2.8,
           colour = "darkgreen") +
  scale_fill_manual(values  = pal2) +
  scale_colour_manual(values = pal2) +
  labs(title = "(c) Finding 2: BMI Distribution\nby Diabetes Status",
       x = "BMI", y = "Density", fill = NULL, colour = NULL) +
  theme_bw(base_size = 10) + theme(legend.position = "bottom")

# (d) Age distribution
p_age <- ggplot(age_dist, aes(x = Age_label, y = pct,
                              colour = Diabetes_f, group = Diabetes_f)) +
  geom_line(linewidth = 1) + geom_point(size = 2) +
  scale_colour_manual(values = pal2) +
  scale_x_discrete(guide = guide_axis(angle = 35)) +
  labs(title = "(d) Finding 3: Age Distribution\nby Diabetes Status",
       x = "Age Group", y = "% within group", colour = NULL) +
  theme_bw(base_size = 10) + theme(legend.position = "bottom")

# (e) Correlation heatmap
cor_long <- as.data.frame(cor_mat) %>%
  rownames_to_column("Var1") %>%
  pivot_longer(-Var1, names_to = "Var2", values_to = "r")

p_cor <- ggplot(cor_long, aes(x = Var1, y = Var2, fill = r)) +
  geom_tile(colour = "white") +
  geom_text(aes(label = sprintf("%.2f", r)), size = 2.6) +
  scale_fill_gradient2(low="#d73027", mid="white", high="#4575b4",
                       midpoint=0, limits=c(-1,1)) +
  scale_x_discrete(guide = guide_axis(angle = 35)) +
  labs(title = "(e) Correlation Matrix", x = NULL, y = NULL, fill = "r") +
  theme_bw(base_size = 9)

layout <- (p_prev | p_rf | p_bmi) / (p_age | p_cor) +
  plot_annotation(
    title = "Figure 1: Exploratory Data Analysis — Diabetes Health Indicators",
    theme = theme(plot.title = element_text(face="bold", size=13))
  )

ggsave("fig1_eda.png", layout, width=16, height=10, dpi=150)
cat("\nFig 1 saved: fig1_eda.png\n")


# =============================================================================
# CAUSAL INFERENCE SETUP
# =============================================================================
# Confounders for both analyses:
# Variables that plausibly affect BOTH the treatment (HighBP/HighChol) AND
# the outcome (Diabetes) — selected based on causal DAG reasoning.
confounders <- c("Age","BMI","Sex","Education","Income",
                 "Smoker","PhysActivity","Fruits","Veggies",
                 "HvyAlcoholConsump","HeartDiseaseorAttack","GenHlth")

formula_bp   <- as.formula(paste("HighBP ~",   paste(confounders, collapse=" + ")))
formula_chol <- as.formula(paste("HighChol ~", paste(confounders, collapse=" + ")))


# Helper: IPW (Horvitz-Thompson stabilised weights)
ipw_ate <- function(df, treat_col, outcome_col, confounders) {
  f <- as.formula(paste(treat_col, "~", paste(confounders, collapse=" + ")))
  ps_model <- glm(f, data=df, family=binomial())
  ps  <- fitted(ps_model)
  ps  <- pmin(pmax(ps, 0.01), 0.99)
  T   <- df[[treat_col]];  Y <- df[[outcome_col]]
  w1  <- T / ps;           w0 <- (1-T) / (1-ps)
  mu1 <- sum(w1*Y) / sum(w1)
  mu0 <- sum(w0*Y) / sum(w0)
  list(ate = mu1 - mu0, ps = ps)
}

# Helper: OLS regression adjustment
ols_ate <- function(df, treat_col, outcome_col, confounders) {
  f <- as.formula(paste(outcome_col, "~", treat_col, "+",
                        paste(confounders, collapse=" + ")))
  m <- lm(f, data=df)
  ci <- confint(m)[treat_col,]
  list(coef = coef(m)[treat_col],
       se   = summary(m)$coefficients[treat_col, "Std. Error"],
       pval = summary(m)$coefficients[treat_col, "Pr(>|t|)"],
       ci   = ci)
}

# Helper: SMD before/after matching (for Love plot)
smd_calc <- function(df_all, df_matched, treat_col, covars) {
  out <- lapply(covars, function(v) {
    grp <- function(d) {
      t1 <- d[[v]][d[[treat_col]]==1];  t0 <- d[[v]][d[[treat_col]]==0]
      smd <- (mean(t1)-mean(t0)) /
             sqrt((var(t1)+var(t0))/2 + 1e-9)
      smd
    }
    data.frame(Covariate=v, Before=grp(df_all), After=grp(df_matched))
  })
  do.call(rbind, out)
}


# =============================================================================
# Q2: CAUSAL EFFECT OF HIGH BP ON DIABETES
# =============================================================================
cat("\n==================================================\n")
cat("Q2: CAUSAL EFFECT OF HIGH BP ON DIABETES\n")
cat("==================================================\n")

# Naive association
naive_bp <- df %>% group_by(HighBP) %>% summarise(rate=mean(Diabetes), .groups="drop")
naive_ate_bp <- diff(naive_bp$rate)
ct_bp  <- table(df$HighBP, df$Diabetes)
or_bp  <- (ct_bp[2,2]*ct_bp[1,1]) / (ct_bp[2,1]*ct_bp[1,2])
chi_bp <- chisq.test(ct_bp)
cat(sprintf("\nNaïve diabetes rate: No HighBP=%.1f%%  HighBP=%.1f%%\n",
            naive_bp$rate[1]*100, naive_bp$rate[2]*100))
cat(sprintf("Naïve ATE: %.4f (%.1f pp)\n", naive_ate_bp, naive_ate_bp*100))
cat(sprintf("Crude OR: %.3f   Chi-sq p: %.2e\n", or_bp, chi_bp$p.value))

# Method 1: Regression Adjustment
res_ols_bp <- ols_ate(df, "HighBP", "Diabetes", confounders)
cat(sprintf("\nOLS Adjusted ATE: %.4f  SE=%.4f  p=%.2e  95%%CI=[%.4f, %.4f]\n",
            res_ols_bp$coef, res_ols_bp$se, res_ols_bp$pval,
            res_ols_bp$ci[1], res_ols_bp$ci[2]))

# Method 2: IPW
res_ipw_bp <- ipw_ate(df, "HighBP", "Diabetes", confounders)
cat(sprintf("IPW ATE: %.4f\n", res_ipw_bp$ate))

# Method 3: PSM (1:1 nearest-neighbour with caliper)
cat("\nRunning PSM for HighBP (this may take a moment)...\n")
m_bp <- matchit(formula_bp, data=df, method="nearest", distance="logit",
                ratio=1, caliper=0.02, replace=FALSE)
matched_bp <- match.data(m_bp)
ate_psm_bp <- mean(matched_bp$Diabetes[matched_bp$HighBP==1]) -
              mean(matched_bp$Diabetes[matched_bp$HighBP==0])

# Bootstrap SE for PSM
boot_psm_bp <- replicate(300, {
  idx1 <- sample(which(matched_bp$HighBP==1), replace=TRUE)
  idx0 <- sample(which(matched_bp$HighBP==0), replace=TRUE)
  mean(matched_bp$Diabetes[idx1]) - mean(matched_bp$Diabetes[idx0])
})
se_psm_bp <- sd(boot_psm_bp)
cat(sprintf("PSM ATE: %.4f  SE=%.4f  95%%CI=[%.4f, %.4f]\n",
            ate_psm_bp, se_psm_bp,
            ate_psm_bp - 1.96*se_psm_bp,
            ate_psm_bp + 1.96*se_psm_bp))
cat(sprintf("Matched sample: %d treated, %d control\n",
            sum(matched_bp$HighBP==1), sum(matched_bp$HighBP==0)))

# Summary table
cat("\nSUMMARY — Effect of HighBP on Diabetes:\n")
bp_summary <- data.frame(
  Method = c("Naïve (unadjusted)","Regression Adjustment","IPW","PSM"),
  ATE_pp = round(c(naive_ate_bp, res_ols_bp$coef,
                   res_ipw_bp$ate, ate_psm_bp)*100, 2)
)
print(bp_summary)


# =============================================================================
# Q3: CAUSAL EFFECT OF HIGH CHOL ON DIABETES
# =============================================================================
cat("\n==================================================\n")
cat("Q3: CAUSAL EFFECT OF HIGH CHOL ON DIABETES\n")
cat("==================================================\n")

naive_chol   <- df %>% group_by(HighChol) %>%
                  summarise(rate=mean(Diabetes), .groups="drop")
naive_ate_chol <- diff(naive_chol$rate)
ct_chol  <- table(df$HighChol, df$Diabetes)
or_chol  <- (ct_chol[2,2]*ct_chol[1,1]) / (ct_chol[2,1]*ct_chol[1,2])
chi_chol <- chisq.test(ct_chol)
cat(sprintf("\nNaïve diabetes rate: No HighChol=%.1f%%  HighChol=%.1f%%\n",
            naive_chol$rate[1]*100, naive_chol$rate[2]*100))
cat(sprintf("Naïve ATE: %.4f (%.1f pp)\n", naive_ate_chol, naive_ate_chol*100))
cat(sprintf("Crude OR: %.3f   Chi-sq p: %.2e\n", or_chol, chi_chol$p.value))

res_ols_chol <- ols_ate(df, "HighChol", "Diabetes", confounders)
cat(sprintf("\nOLS Adjusted ATE: %.4f  SE=%.4f  p=%.2e  95%%CI=[%.4f, %.4f]\n",
            res_ols_chol$coef, res_ols_chol$se, res_ols_chol$pval,
            res_ols_chol$ci[1], res_ols_chol$ci[2]))

res_ipw_chol <- ipw_ate(df, "HighChol", "Diabetes", confounders)
cat(sprintf("IPW ATE: %.4f\n", res_ipw_chol$ate))

cat("\nRunning PSM for HighChol (this may take a moment)...\n")
m_chol <- matchit(formula_chol, data=df, method="nearest", distance="logit",
                  ratio=1, caliper=0.02, replace=FALSE)
matched_chol <- match.data(m_chol)
ate_psm_chol <- mean(matched_chol$Diabetes[matched_chol$HighChol==1]) -
                mean(matched_chol$Diabetes[matched_chol$HighChol==0])

boot_psm_chol <- replicate(300, {
  idx1 <- sample(which(matched_chol$HighChol==1), replace=TRUE)
  idx0 <- sample(which(matched_chol$HighChol==0), replace=TRUE)
  mean(matched_chol$Diabetes[idx1]) - mean(matched_chol$Diabetes[idx0])
})
se_psm_chol <- sd(boot_psm_chol)
cat(sprintf("PSM ATE: %.4f  SE=%.4f  95%%CI=[%.4f, %.4f]\n",
            ate_psm_chol, se_psm_chol,
            ate_psm_chol - 1.96*se_psm_chol,
            ate_psm_chol + 1.96*se_psm_chol))

cat("\nSUMMARY — Effect of HighChol on Diabetes:\n")
chol_summary <- data.frame(
  Method = c("Naïve (unadjusted)","Regression Adjustment","IPW","PSM"),
  ATE_pp = round(c(naive_ate_chol, res_ols_chol$coef,
                   res_ipw_chol$ate, ate_psm_chol)*100, 2)
)
print(chol_summary)


# =============================================================================
# FIGURE 2: Causal Effect of High BP
# =============================================================================
method_cols <- c("Naïve"="#888888", "Regression\nAdjustment"="#2196F3",
                 "IPW"="#4CAF50", "PSM"="#FF5722")

# (a) unadjusted bar
p2a <- ggplot(naive_bp %>% mutate(HighBP_f=factor(HighBP,0:1,c("No High BP","High BP"))),
              aes(x=HighBP_f, y=rate*100, fill=HighBP_f)) +
  geom_col(width=0.5, colour="white") +
  geom_text(aes(label=sprintf("%.1f%%",rate*100)), vjust=-0.4, fontface="bold", size=3.5) +
  scale_fill_manual(values=c("No High BP"="#4C72B0","High BP"="#DD8452")) +
  scale_y_continuous(limits=c(0,85)) +
  labs(title="(a) Unadjusted Diabetes Rates", x=NULL, y="Diabetes Rate (%)") +
  theme_bw(base_size=10) + theme(legend.position="none")

# (b) propensity score distributions
ps_df_bp <- data.frame(
  ps    = res_ipw_bp$ps,
  Group = ifelse(df$HighBP==1,"Treated (High BP)","Control")
)
p2b <- ggplot(ps_df_bp, aes(x=ps, fill=Group)) +
  geom_histogram(aes(y=after_stat(density)), bins=35, alpha=0.65,
                 position="identity", colour="white") +
  scale_fill_manual(values=c("Control"="#4C72B0","Treated (High BP)"="#DD8452")) +
  labs(title="(b) Propensity Score Distribution\n(Before Matching)",
       x="Propensity Score", y="Density", fill=NULL) +
  theme_bw(base_size=10) + theme(legend.position="bottom")

# (c) ATE comparison
ates_bp <- data.frame(
  Method = c("Naïve","Regression\nAdjustment","IPW","PSM"),
  ATE    = c(naive_ate_bp, res_ols_bp$coef, res_ipw_bp$ate, ate_psm_bp)*100
)
ates_bp$Method <- factor(ates_bp$Method, levels=ates_bp$Method)
p2c <- ggplot(ates_bp, aes(x=Method, y=ATE, fill=Method)) +
  geom_col(width=0.5, colour="white") +
  geom_text(aes(label=sprintf("%.1f pp",ATE)), vjust=-0.4, fontface="bold", size=3.2) +
  geom_hline(yintercept=0, linewidth=0.8) +
  scale_fill_manual(values=method_cols) +
  scale_y_continuous(limits=c(0, max(ates_bp$ATE)*1.25)) +
  labs(title="(c) ATE Estimates Across Methods",
       x=NULL, y="ATE (percentage points)") +
  theme_bw(base_size=10) + theme(legend.position="none")

fig2 <- (p2a | p2b | p2c) +
  plot_annotation(
    title="Figure 2: Causal Effect of High BP on Diabetes",
    theme=theme(plot.title=element_text(face="bold",size=13))
  )
ggsave("fig2_highbp_causal.png", fig2, width=16, height=5, dpi=150)
cat("\nFig 2 saved: fig2_highbp_causal.png\n")


# =============================================================================
# FIGURE 3: Causal Effect of High Cholesterol
# =============================================================================
p3a <- ggplot(naive_chol %>%
                mutate(HighChol_f=factor(HighChol,0:1,c("No High Chol","High Chol"))),
              aes(x=HighChol_f, y=rate*100, fill=HighChol_f)) +
  geom_col(width=0.5, colour="white") +
  geom_text(aes(label=sprintf("%.1f%%",rate*100)), vjust=-0.4, fontface="bold", size=3.5) +
  scale_fill_manual(values=c("No High Chol"="#4C72B0","High Chol"="#DD8452")) +
  scale_y_continuous(limits=c(0,80)) +
  labs(title="(a) Unadjusted Diabetes Rates", x=NULL, y="Diabetes Rate (%)") +
  theme_bw(base_size=10) + theme(legend.position="none")

ps_df_chol <- data.frame(
  ps    = res_ipw_chol$ps,
  Group = ifelse(df$HighChol==1,"Treated (High Chol)","Control")
)
p3b <- ggplot(ps_df_chol, aes(x=ps, fill=Group)) +
  geom_histogram(aes(y=after_stat(density)), bins=35, alpha=0.65,
                 position="identity", colour="white") +
  scale_fill_manual(values=c("Control"="#4C72B0","Treated (High Chol)"="#DD8452")) +
  labs(title="(b) Propensity Score Distribution\n(Before Matching)",
       x="Propensity Score", y="Density", fill=NULL) +
  theme_bw(base_size=10) + theme(legend.position="bottom")

ates_chol <- data.frame(
  Method = c("Naïve","Regression\nAdjustment","IPW","PSM"),
  ATE    = c(naive_ate_chol, res_ols_chol$coef, res_ipw_chol$ate, ate_psm_chol)*100
)
ates_chol$Method <- factor(ates_chol$Method, levels=ates_chol$Method)
p3c <- ggplot(ates_chol, aes(x=Method, y=ATE, fill=Method)) +
  geom_col(width=0.5, colour="white") +
  geom_text(aes(label=sprintf("%.1f pp",ATE)), vjust=-0.4, fontface="bold", size=3.2) +
  geom_hline(yintercept=0, linewidth=0.8) +
  scale_fill_manual(values=method_cols) +
  scale_y_continuous(limits=c(0, max(ates_chol$ATE)*1.25)) +
  labs(title="(c) ATE Estimates Across Methods",
       x=NULL, y="ATE (percentage points)") +
  theme_bw(base_size=10) + theme(legend.position="none")

fig3 <- (p3a | p3b | p3c) +
  plot_annotation(
    title="Figure 3: Causal Effect of High Cholesterol on Diabetes",
    theme=theme(plot.title=element_text(face="bold",size=13))
  )
ggsave("fig3_highchol_causal.png", fig3, width=16, height=5, dpi=150)
cat("Fig 3 saved: fig3_highchol_causal.png\n")


# =============================================================================
# FIGURE 4: Love Plots — Covariate Balance (PSM)
# =============================================================================
smd_bp_df   <- smd_calc(df, matched_bp,   "HighBP",   confounders)
smd_chol_df <- smd_calc(df, matched_chol, "HighChol", confounders)

make_love_plot <- function(smd_df, title) {
  smd_long <- smd_df %>%
    arrange(abs(Before)) %>%
    mutate(Covariate = factor(Covariate, levels=Covariate)) %>%
    pivot_longer(c(Before, After), names_to="Timing", values_to="SMD")
  ggplot(smd_long, aes(x=SMD, y=Covariate, colour=Timing, shape=Timing)) +
    geom_point(size=2.8) +
    geom_vline(xintercept=0,   colour="black",  linewidth=0.7) +
    geom_vline(xintercept= 0.1, colour="red", linetype="dashed", linewidth=0.8) +
    geom_vline(xintercept=-0.1, colour="red", linetype="dashed", linewidth=0.8) +
    scale_colour_manual(values=c(Before="#DD8452", After="#4C72B0")) +
    scale_shape_manual(values=c(Before=16, After=18)) +
    labs(title=title, x="Standardised Mean Difference", y=NULL,
         colour=NULL, shape=NULL) +
    theme_bw(base_size=10) +
    theme(legend.position="bottom") +
    annotate("text", x=0.11, y=0.7, label="|SMD|=0.1\nthreshold",
             colour="red", size=2.5, hjust=0)
}

p4a <- make_love_plot(smd_bp_df,   "(a) HighBP Treatment")
p4b <- make_love_plot(smd_chol_df, "(b) HighChol Treatment")

fig4 <- (p4a | p4b) +
  plot_annotation(
    title="Figure 4: Covariate Balance — Love Plots (Before vs. After PSM)",
    theme=theme(plot.title=element_text(face="bold",size=13))
  )
ggsave("fig4_love_plots.png", fig4, width=14, height=6, dpi=150)
cat("Fig 4 saved: fig4_love_plots.png\n")


# =============================================================================
# FINAL SUMMARY
# =============================================================================
cat("\n==================================================\n")
cat("FINAL RESULTS SUMMARY\n")
cat("==================================================\n")
cat(sprintf("
HighBP → Diabetes:
  Naïve ATE:            %.4f  (%.1f pp)
  Regression Adjustment: %.4f  (SE=%.4f, p=%.2e)
  IPW:                  %.4f
  PSM:                  %.4f  (SE=%.4f, 95%%CI=[%.4f, %.4f])

HighChol → Diabetes:
  Naïve ATE:            %.4f  (%.1f pp)
  Regression Adjustment: %.4f  (SE=%.4f, p=%.2e)
  IPW:                  %.4f
  PSM:                  %.4f  (SE=%.4f, 95%%CI=[%.4f, %.4f])
",
naive_ate_bp,  naive_ate_bp*100,
res_ols_bp$coef,  res_ols_bp$se,  res_ols_bp$pval,
res_ipw_bp$ate,
ate_psm_bp, se_psm_bp, ate_psm_bp-1.96*se_psm_bp, ate_psm_bp+1.96*se_psm_bp,

naive_ate_chol,  naive_ate_chol*100,
res_ols_chol$coef,  res_ols_chol$se,  res_ols_chol$pval,
res_ipw_chol$ate,
ate_psm_chol, se_psm_chol, ate_psm_chol-1.96*se_psm_chol, ate_psm_chol+1.96*se_psm_chol
))

cat("All figures saved. Now regenerating Word document...\n")
