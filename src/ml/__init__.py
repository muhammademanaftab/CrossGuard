"""Machine Learning Module for Cross Guard.

This module provides ML-based compatibility risk prediction that can predict
risk for NEW/UNKNOWN features not yet in the Can I Use database.

Key Components:
- FeatureExtractor: Extracts 25+ ML features from caniuse data
- RiskLabeler: Generates binary risk labels (HIGH/LOW)
- RiskPredictor: Inference API for risk predictions
- ModelTrainer: Training pipeline for ML models
- ModelEvaluator: Evaluation and comparison metrics
- Visualizations: Charts for thesis results
"""

from .feature_extractor import FeatureExtractor, extract_all_features
from .risk_labels import RiskLabeler, compute_risk_label
from .risk_predictor import RiskPredictor, get_risk_predictor
from .model_trainer import ModelTrainer, train_models
from .model_evaluator import ModelEvaluator, evaluate_models

__all__ = [
    # Feature extraction
    'FeatureExtractor',
    'extract_all_features',

    # Risk labeling
    'RiskLabeler',
    'compute_risk_label',

    # Risk prediction
    'RiskPredictor',
    'get_risk_predictor',

    # Model training
    'ModelTrainer',
    'train_models',

    # Model evaluation
    'ModelEvaluator',
    'evaluate_models',
]
