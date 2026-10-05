"""
Model loader - Singleton pattern to load ML model once and reuse
"""
import pickle
import os
from backend.config import settings

class ModelLoader:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def load_model(self):
        """Load the trained model from disk"""
        if self._model is None:
            model_path = settings.MODEL_PATH
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self._model = pickle.load(f)
                print(f"✓ Model loaded successfully from {model_path}")
                # Log model info
                if hasattr(self._model, 'feature_names_in_'):
                    print(f"  Features: {list(self._model.feature_names_in_)}")
                if hasattr(self._model, 'n_features_in_'):
                    print(f"  Feature count: {self._model.n_features_in_}")
            else:
                print(f"⚠ Warning: Model not found at {model_path}")
                self._model = None
        return self._model

    @property
    def model(self):
        """Get the loaded model"""
        if self._model is None:
            self.load_model()
        return self._model

    @property
    def feature_names(self):
        """Get feature names from the model"""
        if self.model and hasattr(self.model, 'feature_names_in_'):
            return list(self.model.feature_names_in_)
        return ['debt_to_income_ratio', 'avg_monthly_balance', 'months_delinquent']

# Global instance
model_loader = ModelLoader()
