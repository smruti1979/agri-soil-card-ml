import os
import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder

def train_model_from_local_csv():
    csv_filename = "data\Crop_recommendation.csv"
    output_model_file = "saved_crop_model.joblib"
    
    # 1. Sanity check: Ensure the user placed the Kaggle file in the folder
    if not os.path.exists(csv_filename):
        print(f"❌ Error: '{csv_filename}' not found in your current working directory.")
        print("💡 Action: Please copy your downloaded Kaggle CSV file into this exact project folder and re-run.")
        return

    print(f"📊 Reading local dataset: '{csv_filename}'...")
    df = pd.read_csv(csv_filename)
    print(f"✅ Data imported successfully. Total records: {df.shape[0]} rows, across {df.shape[1]} columns.")
    
    # 2. Normalize dataset column names to lowercase to maintain modular alignment
    df.columns = [col.lower() for col in df.columns]
    
    # Standard Kaggle dataset feature layouts mapping
    required_features = ['n', 'p', 'k', 'ph', 'humidity', 'temperature', 'rainfall']
    
    # Verify all expected columns exist in the downloaded CSV file
    for feature in required_features + ['label']:
        if feature not in df.columns:
            print(f"❌ Error: Missing expected column '{feature}' in your CSV dataset profile.")
            return

    X = df[required_features]
    y = df['label']
    
    print("\n🌱 22-Crop Options found inside your Kaggle Dataset:")
    print(", ".join(sorted(y.unique())))

    # 3. Process categorical text labels into standard index arrays for XGBoost
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # 4. Train the High-Performance XGBoost Classifier Machine Learning Model
    print("\n🧠 Training High-Performance XGBoost Classifier Pipeline...")
    model = XGBClassifier(
        n_estimators=100, 
        max_depth=5, 
        learning_rate=0.1, 
        random_state=42,
        eval_metric='mlogloss'
    )
    model.fit(X, y_encoded)
    
    # 5. Save the structural matrix models and encoders together into a clean binary packet
    pipeline = {
        "model": model,
        "encoder": label_encoder,
        "features": required_features
    }
    
    joblib.dump(pipeline, output_model_file)
    print(f"✨ Production-Grade 22-Crop ML Pipeline successfully created from local CSV data: '{output_model_file}'")

if __name__ == "__main__":
    train_model_from_local_csv()
