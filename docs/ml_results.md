# Machine Learning Results

## Target Variable

The machine-learning model predicts the target variable:

```text
is_suspicious
```

A value of `0` means the login is normal. A value of `1` means the login is suspicious.

## Class Imbalance

The dataset contains more normal logins than suspicious logins. This creates class imbalance because the model may learn to predict the majority class more often.

Class imbalance summary:

| Dataset | Class | Count |
|---|---|---:|
| Train | Normal | ENTER_VALUE |
| Train | Suspicious | ENTER_VALUE |
| Test | Normal | ENTER_VALUE |
| Test | Suspicious | ENTER_VALUE |

Because cybersecurity detection depends on catching suspicious logins, balanced class weights were tested. Balanced class weights help the model pay more attention to the minority class.

## Models Compared

The following models were trained and compared:

- Logistic Regression
- Logistic Regression with balanced class weights
- Decision Tree
- Decision Tree with balanced class weights
- Random Forest
- Random Forest with balanced class weights

## Model Comparison Results

| Model | Accuracy | Precision | Recall | F1 Score | False Positives | False Negatives |
|---|---:|---:|---:|---:|---:|---:|
| ENTER_MODEL | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE |
| ENTER_MODEL | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE |
| ENTER_MODEL | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE | ENTER_VALUE |

## Best Model Selected

The best model selected was:

```text
ENTER_BEST_MODEL_NAME
```

The best model was selected mainly based on F1 score. Recall was also important because in cybersecurity, a false negative means a suspicious login was incorrectly classified as normal.

## Confusion Matrix Interpretation

The confusion matrix shows four outcomes:

| Outcome | Meaning |
|---|---|
| True Negative | Normal login correctly predicted as normal |
| False Positive | Normal login incorrectly predicted as suspicious |
| False Negative | Suspicious login incorrectly predicted as normal |
| True Positive | Suspicious login correctly predicted as suspicious |

False negatives are especially important in this project because they represent missed threats.

## Feature Importance

The most important model features were:

| Rank | Feature | Importance |
|---:|---|---:|
| 1 | ENTER_FEATURE | ENTER_VALUE |
| 2 | ENTER_FEATURE | ENTER_VALUE |
| 3 | ENTER_FEATURE | ENTER_VALUE |
| 4 | ENTER_FEATURE | ENTER_VALUE |
| 5 | ENTER_FEATURE | ENTER_VALUE |

These features are important because they represent strong login-security signals such as failed attempts, suspicious IP usage, impossible travel, no MFA, foreign login behavior, and unusual login timing.

## Results Summary

The baseline machine-learning models were able to learn suspicious login patterns from the synthetic dataset. Models with balanced class weights were tested to reduce the impact of class imbalance.

The selected model performed best overall based on F1 score while still maintaining strong recall. This makes it a good baseline model for identifying suspicious login activity.

## Limitations

These results are based on synthetic data, not real enterprise login data. The suspicious labels are scenario-based, which means some patterns may be easier for the model to learn than they would be in the real world.

The model may also learn patterns that are specific to how the synthetic data generator created attacks. For example, if suspicious IPs or failed attempts are strongly tied to suspicious labels, the model may rely heavily on those features.

Future improvements should include more realistic user behavior history, real geographic distance calculations, time-based user baselines, real IP reputation data, and testing on more diverse login scenarios.