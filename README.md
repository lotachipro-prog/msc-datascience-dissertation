# FTSE ESG Anomaly Intelligence Platform

**MSc Data Science Dissertation — Lota Anene — 2026**

Cross-modal greenwashing detection for UK FTSE-listed firms combining
NLP text analysis, verified NAEI government emissions data, and
Sentinel-5P TROPOMI satellite observation.

## Live Dashboard
https://lotachipro-prog-msc-datascience-dissertation.streamlit.app

## Anchor Paper
ESG-washing detection in corporate sustainability reports
International Review of Financial Analysis (2024) | IF: 9.8 | SCIE Verified
DOI: 10.1016/j.irfa.2024.103553

## Key Results
- ROC-AUC: 0.881 (leak-free LOO-CV)
- Recall: 0.800 (4 of 5 confirmed greenwashing cases detected)
- F1: 0.615
- Dataset: 37 company-year observations, 11 UK FTSE companies, 2019-2025
- Labels: 5 confirmed regulatory actions (ASA, FCA, CMA)

## Three Contributions
1. Original matched dataset: UK FTSE NLP features + NAEI emissions + regulatory labels
2. Extended ESGSI: Cross-Modal Divergence Index with sigmoid-weighted formula
3. Satellite verification: Sentinel-5P TROPOMI NO2 case study (Drax 2023, 1.40x background)

## Technical Stack
- ClimateBERT (distilroberta-base-climate-f) for semantic embeddings
- Logistic Regression with leak-free sklearn Pipeline
- Leave-One-Out Cross-Validation
- NAEI Large Point Sources 2023 (UK DESNZ)
- Google Earth Engine + Sentinel-5P TROPOMI

## Dashboard Tabs
1. Market Anomaly Matrix: Cross-modal scatter plot and risk leaderboard
2. Company Profiler: Trajectory analysis and regulatory status
3. Live Report Scanner: Upload any PDF for instant risk assessment
4. Satellite Verification: Drax Group 2023 cross-modal case study
