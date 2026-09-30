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

# 4. Crime Incidents - Data Cleaning and Preprocessing - Python
**Under preparation!! -> data visualization and analysis soon added**

A Python data-cleaning workflow applied to a deliberately messy simulated crime dataset. The project focuses on identifying and correcting realistic data-quality problems while keeping cleaning decisions transparent and avoiding unjustified data imputation.

## Overview

- **Dataset:** simulated crime incident dataset with more than 5,000 records and information on crimes, locations, victims, suspects, officers, arrests, property loss and case status
- **Task:** transform inconsistent raw data into an analysis-ready dataset
- **Focus:** duplicate removal, datatype correction, categorical harmonization, missing-data handling, validation of numeric values and standardization of heterogeneous date/time information

## Methodology

1. **Initial data audit** : inspected datatypes, missing values, duplicate records, categorical levels and numerical ranges to identify the main data-quality problems.
2. **Text and datatype standardization** : removed leading/trailing and repeated whitespace, standardized capitalization, converted identifiers to appropriate string formats and coerced incorrectly stored numerical variables to numeric values.
3. **Categorical cleaning** : detected potential spelling errors using string similarity (`difflib`), manually reviewed suggested corrections and harmonized abbreviations and synonyms across variables such as crime type, district, weapon, severity, case status and reporting method.
4. **Missing-data handling** : evaluated missingness variable by variable rather than applying a single imputation strategy. Missing victim and suspect gender values were inferred from available first names using `gender-guesser`, with imputed and uncertain values explicitly flagged.
5. **Numeric and geographic validation** : inspected numerical distributions and plausible ranges, converted invalid values to missing where appropriate, and checked latitude/longitude against valid geographic ranges.
6. **Date and time preprocessing** : separated mixed date/time information, converted heterogeneous date formats to pandas datetime values and derived analysis-ready variables including time of day and season.

## Skills demonstrated

- **Data cleaning:** missing-value assessment, duplicate detection, datatype conversion, string normalization, outlier and range validation
- **Categorical data preprocessing:** typo detection, synonym harmonization, category reduction and manual quality control
- **Pragmatic missing-data handling:** selective imputation, preservation of unavailable information and explicit imputation/uncertainty flags
- **Feature engineering:** extraction and standardization of dates and times, creation of time-of-day and seasonal variables
- **Reproducible preprocessing:** systematic checks before and after transformations rather than manual row-by-row correction

## Tech stack

Python · pandas · NumPy · difflib · gender-guesser · matplotlib

## File

Crimes_cleaning_data.ipynb — full data-cleaning notebook

