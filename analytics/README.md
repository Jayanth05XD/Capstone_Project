# Module 2 — Analytics (`/analytics`)

This module focuses on exploratory data analysis, data preprocessing, classification, and regression using the Titanic dataset.

The work is organized into two Jupyter notebooks:

| Notebook | Purpose |
|---|---|
| `01_eda.ipynb` | Data loading, profiling, cleaning, exploratory analysis, visualization, and preprocessing |
| `02_modeling.ipynb` | Classification, imbalance handling, model evaluation, hyperparameter tuning, and regression |

## Project Overview

The objective of this module is to understand the Titanic dataset through exploratory data analysis and then build machine-learning models to predict passenger survival.

**Workflow:** Data Loading → Data Cleaning → EDA → Feature Analysis → Train/Test Split → Preprocessing → Classification → Model Evaluation → Imbalance Handling → Hyperparameter Tuning → Regression → Model Comparison

---

# `01_eda.ipynb` — Exploratory Data Analysis

The first notebook focuses on understanding and preparing the Titanic dataset before moving into machine learning.

## Dataset Loading and Profiling

The Titanic dataset is loaded using Seaborn:

```python
df = sns.load_dataset("titanic")
```

Initial profiling includes:

- Dataset shape
- Data types
- Non-null counts
- Descriptive statistics
- Missing-value percentages

The original dataset contains **891 rows** and **15 columns**.

Important missing values were identified in:

- `age`
- `embarked`
- `embark_town`
- `deck`

## Missing-Value Analysis

Missing values were examined column by column and handled according to their percentage of missing data.

The main decisions were:

- Very small amounts of missing data → remove affected rows
- Moderate missing data → impute using an appropriate statistic
- Very high missing data → remove the column when it was not useful for the analysis

For numerical variables such as `age`, median imputation was used where required.

The `deck` column contained a very large proportion of missing values and was removed from the cleaned analytical dataset.

After cleaning, the resulting dataset contains **889 observations**.

## Univariate Analysis

The distributions of `age` and `fare` were investigated using:

- Histograms
- KDE plots
- Box plots
- IQR-based outlier detection

The analysis identified:

- **65 age outliers**
- **114 fare outliers**

Fare showed strong right skewness.

```text
Mean:       32.10
Median:     14.45
Mode:        8.05
Skewness:    4.801
```

## Survival Analysis

Survival rates were examined across:

- Sex
- Passenger class
- Sex and passenger class together

These comparisons help identify relationships between passenger characteristics and survival outcomes.

## Correlation Analysis

A correlation matrix was created using:

```text
survived
pclass
age
sibsp
parch
fare
```

A heatmap was generated to visualize relationships between these variables, and the strongest correlations were identified programmatically.

## Standardization

`age` and `fare` were standardized using `StandardScaler`.

After standardization, both variables had approximately:

```text
Mean = 0
Standard deviation = 1
```

Example:

```text
Age:
Before → mean ≈ 29.315
After  → mean ≈ 0.000

Fare:
Before → mean ≈ 32.097
After  → mean ≈ 0.000
```

---

# `02_modeling.ipynb` — Machine Learning

The second notebook uses the cleaned Titanic dataset to build and compare classification models and perform a regression side task.

The cleaned data is loaded from:

```text
titanic.csv
```

## Train/Test Split

The target variable is:

```text
survived
```

A stratified train/test split was used:

```python
train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
```

Dataset split:

```text
Training samples: 712
Testing samples: 179
```

Training class distribution:

```text
0    439
1    273
```

## Data Preprocessing

A `ColumnTransformer` was used to process numerical and categorical features.

### Numerical features

```text
age
fare
sibsp
parch
```

Processing:

1. Median imputation
2. Standard scaling

### Categorical features

```text
sex
embarked
```

Processing:

1. Most-frequent imputation
2. One-hot encoding

---

# Classification Models

Three classification algorithms were evaluated:

- Logistic Regression
- Decision Tree
- Random Forest

All models were evaluated using the same train/test split.

