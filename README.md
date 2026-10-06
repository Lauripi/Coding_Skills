# 1. Breast Cancer Classification - Model Building, Predictor Selection and Validation - Python 

A complete, leakage-aware machine learning pipeline for classifying breast tumors as malignant or benign. It is built not just to chase accuracy, but to produce a model whose feature selection and decision threshold can actually be defended and explained.

## Overview

- **Dataset:** Wisconsin Diagnostic Breast Cancer dataset (569 samples, 30 morphological features extracted from digitized biopsy images)
- **Task:** binary classification — malignant vs. benign tissue
- **Focus:** this project prioritizes methodological rigor over a single headline number : handling multicollinearity properly, validating feature selection stability, and choosing a decision threshold aligned with clinical priorities

## Results at a glance

| Metric | Value |
|---|---|
| ROC-AUC | 0.996 |
| Accuracy | 97.4% |
| Sensitivity (malignant recall) | 95.2% |
| Specificity | 98.6% |
| Features used | 12 (reduced from 30) |

## Methodology

1. **Exploratory analysis & correlation screening**: identified strong multicollinearity among size-related features (radius, perimeter, area are mathematically redundant); manually removed 9 redundant features before modeling.
2. **Model comparison** : benchmarked 6 classifiers (Logistic Regression, KNN, Linear/RBF SVM, Random Forest, Gradient Boosting) via 10-fold stratified cross-validation. Logistic Regression was selected for its interpretability, at no measurable cost in performance.
3. **Regularization comparison** : compared L1, L2, and Elastic Net penalties; L1 produced the sparsest model (12 features) with no loss in ROC-AUC.
4. **Threshold optimization** : compared a balanced (Youden) threshold against a minimum-sensitivity target, and selected the final threshold based on its best compromise between sensitivity and specificity.
5. **Feature stability validation** : bootstrap-resampled the L1 feature selection (200 iterations) to separate genuinely robust predictors from features that only appeared due to one particular data split.

## Skills demonstrated

- **Statistical rigor:** multicollinearity diagnosis, correlation-based feature reduction, nested cross-validation, bootstrap stability analysis
- **Machine learning:** regularized logistic regression (L1/L2/Elastic Net), systematic model benchmarking, hyperparameter tuning via GridSearchCV
- **Clinical decision-analytic thinking:** sensitivity/specificity trade-offs, threshold selection aligned to domain priorities, separation of cross-validated vs. held-out performance
- **Reproducible pipeline design:** leakage-safe workflow throughout (correlation computed on training data only, scaling fit within pipeline folds, thresholds chosen from training CV and applied once to a held-out test set)

## Tech stack

Python · scikit-learn · pandas · NumPy · matplotlib

## File

Predictive_model_on_breast_cancer.ipynb — full analysis notebook



# 2. Palmer Penguins - Data Cleaning, Visualisation and Statistical Inference - R 
A reproducible R workflow showing how I handle a fresh dataset: checked cleaning decisions, the right summary for each variable type, and tests chosen from verified assumptions.

## Overview
Dataset: Palmer Penguins (344 penguins, 3 species, 4 body measurements plus sex and year)

## Methodology
Cleaning : missing values per variable, the 2 empty rows identified by code, birds of unknown sex kept, range check on every numeric variable.
Description and visualisation : counts for categorical variables, mean ± SD and median (Q1/Q3) per species for continuous ones; density, scatter and violin plots, including a textbook Simpson's paradox on bill shape.
Inference : Shapiro–Wilk normality check, ANOVA and Kruskal–Wallis side by side, Tukey post hoc, Welch t-test, chi-square, Pearson correlation.

## Skills demonstrated
Statistical rigor: assumption checking, omnibus vs post hoc tests, confounding and Simpson's paradox
Data wrangling in R: tidyverse pipelines (dplyr, tidyr, purrr), long/wide reshaping
Visualisation: ggplot2, patchwork
Reproducible reporting: Quarto, flextable, everything loaded from packages

## Tech stack
R · tidyverse · Quarto · flextable · patchwork · ggbeeswarm · wrappedtools

## File/ Repository
Data_Cleaning_Visualisation_Statistical_Inference.md — rendered results, viewable on GitHub
Data_Cleaning_Visualisation_Statistical_Inference_files — tables and graphs used by .md file


# 3. SQL Exercises

## Overview : 
This file contains MySQL exercises focused on relational database design and basic SQL programming and was created to practice structuring relational databases and applying SQL concepts to scientific datasets.
Two example databases are included: a **laboratory database** for experiments, employees, tools, and results, and a **greenhouse database** for plants, gardeners, and greenhouse management.

