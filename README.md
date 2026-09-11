# Breast Cancer Classification - Model Building, Predictor Selection and Validation

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

## Repository contents

- `Predictive_model_on_breast_cancer.ipynb` — full analysis notebook
- `README.md` — this file
