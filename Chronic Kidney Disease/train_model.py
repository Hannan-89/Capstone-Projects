import pandas as pd
import numpy as np
import joblib
from sklearn.tree import DecisionTreeClassifier

def train_and_export_model():
    # Load dataset
    df = pd.read_csv('kidney_disease.csv')
    
    # Drop 'id' column as it's not a feature
    if 'id' in df.columns:
        df.drop('id', axis=1, inplace=True)

    # Clean categorical typos
    df['classification'] = df['classification'].replace(to_replace={'ckd\t': 'ckd', 'notckd': 'notckd'})
    df['cad'] = df['cad'].replace(to_replace='\tno', value='no')
    df['dm'] = df['dm'].replace(to_replace={'\tno': 'no', '\tyes': 'yes', ' yes': 'yes'})

    # Handle numeric columns with string noise
    def convert_to_numeric(val):
        if isinstance(val, str):
            val = val.replace('\t', '').replace('?', '')
            try:
                return float(val)
            except ValueError:
                return np.nan
        return val

    df['rc'] = df['rc'].apply(convert_to_numeric)
    df['wc'] = df['wc'].apply(convert_to_numeric)
    df['pcv'] = df['pcv'].apply(convert_to_numeric)

    # Split columns into numerical and categorical
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    cat_cols = df.select_dtypes(exclude=['int64', 'float64']).columns

    # Imputation values (to be saved for inference)
    impute_values = {}
    for col in num_cols:
        impute_values[col] = df[col].mean()
        df[col] = df[col].fillna(impute_values[col])
    
    for col in cat_cols:
        impute_values[col] = df[col].mode()[0]
        df[col] = df[col].fillna(impute_values[col])

    # Convert types
    df['rc'] = df['rc'].astype('float64')
    df['wc'] = df['wc'].astype('int64')
    df['pcv'] = df['pcv'].astype('int64')

    # Separate features and target
    X = df.drop('classification', axis=1)
    y = df['classification']

    # Target encoding: ckd -> 0, notckd -> 1 (consistent with notebooks's get_dummies approach)
    y = y.map({'ckd': 0, 'notckd': 1})

    # Save feature names for inference alignment
    feature_columns = X.columns.tolist()
    
    # Identify categorical features for dummy encoding
    categorical_features = X.select_dtypes(include=['object']).columns.tolist()

    # One-hot encoding
    X_encoded = pd.get_dummies(X, columns=categorical_features, drop_first=True)
    final_columns = X_encoded.columns.tolist()

    # Train model
    model = DecisionTreeClassifier()
    model.fit(X_encoded, y)

    # Export model and metadata
    metadata = {
        'num_cols': num_cols.tolist(),
        'cat_cols': cat_cols.drop('classification').tolist() if 'classification' in cat_cols else cat_cols.tolist(),
        'impute_values': impute_values,
        'categorical_features': categorical_features,
        'final_columns': final_columns,
        'target_map': {0: 'ckd', 1: 'notckd'}
    }

    joblib.dump(model, 'model.joblib')
    joblib.dump(metadata, 'metadata.joblib')
    print("Model and metadata exported successfully.")

if __name__ == "__main__":
    train_and_export_model()