## Skills demonstrated

* Creation of databases and tables
* Primary and foreign keys
* Constraints such as `CHECK`, `UNIQUE`, and `NOT NULL`
* Many-to-many relationships
* Stored procedures
* Subqueries and filtering

## File
SQL_Stored_Procedures_and_Database_Creation (code only)  

# 4. Crime Incidents - Data Cleaning, Exploration and Statistical Analysis - Python

A Python workflow applied to a messy, simulated crime dataset: from raw data with realistic quality problems to an analysis-ready table, followed by exploratory analysis and statistical tests. Cleaning decisions are checked and explained, and imputed values are flagged rather than hidden.

## Overview

- **Dataset:** simulated crime incident dataset from Kaggle [(https://www.kaggle.com/datasets/sananshaikh/messy-crime-dataset-for-data-cleaning-practice)], 5,250 records describing crimes, locations, victims, suspects, officers, arrests, property loss and case status
- **Task:** clean the raw data, then use it to answer three analysis questions
- **Focus:** transparent cleaning decisions, checks before and after each transformation, and statistical tests chosen to fit the data

## Cleaning at a glance

| Problem | Action | Result |
|---|---|---|
| Duplicate records | Removed | 5,250 → 5,050 rows |
| Typos, abbreviations and synonyms | Similarity detection (`difflib`) + manual review | e.g. crime type: 58 spellings → 4 categories; district: 16 → 10 |
| Malformed amounts (e.g. `35446.9.0`) | Repaired before numeric conversion | 136 values recovered |
| Three date formats, incl. US month-first | Each format converted explicitly | No swapped days and months |
| Impossible values (negative numbers, ages up to 298, latitudes > 90) | Sign corrected or set to missing | 331 ages and 176 coordinates set to missing |
| Missing victim/suspect gender | Inferred from first names (`gender-guesser`) | 1,964 values imputed and flagged |

## Methodology

1. **Initial data audit:** inspected datatypes, missing values, duplicates, categorical levels and numeric ranges to identify the main data-quality problems.
2. **Text and datatype standardization:** trimmed whitespace, standardized capitalization, stored identifiers as text and converted wrongly stored numbers to numeric values.
3. **Categorical cleaning:** detected spelling errors by string similarity, reviewed every suggested correction manually, harmonized abbreviations and synonyms, and grouped crime types into four broad categories.
4. **Missing-data handling:** assessed missingness variable by variable instead of applying one imputation rule; imputed gender from first names with explicit imputation and uncertainty flags, and left other missing values as missing.
5. **Numeric and geographic validation:** checked distributions and plausible ranges, corrected sign errors and set impossible values to missing.
6. **Date and time preprocessing:** split date and time, standardized three date formats, and created time-of-day and season variables.
7. **Exploration and analysis:** described the main variables (summary statistics, bar charts, histograms), then answered three questions with statistical tests. Numeric variables are not normally distributed, so non-parametric tests were used where needed.

## Results at a glance

| Question | Test | Result |
|---|---|---|
| Do incident counts differ between cities? | Chi-square goodness-of-fit | Yes (χ² = 15.6, p = 0.03); Riverside has the most incidents (705) |
| Does the crime-type mix differ between cities? | Chi-square test of independence | No (p = 0.26) |
| Did incidents change over time (2018–2024)? | Poisson regression on monthly counts | No significant trend (+1.1% per year, p = 0.12) |
| Do incidents vary by season? | Chi-square goodness-of-fit | No (p = 0.32) |
| Is crime severity linked to property loss? | Kruskal–Wallis, Spearman correlation | No (p = 0.79; ρ = 0.01, p = 0.39) |

## Skills demonstrated

- **Data cleaning:** duplicate detection, datatype conversion, string normalization, range validation, handling of mixed date formats
- **Categorical preprocessing:** typo detection, synonym harmonization, category grouping and manual quality control
- **Missing-data handling:** variable-by-variable assessment, selective imputation with explicit flags
- **Feature engineering:** time-of-day and season variables derived from raw timestamps
- **Statistics:** chi-square tests, Poisson regression for count data, non-parametric tests (Kruskal–Wallis, Spearman) chosen after checking distributions
- **Visualization:** bar charts, histograms, box plots and trend plots with matplotlib

## Tech stack

Python · pandas · NumPy · SciPy · statsmodels · matplotlib · difflib · gender-guesser

## File

Crimes_cleaning_data.ipynb 