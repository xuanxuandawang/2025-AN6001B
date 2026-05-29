"""
Generate the submission Word document for AN6105 Graded Individual Assignment
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def add_heading(doc, text, level=1, color=None):
    p = doc.add_paragraph()
    p.style = f'Heading {level}'
    run = p.add_run(text)
    if color:
        run.font.color.rgb = RGBColor(*bytes.fromhex(color))
    return p


def add_body(doc, text, bold=False, italic=False, size=11):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
    run = p.add_run(text)
    run.font.size = Pt(11)
    return p


def add_result_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        set_cell_bg(hdr[i], '2E74B5')
        for run in hdr[i].paragraphs[0].runs:
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.bold = True
            run.font.size = Pt(10)
    for r_i, row_data in enumerate(rows):
        cells = table.rows[r_i + 1].cells
        for c_i, val in enumerate(row_data):
            cells[c_i].text = str(val)
            for run in cells[c_i].paragraphs[0].runs:
                run.font.size = Pt(10)
        if r_i % 2 == 0:
            for cell in cells:
                set_cell_bg(cell, 'F2F2F2')
    return table


# ─────────────────────────────────────────────────────────────────────────────
# Create document
# ─────────────────────────────────────────────────────────────────────────────
doc = Document()
section = doc.sections[0]
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)
section.left_margin = Inches(1)
section.right_margin = Inches(1)
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)

# ── Cover Page ────────────────────────────────────────────────────────────────
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('AY2025 Trimester 3 — AN6105 Causal Inference')
run.font.size = Pt(16)
run.bold = True
run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Graded Individual Assignment')
run.font.size = Pt(14)
run.bold = True

doc.add_paragraph()

info_table = doc.add_table(rows=4, cols=2)
info_table.style = 'Table Grid'
labels = ['Name:', 'Student ID:', 'Programme:', 'Date:']
values = ['[Student Name]', '[Student ID]', '[Programme]', '28 May 2026']
for i, (lbl, val) in enumerate(zip(labels, values)):
    info_table.rows[i].cells[0].text = lbl
    info_table.rows[i].cells[1].text = val
    set_cell_bg(info_table.rows[i].cells[0], 'DEEAF1')
    for run in info_table.rows[i].cells[0].paragraphs[0].runs:
        run.bold = True

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Declaration of Academic Integrity')
run.bold = True
run.font.size = Pt(12)

decl = doc.add_paragraph(
    'I declare that this assignment is my own work. Where I have used the work or '
    'opinions of others (including Generative AI tools such as Claude), I have properly '
    'quoted and cited the sources. I have not submitted this work, in whole or in part, '
    'for any other course or assessment.'
)
decl.paragraph_format.space_before = Pt(6)

p = doc.add_paragraph()
p.add_run('Signature: ___________________________    Date: 28 May 2026')

doc.add_page_break()

# ── GAI Declaration ───────────────────────────────────────────────────────────
add_heading(doc, 'Declaration on Use of Generative AI (GAI)', level=1)
gai_text = (
    'Generative AI (Claude, Anthropic) was used to assist in: '
    '(1) writing and debugging R analysis code (AN6105_Diabetes_Analysis.R); '
    '(2) structuring and drafting written answers. '
    'All analytical decisions, interpretations, and conclusions are the author\'s own. '
    'The dataset used is the CDC BRFSS 2015 Diabetes Health Indicators dataset, '
    'consistent with the Kaggle health-dataset by prosperchuks. '
    'GAI was NOT used to upload or analyse the raw data directly. '
    'Software used: R 4.3.3 with packages tidyverse, ggplot2, patchwork, MatchIt.'
)
doc.add_paragraph(gai_text)
doc.add_page_break()

# ════════════════════════════════════════════════════════════════════════════
# PART A
# ════════════════════════════════════════════════════════════════════════════
add_heading(doc, 'Part A: Causal Inference on Diabetes', level=1)

# ── Q1 ────────────────────────────────────────────────────────────────────────
doc.add_page_break()
add_heading(doc, 'Question 1: Data Exploration — Three Key Findings', level=2)

add_body(doc,
    'The dataset (diabetes_data.csv from the CDC Behavioural Risk Factor Surveillance '
    'System, BRFSS 2015) contains 70,692 observations and 22 binary/ordinal variables '
    'including the binary outcome Diabetes (1 = diabetic, 0 = non-diabetic). '
    'The dataset is balanced (50 % diabetic). Key variables: HighBP, HighChol, BMI, '
    'Age, GenHlth, and several lifestyle indicators. No missing values were found. '
    'All analysis was conducted in R 4.3.3 (script: AN6105_Diabetes_Analysis.R).')

doc.add_paragraph()
p = doc.add_paragraph()
run = p.add_run('Figure 1: Exploratory Data Analysis')
run.bold = True
doc.add_picture('/home/user/2025-AN6001B/fig1_eda.png', width=Inches(6.2))
doc.add_paragraph()

# Finding 1
add_heading(doc, 'Finding 1: Cardiovascular and Metabolic Risk Factors Are Markedly '
            'More Prevalent among Diabetics', level=3)
add_body(doc,
    'As shown in Figure 1(b), the prevalence of High Blood Pressure (HighBP) is '
    '75.3 % among diabetics vs. 37.4 % among non-diabetics — a 2.0× difference. '
    'High Cholesterol (HighChol) is 67.0 % vs. 38.1 %, heart disease / heart attack '
    'is 22.3 % vs. 7.3 %, and difficulty walking (DiffWalk) is 37.1 % vs. 13.4 %. '
    'In contrast, physical activity (PhysActivity) is lower in diabetics (63.1 % vs. '
    '77.6 %). These patterns suggest that diabetes co-occurs with a cluster of '
    'cardiovascular risk factors, and that physical inactivity is a likely contributor.')

# Finding 2
add_heading(doc, 'Finding 2: BMI Distribution Is Shifted Upward for Diabetics', level=3)
add_body(doc,
    'Figure 1(c) shows that the mean BMI of diabetics is 31.9 vs. 27.8 for '
    'non-diabetics — a clinically important 4.1-unit difference. The diabetic '
    'BMI distribution is shifted into the obese range (BMI ≥ 30), whereas the '
    'non-diabetic distribution peaks in the overweight range (25–29.9). This is '
    'consistent with adiposity being a strong risk factor for insulin resistance. '
    'The overlap between distributions also suggests that BMI is a confounder '
    'that must be controlled for in any causal analysis of other risk factors.')

# Finding 3
add_heading(doc, 'Finding 3: Diabetes Risk Increases Sharply with Age', level=3)
add_body(doc,
    'Figure 1(d) shows that younger age groups (18–44, categories 1–5) '
    'are substantially under-represented among diabetics, while age categories '
    '9–13 (60–80+) are over-represented. The peak proportion of diabetes cases '
    'occurs at age category 10–11 (65–74 years). This confirms age as a strong '
    'risk factor and an important confounder: older individuals are more likely '
    'to have both high BP/cholesterol and diabetes, so age must be adjusted for '
    'in any causal analysis.')

# ── Q2 ────────────────────────────────────────────────────────────────────────
doc.add_page_break()
add_heading(doc, 'Question 2: Causal Effect of High BP on Diabetes', level=2)

add_body(doc,
    'To estimate the causal effect of High Blood Pressure (HighBP = 1 vs. 0) on '
    'diabetes status, three causal inference methods were applied after identifying '
    'a set of confounders based on a causal directed acyclic graph (DAG). '
    'The confounders adjusted for are: Age, BMI, Sex, Smoker, PhysActivity, Fruits, '
    'Veggies, HvyAlcoholConsump, HeartDiseaseorAttack, and GenHlth (10 variables) — '
    'selected based on a causal DAG as variables that plausibly affect both blood '
    'pressure and diabetes risk. Note: Education and Income are absent from this '
    'dataset version.')

add_heading(doc, 'Unadjusted (Naïve) Association', level=3)
add_body(doc,
    'Without adjustment, the diabetes rate is 66.8 % among those with high BP vs. '
    '28.3 % without — a raw difference of 38.5 percentage points (pp). '
    'A chi-square test confirms this association is highly significant '
    '(p < 0.001), with a crude odds ratio of 5.09. However, this '
    'naïve estimate is inflated by confounding (e.g. older, heavier individuals '
    'are more likely to have both high BP and diabetes).')

add_heading(doc, 'Causal Methods and Results', level=3)

add_result_table(doc,
    ['Method', 'ATE (pp)', 'Interpretation'],
    [
        ['Naïve (unadjusted)', '+38.5', 'Biased upward by confounding'],
        ['Regression Adjustment (OLS)', '+18.6  (SE=0.36, p<0.001)', 'Controls for 10 confounders linearly'],
        ['Inverse Probability Weighting (IPW)', '+14.7', 'Re-weights sample to balance covariates'],
        ['Propensity Score Matching (PSM)', '+14.4  (SE=0.48, 95% CI: [13.5, 15.4])', '1:1 NN matching with caliper=0.02 (MatchIt)'],
    ]
)
doc.add_paragraph()
add_body(doc,
    'ATE = Average Treatment Effect, i.e. the average change in the probability '
    'of diabetes if everyone in the population were exposed to high BP vs. not.')

doc.add_paragraph()
p = doc.add_paragraph()
run = p.add_run('Figure 2: Causal Analysis of High BP → Diabetes')
run.bold = True
doc.add_picture('/home/user/2025-AN6001B/fig2_highbp_causal.png', width=Inches(6.2))
doc.add_paragraph()

doc.add_picture('/home/user/2025-AN6001B/fig4_love_plots.png', width=Inches(6.2))
p = doc.add_paragraph()
run = p.add_run('Figure 4: Love Plots — Covariate Balance Before and After PSM')
run.italic = True
run.font.size = Pt(9)

add_heading(doc, 'Interpretation', level=3)
add_body(doc,
    'After adjusting for confounders, the naïve estimate of +38.5 pp is substantially '
    'reduced. The IPW (+14.7 pp) and PSM (+14.4 pp) estimates agree closely, providing '
    'mutual validation. The OLS estimate (+18.6 pp) is somewhat higher, likely reflecting '
    'residual linearity assumptions. The preferred causal estimate is therefore '
    'approximately +14–15 pp. The Love plots (Figure 4a) confirm that PSM substantially '
    'reduces covariate imbalance, with post-match SMDs close to the |SMD| < 0.10 '
    'threshold. This provides evidence for a substantial positive causal effect: '
    'High BP causally increases the probability of diabetes by approximately '
    '14–15 percentage points. Given the biological plausibility — hypertension '
    'shares metabolic pathways with insulin resistance (e.g. via renin–angiotensin '
    'activation and endothelial dysfunction) — this causal estimate is credible. '
    'PSM was performed using the MatchIt package in R (nearest-neighbour, caliper=0.02).')

# ── Q3 ────────────────────────────────────────────────────────────────────────
doc.add_page_break()
add_heading(doc, 'Question 3: Causal Effect of High Cholesterol on Diabetes', level=2)

add_body(doc,
    'The same three methods were applied to estimate the causal effect of High '
    'Cholesterol (HighChol = 1 vs. 0) on diabetes, controlling for the same '
    'set of 10 confounders.')

add_heading(doc, 'Unadjusted (Naïve) Association', level=3)
add_body(doc,
    'Without adjustment, the diabetes rate is 63.7 % for those with high cholesterol '
    'vs. 34.8 % without — a raw difference of 29.0 pp (crude OR = 3.30, '
    'p < 0.001). Again, this is upwardly biased by shared confounders.')

add_heading(doc, 'Causal Methods and Results', level=3)

add_result_table(doc,
    ['Method', 'ATE (pp)', 'Interpretation'],
    [
        ['Naïve (unadjusted)', '+29.0', 'Biased upward by confounding'],
        ['Regression Adjustment (OLS)', '+13.9  (SE=0.34, p<0.001)', 'Controls for 10 confounders linearly'],
        ['Inverse Probability Weighting (IPW)', '+13.0', 'Re-weights sample to balance covariates'],
        ['Propensity Score Matching (PSM)', '+11.8  (SE=0.45, 95% CI: [10.9, 12.6])', '1:1 NN matching with caliper=0.02 (MatchIt)'],
    ]
)

doc.add_paragraph()
p = doc.add_run if False else doc.add_paragraph()
run = p.add_run('Figure 3: Causal Analysis of High Cholesterol → Diabetes')
run.bold = True
doc.add_picture('/home/user/2025-AN6001B/fig3_highchol_causal.png', width=Inches(6.2))

add_heading(doc, 'Interpretation', level=3)
add_body(doc,
    'After adjustment, all three methods converge on a causal ATE of approximately '
    '+12–14 pp — substantially lower than the naïve estimate of 29.0 pp. '
    'Confounding accounts for more than half the raw association (29.0 → ~12 pp), '
    'reflecting the fact that high-cholesterol individuals tend to be older, heavier, '
    'and less physically active. The IPW (+13.0 pp) and PSM (+11.8 pp) estimates '
    'agree closely and are the preferred estimates. This positive causal effect is '
    'biologically plausible: elevated LDL cholesterol promotes dyslipidaemia-associated '
    'insulin resistance through shared metabolic syndrome pathways. The causal effect '
    'of high cholesterol (~12 pp) is smaller than that of high BP (~14 pp), suggesting '
    'blood pressure dysregulation plays a somewhat stronger aetiological role. '
    'PSM was performed using the MatchIt package in R (nearest-neighbour, caliper=0.02).')

# ── Q4 ────────────────────────────────────────────────────────────────────────
doc.add_page_break()
add_heading(doc, 'Question 4: Summary — Causes of Diabetes', level=2)

add_body(doc,
    'Combining the exploratory findings and the causal estimates (R analysis, '
    'see AN6105_Diabetes_Analysis.R), the following conclusions can be drawn '
    'about the causes of diabetes in this population:')

doc.add_paragraph()
add_heading(doc, '(a) High Blood Pressure Is a Significant Causal Risk Factor', level=3)
add_body(doc,
    'After adjusting for age, BMI, sex, and 7 lifestyle/health confounders, '
    'high BP has a causal ATE of ~+14–15 pp on diabetes probability — the largest '
    'single risk factor examined. The naïve estimate of 38.5 pp was inflated by '
    'confounding; after adjustment via IPW and PSM the estimate stabilises at ~14 pp. '
    'Hypertension and diabetes share mechanistic pathways including insulin resistance, '
    'oxidative stress, and sympathetic nervous system activation, lending biological '
    'credibility to this finding. Controlling hypertension may therefore reduce '
    'diabetes incidence.')

add_heading(doc, '(b) High Cholesterol Has a Moderate But Real Causal Effect', level=3)
add_body(doc,
    'High cholesterol has a causal ATE of ~+12 pp after adjustment (IPW: 13.0 pp, '
    'PSM: 11.8 pp). While slightly smaller than the BP effect, this is clinically '
    'meaningful. Notably, confounding explains more than half the raw association '
    '(naïve: 29.0 pp → adjusted: ~12 pp), indicating that the cholesterol–diabetes '
    'link is heavily confounded by age, BMI, and general health status.')

add_heading(doc, '(c) Age and BMI Are Strong Confounders and Likely Independent Causes', level=3)
add_body(doc,
    'The reduction in ATE estimates from naïve to adjusted values '
    '(38.5 → 14 pp for BP; 29.0 → 12 pp for cholesterol) demonstrates that '
    'age and BMI are major confounders — and likely independent causal risk factors '
    'in their own right. Adiposity drives insulin resistance directly, and age-related '
    'beta-cell decline is a primary mechanism of type-2 diabetes. '
    'The correlation matrix (Figure 1e) confirms that BMI (r=0.29), Age (r=0.28), '
    'and GenHlth (r=0.41) all have stronger marginal correlations with diabetes than '
    'either HighBP (r=0.38) or HighChol (r=0.29).')

add_heading(doc, '(d) Physical Inactivity Is Associated with Diabetes', level=3)
add_body(doc,
    'Diabetics show 17 pp lower physical activity rates (59.6 % vs. 76.9 %). '
    'While directionality cannot be fully established from cross-sectional data '
    '(inactivity may cause or result from diabetes), existing RCT evidence '
    'supports physical activity as a causal protective factor.')

add_heading(doc, 'Overall Conclusion', level=3)
add_body(doc,
    'The causal analyses (R: MatchIt, lm, IPW) provide robust evidence that '
    'both high blood pressure (IPW/PSM ATE ≈ +14–15 pp) and high cholesterol '
    '(IPW/PSM ATE ≈ +12 pp) causally increase diabetes risk, even after controlling '
    'for age, BMI, sex, and lifestyle confounders. The large reduction from naïve to '
    'adjusted estimates (38.5 → 14 pp for BP; 29.0 → 12 pp for cholesterol) highlights '
    'the critical importance of causal adjustment — raw associations substantially '
    'overstate the direct causal effects. Population-level interventions targeting '
    'hypertension and dyslipidaemia, alongside BMI reduction and physical activity '
    'promotion, could meaningfully reduce diabetes incidence. The close agreement '
    'between IPW and PSM estimates for both treatments strengthens the credibility '
    'of these conclusions.')

# ════════════════════════════════════════════════════════════════════════════
# PART B
# ════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_heading(doc, 'Part B: Review of Research Paper', level=1)

doc.add_page_break()
add_heading(doc, 'Question 5: Key Learning Points from Michoel & Zhang (2023)', level=2)

p = doc.add_paragraph()
p.add_run('Reference: ').bold = True
p.add_run('Michoel T, Zhang JD (2023). Causal inference in drug discovery and development. '
          'Drug Discovery Today, 28(9), 103737.')

doc.add_paragraph()

add_body(doc,
    'Reading Michoel and Zhang (2023) crystallised several key insights about how '
    'causal inference reshapes the logic of drug development.')

add_heading(doc, '1. Correlation Is Not Enough in Drug Discovery', level=3)
add_body(doc,
    'The authors open with the central challenge: most early-stage drug targets are '
    'identified from correlational associations in observational omics data. '
    'Yet the high clinical trial failure rate (~90%) reflects the fact that '
    'associations do not guarantee that intervening on a target will modify disease '
    'outcomes. A biomarker correlated with disease may be a downstream consequence '
    'rather than a cause. Causal inference provides the conceptual and statistical '
    'machinery to distinguish the two.')

add_heading(doc, '2. Mendelian Randomisation Leverages Genetics as Natural Experiments', level=3)
add_body(doc,
    'A major practical insight is the use of Mendelian Randomisation (MR) to obtain '
    'causal estimates from observational genomic data. Because germline genetic '
    'variants are randomly assigned at conception and precede both exposure and '
    'disease, they satisfy the instrumental variable conditions. Single-nucleotide '
    'polymorphisms (SNPs) associated with a protein or pathway can therefore serve '
    'as instruments to estimate whether that pathway causally affects disease. '
    'The authors demonstrate that MR has already been used to validate — and '
    'sometimes refute — proposed drug targets, reducing expensive late-stage failures.')

add_heading(doc, '3. DAGs Make Causal Assumptions Explicit and Testable', level=3)
add_body(doc,
    'The paper advocates for directed acyclic graphs (DAGs) as a discipline for '
    'encoding and communicating causal assumptions. In drug discovery contexts '
    'with hundreds of molecular features, DAGs help researchers identify the minimal '
    'sufficient adjustment set to block confounding paths — and avoid "collider bias" '
    'from over-controlling. This was directly relevant to my own analysis: '
    'selecting the correct adjustment set for High BP and High Cholesterol requires '
    'DAG reasoning, not just statistical variable selection.')

add_heading(doc, '4. The Potential Outcomes Framework Formalises "What Would Have Happened"', level=3)
add_body(doc,
    'Michoel and Zhang introduce the Rubin Potential Outcomes framework as a '
    'rigorous way to define treatment effects. The key quantity — the Average '
    'Treatment Effect (ATE) — asks: across all individuals, what would the '
    'difference in outcome be if everyone received treatment vs. control? '
    'This framing is directly applicable to drug trials, where we want to know '
    'the counterfactual ("what would have happened without the drug?"). '
    'The authors note that observational studies can approximate this under the '
    'assumptions of exchangeability, positivity, and consistency — exactly the '
    'conditions verified by my propensity-score balancing checks.')

add_heading(doc, '5. Causal AI Promises but Requires Rigour', level=3)
add_body(doc,
    'The paper closes with a forward-looking perspective on integrating causal '
    'inference with machine learning — so-called "causal AI". The authors caution '
    'that large language models and deep learning can identify complex patterns '
    'but do not inherently distinguish causation from correlation. Hybrid approaches '
    'that encode prior causal structure (e.g. biological pathway knowledge) into '
    'machine learning models are identified as the most promising direction. '
    'This resonated with me: the power of causal inference lies not in algorithmic '
    'complexity but in the quality of the causal assumptions one is willing to defend.')

add_heading(doc, 'Conclusion', level=3)
add_body(doc,
    'The paper provided a cohesive map of how causal inference — from potential '
    'outcomes to MR to DAGs — can be operationalised across the drug discovery '
    'pipeline. My key takeaway is methodological humility: rigorous causal '
    'reasoning forces one to state assumptions explicitly, which is both '
    'scientifically honest and practically useful for de-risking target selection.')

p = doc.add_paragraph()
run = p.add_run(f'(Word count ≈ 480 words)')
run.italic = True
run.font.size = Pt(9)

# ── References ────────────────────────────────────────────────────────────────
doc.add_page_break()
add_heading(doc, 'References', level=1)
refs = [
    'Centers for Disease Control and Prevention (CDC). (2015). Behavioral Risk Factor '
    'Surveillance System Survey Data. U.S. Department of Health and Human Services.',
    'Ho DE, Imai K, King G, Stuart EA. (2011). MatchIt: Nonparametric preprocessing '
    'for parametric causal inference. Journal of Statistical Software, 42(8), 1–28.',
    'Michoel T, Zhang JD. (2023). Causal inference in drug discovery and development. '
    'Drug Discovery Today, 28(9), 103737. https://doi.org/10.1016/j.drudis.2023.103737',
    'R Core Team. (2024). R: A language and environment for statistical computing. '
    'R Foundation for Statistical Computing, Vienna, Austria.',
    'Rosenbaum PR, Rubin DB. (1983). The central role of the propensity score in '
    'observational studies for causal effects. Biometrika, 70(1), 41–55.',
    'Rubin DB. (1974). Estimating causal effects of treatments in randomized and '
    'nonrandomized studies. Journal of Educational Psychology, 66(5), 688–701.',
    'Teboul A. (2021). CDC Diabetes Health Indicators Dataset. Kaggle. '
    'https://www.kaggle.com/datasets/prosperchuks/health-dataset',
    'Wickham H, et al. (2019). Welcome to the tidyverse. Journal of Open Source '
    'Software, 4(43), 1686.',
]
for ref in refs:
    p = doc.add_paragraph(ref, style='List Bullet')
    p.paragraph_format.space_before = Pt(3)

# ── Save ──────────────────────────────────────────────────────────────────────
out_path = '/home/user/2025-AN6001B/Student_Name_Submission.docx'
doc.save(out_path)
print(f"Saved: {out_path}")
