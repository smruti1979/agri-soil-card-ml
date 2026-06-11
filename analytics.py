import os
import joblib
import pandas as pd
import httpx

class AgriAnalyticsEngine:
    def __init__(self):
        self.model_path = "saved_crop_model.joblib"
        self.model = None
        self.encoder = None
        self._load_production_model()

    def _load_production_model(self):
        """Safely extracts pre-trained pipeline binaries into local memory layout."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"❌ Model file '{self.model_path}' not found. Please execute 'python train_model.py' first!"
            )
        payload = joblib.load(self.model_path)
        self.model = payload["model"]
        self.encoder = payload["encoder"]
        print("🧠 Real 22-Crop XGBoost Machine Learning Pipeline safely deployed.")

    async def fetch_live_weather(self, lat: float, lon: float):
        """Fetches current location metrics using free Open-Meteo API."""
        url = f"https://open-meteo.com{lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m&daily=precipitation_sum&timezone=auto"
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(url, timeout=5.0)
                data = res.json()
                temp = data["current"]["temperature_2m"]
                humidity = data["current"]["relative_humidity_2m"]
                rainfall = (data["daily"]["precipitation_sum"] or 0.0) * 30
                return temp, humidity, rainfall
            except:
                return 27.2, 65.0, 115.0  # Fallback weather metrics

    def predict_crop(self, n, p, k, ph, humidity, temp, rainfall):
        """Runs predictions across 22 crops and returns the text label and probability score."""
        # Align features array to match the training dataframe format precisely
        input_df = pd.DataFrame(
            [[n, p, k, ph, humidity, temp, rainfall]], 
            columns=['n', 'p', 'k', 'ph', 'humidity', 'temperature', 'rainfall']
        )
        
        # Calculate matrix prediction indexes
        predicted_encoded = self.model.predict(input_df)
        probs = self.model.predict_proba(input_df)
        
        # Reverse encode the numerical class index back into plain text crop names
        crop_name = self.encoder.inverse_transform(predicted_encoded)[0]
        confidence = round(max(probs[0]) * 100, 1)
        
        return crop_name.capitalize(), confidence

    def calculate_optimization(self, crop, n, p, k, rainfall):
        """Provides generalized target agricultural baselines fallback calculations."""
        targets = {
            "Rice": {"n": 120, "p": 60, "k": 60, "base_yield": 4.2},
            "Maize": {"n": 100, "p": 50, "k": 40, "base_yield": 3.8},
            "Chickpeas": {"n": 30, "p": 60, "k": 30, "base_yield": 2.1},
            "Wheat": {"n": 90, "p": 45, "k": 40, "base_yield": 3.5},
            "Coffee": {"n": 100, "p": 40, "k": 80, "base_yield": 2.5},
            "Cotton": {"n": 120, "p": 40, "k": 40, "base_yield": 1.8},
            "Banana": {"n": 150, "p": 50, "k": 200, "base_yield": 15.0}
        }
        
        crop_target = targets.get(crop, {"n": 80, "p": 45, "k": 45, "base_yield": 3.2})
        
        deficits = {
            "urea": max(0, (crop_target["n"] - n) * 2.17),
            "dap": max(0, (crop_target["p"] - p) * 2.17),
            "mop": max(0, (crop_target["k"] - k) * 1.66)
        }
        
        weather_factor = 1.15 if rainfall > 110 else 0.90
        optimized_yield = round(crop_target["base_yield"] * weather_factor, 2)
        
        return optimized_yield, deficits