## Final Classification Results

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.7989 | 0.7797 | 0.6667 | 0.7188 | 0.8194 |
| **Decision Tree** | **0.8101** | **0.7966** | **0.6812** | **0.7344** | **0.8309** |
| Random Forest | 0.7821 | 0.7500 | 0.6522 | 0.6977 | 0.8184 |

The Decision Tree achieved the best final test-set performance:

```text
Accuracy:   81.01%
Precision:  79.66%
Recall:     68.12%
F1 Score:   73.44%
ROC-AUC:    0.8309
```

## Class Imbalance Analysis

Three Random Forest strategies were compared:

1. Baseline Random Forest
2. `class_weight="balanced"`
3. SMOTE

| Strategy | Precision | Recall | F1 Score |
|---|---:|---:|---:|
| Baseline | 0.7667 | 0.6667 | 0.7132 |
| Class Weight = Balanced | 0.7586 | 0.6377 | 0.6929 |
| SMOTE | 0.6857 | 0.6957 | 0.6906 |

SMOTE changed the training distribution from:

```text
0 → 439
1 → 273
```

to:

```text
0 → 439
1 → 439
```

The comparison shows that increasing recall through oversampling does not necessarily produce a higher F1 score.

## Random Forest Hyperparameter Tuning

`GridSearchCV` was used to tune:

- `n_estimators`
- `max_depth`
- `max_features`

Best configuration:

```text
max_depth:     5
max_features:  sqrt
n_estimators:  100
```

Best cross-validation accuracy:

```text
0.8161
```

OOB score:

```text
0.8146
```

## Decision Tree Visualization

The Decision Tree was visualized using `plot_tree`, displaying feature names, class names, decision splits, and node information.

Test accuracy:

```text
0.8101
```

## ROC Curve Analysis

ROC curves were generated for all three classifiers.

```text
Logistic Regression: 0.8194
Decision Tree:       0.8309
Random Forest:       0.8184
```

The Decision Tree achieved the highest ROC-AUC.

---

# Regression Side Task

A regression model was used to predict `fare`.

Evaluation metrics:

- MAE
- RMSE
- R²
- Adjusted R²

Results:

```text
MAE:         21.4833
RMSE:        34.5198
R²:           0.2299
Adjusted R²:  0.1642
```

Residual statistics:

```text
Mean residual:   -4.2958
Std residual:    34.3475
Min residual:    -68.8944
Max residual:    206.5498
```

The R² value indicates that the selected features explain only part of the variation in passenger fare.

---

# Project Outputs

The notebooks generate analytical outputs including:

- EDA visualizations
- Survival-rate charts
- Correlation heatmap
- Standardization plots
- Decision Tree visualization
- ROC curves
- Confusion matrices
- Regression prediction and residual plots

Generated outputs are excluded from version control through `.gitignore`.

---

# How to Run

From the project root, activate the virtual environment:

```powershell
.venv\Scripts\activate
```

Install the required dependencies:

```powershell
pip install -r requirements.txt
```

Open the notebooks:

```text
analytics/
├── 01_eda.ipynb
├── 02_modeling.ipynb
└── README.md
```

Run them in this order:

```text
01_eda.ipynb
      ↓
02_modeling.ipynb
```

---

# Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Imbalanced-learn
- Jupyter Notebook

Machine-learning techniques used:

- Data preprocessing
- Standardization
- One-hot encoding
- Logistic Regression
- Decision Tree
- Random Forest
- SMOTE
- GridSearchCV
- ROC-AUC analysis
- Linear Regression
- Residual analysis

---

# Conclusion

This analytics module demonstrates a complete workflow from exploratory analysis through machine-learning evaluation.

The Titanic dataset shows meaningful differences in survival outcomes across passenger characteristics. Multiple classification approaches were evaluated using a common preprocessing workflow.

Among the tested classifiers, the **Decision Tree performed best on the final test set**, achieving **81.01% accuracy** and **0.8309 ROC-AUC**.

The regression experiment achieved an **R² of 0.2299**, indicating that predicting fare from the selected features is more difficult than predicting survival.

Overall, the project demonstrates practical skills in data cleaning, exploratory analysis, feature preprocessing, classification, model comparison, hyperparameter tuning, and regression using Python.
