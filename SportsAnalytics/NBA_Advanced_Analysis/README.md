## This folder showcases my work with NBA advanced metrics using complex computational methods.

## The projects in this folder include:

1. One Man Offense: Quantifying Heliocentrism in NBA Teams

The objective of this project is to analyze the effectiveness of high-usage players and their impact on team efficiency. Specifically, my goal was to find out whether or not over-reliance on a single "star" player leads to a diminishing return.

* Methodology: trained an XGBoost model (Binary Logisitic) on 2024-25 player telemetry and game outcomes
* Visualization Techniques:
  * Ceteris Paribus (CP) Profiles were created to isolate the specific turnover and player usage thresholds where the win probabilitly declines
  * SHAP Waterfall and Beeswarm plots used to decompose individual performances and see how high-volume scoring can sometimes negatively impact win probability


2. Predicting the Win: Intrinsic Interpretability in Team Metrics

The question to answer: Which advanced metrics are the true indicators of a winning season?

* Methodolgy: compared LASSO Regression (Linear/Regularized) against CART (Non-linear/Hierarchial) to predict 2025-2026 win percentages and to find potential hidden relationships between metrics
* Metrics:
  * Effective Field Goal % (eFG%)
  * Turnover % (TOV%)
  * Offensive Rebounding % (ORB%)
  * Net Rating (NRtg)
  * Strength of Schedule (SOS)
* Sanity Check: validated model stability by testing $\lambda_{1se}$ penalty

Technical Tools Used:
* Machine Learning: XGBoost, Random Forests, LASSO (L1 Regularization), CART
* Interpretability: SHAP (shapviz), Ceteris Paribus (dalex), Partial Dependence Plots (PDP)
* Environment: R (tidyverse, dplyr, xgboost, glmnet, rpart)

