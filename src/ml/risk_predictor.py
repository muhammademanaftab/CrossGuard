"""Risk Predictor for ML-based Compatibility Risk Prediction.

This module provides the inference API for predicting compatibility
risk using trained ML models. It can predict risk for both known
features (in Can I Use) and unknown/new features.

Key Features:
- Load pretrained models
- Predict risk with confidence scores
- Identify contributing factors
- Fallback to heuristics when model unavailable
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
import numpy as np

from ..utils.config import get_logger, CANIUSE_FEATURES_PATH
from .feature_extractor import (
    FeatureExtractor,
    extract_features_for_unknown,
    FEATURE_NAMES,
)
from .risk_labels import RiskLabeler, compute_risk_label

logger = get_logger('ml.risk_predictor')

# Import joblib for model loading
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

# Pretrained model directory
PRETRAINED_DIR = Path(__file__).parent / 'pretrained'


class RiskCategory(Enum):
    """Risk category classifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class RiskPrediction:
    """Result of a risk prediction.

    Attributes:
        feature_id: Feature identifier
        risk_level: Predicted risk category (LOW/MEDIUM/HIGH)
        confidence: Prediction confidence (0.0 - 1.0)
        probability_high_risk: Raw probability of HIGH risk
        contributing_factors: List of factors influencing the prediction
        model_used: Name of model used for prediction
        is_known_feature: Whether feature exists in Can I Use
    """
    feature_id: str
    risk_level: RiskCategory
    confidence: float
    probability_high_risk: float
    contributing_factors: List[str]
    model_used: str
    is_known_feature: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'feature_id': self.feature_id,
            'risk_level': self.risk_level.value,
            'confidence': self.confidence,
            'probability_high_risk': self.probability_high_risk,
            'contributing_factors': self.contributing_factors,
            'model_used': self.model_used,
            'is_known_feature': self.is_known_feature,
        }


class RiskPredictor:
    """ML-based risk predictor for browser compatibility.

    This class provides the main inference API for the ML module.
    It loads pretrained models and provides predictions with explanations.
    """

    def __init__(
        self,
        model_name: str = 'random_forest',
        pretrained_dir: Optional[Path] = None,
    ):
        """Initialize the risk predictor.

        Args:
            model_name: Name of model to use ('random_forest', 'logistic_regression', 'gradient_boosting')
            pretrained_dir: Directory containing pretrained models
        """
        self.model_name = model_name
        self.pretrained_dir = pretrained_dir or PRETRAINED_DIR

        self.model = None
        self.scaler = None
        self.feature_extractor = FeatureExtractor()
        self.rule_labeler = RiskLabeler()

        self._feature_data_cache: Dict[str, Dict] = {}
        self._model_loaded = False

        # Try to load model
        self._load_model()

    def _load_model(self) -> bool:
        """Load pretrained model and scaler.

        Returns:
            True if model loaded successfully
        """
        if not JOBLIB_AVAILABLE:
            logger.warning("joblib not available, using rule-based fallback")
            return False

        model_path = self.pretrained_dir / f'{self.model_name}.joblib'
        scaler_path = self.pretrained_dir / 'feature_scaler.joblib'

        if not model_path.exists():
            logger.warning(f"Model not found at {model_path}, using rule-based fallback")
            return False

        try:
            self.model = joblib.load(model_path)
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
            self._model_loaded = True
            logger.info(f"Loaded model: {self.model_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def _load_feature_data(self, feature_id: str) -> Optional[Dict]:
        """Load feature data from Can I Use database.

        Args:
            feature_id: Feature identifier

        Returns:
            Feature data dict or None if not found
        """
        if feature_id in self._feature_data_cache:
            return self._feature_data_cache[feature_id]

        feature_path = Path(CANIUSE_FEATURES_PATH) / f'{feature_id}.json'

        if not feature_path.exists():
            return None

        try:
            with open(feature_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._feature_data_cache[feature_id] = data
            return data
        except Exception as e:
            logger.warning(f"Failed to load feature {feature_id}: {e}")
            return None

    def predict(self, feature_id: str) -> RiskPrediction:
        """Predict risk for a known feature.

        Args:
            feature_id: Feature identifier (e.g., 'css-grid', 'flexbox')

        Returns:
            RiskPrediction with risk level and explanations
        """
        # Load feature data
        feature_data = self._load_feature_data(feature_id)

        if feature_data is None:
            return self._predict_unknown_feature(feature_id)

        # Extract features
        features = self.feature_extractor.extract_features(feature_data)

        # Use ML model if available
        if self._model_loaded:
            return self._predict_with_model(feature_id, features, feature_data)
        else:
            return self._predict_with_rules(feature_id, feature_data)

    def predict_unknown(
        self,
        feature_id: str,
        spec_status: str = 'wd',
        category: str = 'CSS',
        browsers_implementing: int = 1,
        has_polyfill: bool = False,
        complexity: str = 'medium',
    ) -> RiskPrediction:
        """Predict risk for an unknown/new feature.

        This is the key thesis contribution: predicting risk for features
        NOT in the Can I Use database.

        Args:
            feature_id: Identifier for the new feature
            spec_status: Specification status ('rec', 'cr', 'wd', 'unoff')
            category: Feature category ('CSS', 'JS', 'HTML5')
            browsers_implementing: Number of browsers implementing
            has_polyfill: Whether a polyfill is available
            complexity: Complexity level ('low', 'medium', 'high')

        Returns:
            RiskPrediction with risk level and explanations
        """
        # Generate features for unknown feature
        features = extract_features_for_unknown(
            spec_status=spec_status,
            category=category,
            browsers_implementing=browsers_implementing,
            has_polyfill=has_polyfill,
            complexity=complexity,
        )

        if self._model_loaded:
            # Scale features
            if self.scaler is not None:
                features_scaled = self.scaler.transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)

            # Predict
            prob = self.model.predict_proba(features_scaled)[0, 1]

            # Determine risk level and confidence
            risk_level, confidence = self._probability_to_risk_level(prob)

            # Generate contributing factors
            contributing_factors = self._explain_unknown_prediction(
                spec_status, browsers_implementing, has_polyfill, complexity
            )

            return RiskPrediction(
                feature_id=feature_id,
                risk_level=risk_level,
                confidence=confidence,
                probability_high_risk=float(prob),
                contributing_factors=contributing_factors,
                model_used=self.model_name,
                is_known_feature=False,
            )

        else:
            # Heuristic prediction for unknown features
            return self._predict_unknown_heuristic(
                feature_id, spec_status, browsers_implementing, has_polyfill
            )

    def _predict_unknown_feature(self, feature_id: str) -> RiskPrediction:
        """Handle prediction request for feature not in database.

        Args:
            feature_id: Feature identifier

        Returns:
            RiskPrediction with unknown feature warning
        """
        return RiskPrediction(
            feature_id=feature_id,
            risk_level=RiskCategory.HIGH,
            confidence=0.5,
            probability_high_risk=0.75,
            contributing_factors=[
                f"Feature '{feature_id}' not found in Can I Use database",
                "Unknown features are considered HIGH risk by default",
                "Use predict_unknown() with feature metadata for better prediction"
            ],
            model_used='fallback',
            is_known_feature=False,
        )

    def _predict_with_model(
        self,
        feature_id: str,
        features: np.ndarray,
        feature_data: Dict,
    ) -> RiskPrediction:
        """Predict using trained ML model.

        Args:
            feature_id: Feature identifier
            features: Extracted feature vector
            feature_data: Raw feature data for explanations

        Returns:
            RiskPrediction
        """
        # Scale features
        if self.scaler is not None:
            features_scaled = self.scaler.transform(features.reshape(1, -1))
        else:
            features_scaled = features.reshape(1, -1)

        # Get prediction probability
        prob = self.model.predict_proba(features_scaled)[0, 1]

        # Convert to risk level with confidence
        risk_level, confidence = self._probability_to_risk_level(prob)

        # Get feature importances for explanation
        contributing_factors = self._explain_prediction(features, feature_data)

        return RiskPrediction(
            feature_id=feature_id,
            risk_level=risk_level,
            confidence=confidence,
            probability_high_risk=float(prob),
            contributing_factors=contributing_factors,
            model_used=self.model_name,
            is_known_feature=True,
        )

    def _predict_with_rules(
        self,
        feature_id: str,
        feature_data: Dict,
    ) -> RiskPrediction:
        """Predict using rule-based system (fallback).

        Args:
            feature_id: Feature identifier
            feature_data: Raw feature data

        Returns:
            RiskPrediction
        """
        label, factors = self.rule_labeler.compute_label(feature_data)
        reasons = factors.to_reasons()

        risk_level = RiskCategory.HIGH if label == 1 else RiskCategory.LOW
        confidence = 0.8 if factors.risk_count() >= 3 else 0.6

        return RiskPrediction(
            feature_id=feature_id,
            risk_level=risk_level,
            confidence=confidence,
            probability_high_risk=float(label),
            contributing_factors=reasons if reasons else ["Feature is widely supported"],
            model_used='rule_based',
            is_known_feature=True,
        )

    def _probability_to_risk_level(
        self, prob: float
    ) -> Tuple[RiskCategory, float]:
        """Convert probability to risk level and confidence.

        Args:
            prob: Probability of HIGH risk (0.0 - 1.0)

        Returns:
            Tuple of (RiskCategory, confidence)
        """
        if prob >= 0.7:
            return RiskCategory.HIGH, min(prob, 0.95)
        elif prob >= 0.4:
            return RiskCategory.MEDIUM, 0.5 + abs(prob - 0.5)
        else:
            return RiskCategory.LOW, min(1.0 - prob, 0.95)

    def _explain_prediction(
        self,
        features: np.ndarray,
        feature_data: Dict,
    ) -> List[str]:
        """Generate human-readable explanation of prediction.

        Only shows RISK FACTORS (negative things), not positive factors.

        Args:
            features: Feature vector
            feature_data: Raw feature data

        Returns:
            List of contributing factor explanations (risk factors only)
        """
        risk_factors = []

        # RISK: Low global usage
        usage_y = feature_data.get('usage_perc_y', 0)
        if usage_y < 90:
            risk_factors.append(f"Low global usage: {usage_y:.1f}% (below 90% threshold)")

        # RISK: Unstable specification status
        status = feature_data.get('status', 'unknown')
        status_risk_names = {
            'wd': 'Working Draft - specification may change',
            'unoff': 'Unofficial/experimental - not standardized',
            'other': 'Non-standard specification status',
        }
        if status in ['wd', 'unoff', 'other']:
            risk_factors.append(f"Unstable spec: {status_risk_names.get(status, status)}")

        # RISK: Many browser bugs
        bugs = feature_data.get('bugs', [])
        if len(bugs) > 0:
            risk_factors.append(f"{len(bugs)} known browser bug{'s' if len(bugs) > 1 else ''}")

        # RISK: Inconsistent browser support
        if features[16] > 0.1:  # support_variance
            risk_factors.append("Inconsistent behavior across browsers")

        # RISK: Not fully supported in all browsers
        browsers_full = features[13] if len(features) > 13 else 0  # browsers_full_support
        if browsers_full < 4:
            risk_factors.append(f"Only {int(browsers_full)} browsers have full support")

        # RISK: Has partial support issues
        browsers_partial = features[14] if len(features) > 14 else 0  # browsers_partial_support
        if browsers_partial > 2:
            risk_factors.append(f"{int(browsers_partial)} browsers have only partial support")

        # If no risk factors found, the model found patterns we didn't explicitly check
        if not risk_factors:
            # Check if this is actually high risk based on probability
            risk_factors.append("ML model detected risk patterns in feature characteristics")

        return risk_factors

    def _explain_unknown_prediction(
        self,
        spec_status: str,
        browsers_implementing: int,
        has_polyfill: bool,
        complexity: str,
    ) -> List[str]:
        """Generate explanation for unknown feature prediction.

        Args:
            spec_status: Specification status
            browsers_implementing: Number of browsers implementing
            has_polyfill: Whether polyfill exists
            complexity: Complexity level

        Returns:
            List of explanations
        """
        explanations = []

        if spec_status in ['wd', 'unoff']:
            explanations.append(f"Early specification stage: {spec_status}")

        if browsers_implementing < 3:
            explanations.append(f"Limited browser support ({browsers_implementing} browsers)")

        if not has_polyfill and browsers_implementing < 4:
            explanations.append("No polyfill available")

        if complexity == 'high':
            explanations.append("Complex feature may have implementation variations")

        if not explanations:
            explanations.append("Feature characteristics suggest reasonable compatibility")

        return explanations

    def _predict_unknown_heuristic(
        self,
        feature_id: str,
        spec_status: str,
        browsers_implementing: int,
        has_polyfill: bool,
    ) -> RiskPrediction:
        """Heuristic prediction when model not available.

        Args:
            feature_id: Feature identifier
            spec_status: Specification status
            browsers_implementing: Number of browsers
            has_polyfill: Whether polyfill exists

        Returns:
            RiskPrediction
        """
        # Simple scoring heuristic
        risk_score = 0

        if spec_status in ['wd', 'unoff']:
            risk_score += 2
        if browsers_implementing < 2:
            risk_score += 2
        elif browsers_implementing < 4:
            risk_score += 1
        if not has_polyfill and browsers_implementing < 4:
            risk_score += 1

        if risk_score >= 3:
            risk_level = RiskCategory.HIGH
            prob = 0.8
        elif risk_score >= 2:
            risk_level = RiskCategory.MEDIUM
            prob = 0.5
        else:
            risk_level = RiskCategory.LOW
            prob = 0.2

        return RiskPrediction(
            feature_id=feature_id,
            risk_level=risk_level,
            confidence=0.6,
            probability_high_risk=prob,
            contributing_factors=self._explain_unknown_prediction(
                spec_status, browsers_implementing, has_polyfill, 'medium'
            ),
            model_used='heuristic',
            is_known_feature=False,
        )

    def predict_batch(
        self,
        feature_ids: List[str],
    ) -> Dict[str, RiskPrediction]:
        """Predict risk for multiple features.

        Args:
            feature_ids: List of feature identifiers

        Returns:
            Dict mapping feature_id to RiskPrediction
        """
        predictions = {}

        for feature_id in feature_ids:
            predictions[feature_id] = self.predict(feature_id)

        return predictions

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance scores from model.

        Returns:
            Dict mapping feature names to importance scores,
            or None if not available
        """
        if not self._model_loaded:
            return None

        if hasattr(self.model, 'feature_importances_'):
            return {
                name: float(imp)
                for name, imp in zip(FEATURE_NAMES, self.model.feature_importances_)
            }
        elif hasattr(self.model, 'coef_'):
            return {
                name: float(abs(coef))
                for name, coef in zip(FEATURE_NAMES, self.model.coef_[0])
            }

        return None

    def is_model_loaded(self) -> bool:
        """Check if ML model is loaded.

        Returns:
            True if model is available
        """
        return self._model_loaded


# Singleton instance
_predictor_instance: Optional[RiskPredictor] = None


def get_risk_predictor(model_name: str = 'gradient_boosting') -> RiskPredictor:
    """Get or create the singleton risk predictor instance.

    Args:
        model_name: Name of model to use

    Returns:
        RiskPredictor instance
    """
    global _predictor_instance

    if _predictor_instance is None or _predictor_instance.model_name != model_name:
        _predictor_instance = RiskPredictor(model_name=model_name)

    return _predictor_instance


def predict_feature_risk(feature_id: str) -> RiskPrediction:
    """Convenience function to predict risk for a single feature.

    Args:
        feature_id: Feature identifier

    Returns:
        RiskPrediction
    """
    predictor = get_risk_predictor()
    return predictor.predict(feature_id)


def predict_features_risk(feature_ids: Set[str]) -> Dict[str, RiskPrediction]:
    """Predict risk for multiple features.

    Args:
        feature_ids: Set of feature identifiers

    Returns:
        Dict mapping feature_id to RiskPrediction
    """
    predictor = get_risk_predictor()
    return predictor.predict_batch(list(feature_ids))


# Model display names for UI
MODEL_DISPLAY_NAMES = {
    'gradient_boosting': 'Gradient Boosting',
    'random_forest': 'Random Forest',
    'logistic_regression': 'Logistic Regression',
}

MODEL_ACCURACIES = {
    'gradient_boosting': 0.93,
    'random_forest': 0.904,
    'logistic_regression': 0.886,
}


def get_all_models_prediction(feature_id: str) -> Dict[str, Dict]:
    """Get predictions from all 3 models for comparison.

    Args:
        feature_id: Feature identifier

    Returns:
        Dict with predictions from each model
    """
    results = {}

    for model_name in ['gradient_boosting', 'random_forest', 'logistic_regression']:
        try:
            predictor = RiskPredictor(model_name=model_name)
            if predictor.is_model_loaded():
                pred = predictor.predict(feature_id)
                results[model_name] = {
                    'risk_level': pred.risk_level.value,
                    'confidence': pred.confidence,
                    'probability': pred.probability_high_risk,
                    'display_name': MODEL_DISPLAY_NAMES[model_name],
                    'accuracy': MODEL_ACCURACIES[model_name],
                }
        except Exception:
            pass

    return results


def get_all_models_aggregate(feature_ids: List[str], full_analysis: bool = True) -> Dict[str, Any]:
    """Get aggregate predictions from all 3 models.

    Args:
        feature_ids: List of feature identifiers
        full_analysis: If True, analyze all features (slower but accurate)

    Returns:
        Dict with aggregate results from each model and consensus info
    """
    all_results = {
        'gradient_boosting': {'high': 0, 'medium': 0, 'low': 0, 'predictions': []},
        'random_forest': {'high': 0, 'medium': 0, 'low': 0, 'predictions': []},
        'logistic_regression': {'high': 0, 'medium': 0, 'low': 0, 'predictions': []},
    }

    # Analyze all features for accurate results in advanced view
    features_to_analyze = feature_ids if full_analysis else feature_ids[:10]

    for model_name in all_results.keys():
        try:
            predictor = RiskPredictor(model_name=model_name)
            if not predictor.is_model_loaded():
                continue

            for fid in features_to_analyze:
                try:
                    pred = predictor.predict(fid)
                    risk = pred.risk_level.value
                    all_results[model_name][risk] += 1
                    all_results[model_name]['predictions'].append({
                        'feature': fid,
                        'risk': risk,
                        'confidence': pred.confidence,
                        'reason': pred.contributing_factors[0] if pred.contributing_factors else 'Risk detected by ML model',
                    })
                except Exception:
                    continue
        except Exception:
            continue

    # Calculate overall risk for each model
    model_summaries = {}
    for model_name, counts in all_results.items():
        total = counts['high'] + counts['medium'] + counts['low']
        if total == 0:
            continue

        # Determine overall risk
        if counts['high'] > total * 0.3:
            overall_risk = 'high'
        elif counts['high'] > 0 or counts['medium'] > total * 0.3:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'

        # Get actual flagged features (HIGH and MEDIUM risk)
        flagged_predictions = [p for p in counts['predictions'] if p['risk'] in ['high', 'medium']]

        # Calculate average confidence from all predictions
        all_confidences = [p['confidence'] for p in counts['predictions'] if 'confidence' in p]
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.5

        model_summaries[model_name] = {
            'overall_risk': overall_risk,
            'high_count': counts['high'],
            'medium_count': counts['medium'],
            'low_count': counts['low'],
            'display_name': MODEL_DISPLAY_NAMES[model_name],
            'predictions': flagged_predictions,  # Only include flagged features
            'avg_confidence': avg_confidence,  # Real confidence from model
            'accuracy': MODEL_ACCURACIES.get(model_name, 0.0),  # Model's test accuracy
        }

    # Calculate consensus
    risk_votes = [s['overall_risk'] for s in model_summaries.values()]
    if risk_votes:
        from collections import Counter
        vote_counts = Counter(risk_votes)
        consensus_risk, consensus_count = vote_counts.most_common(1)[0]
        total_models = len(risk_votes)
    else:
        consensus_risk = 'unknown'
        consensus_count = 0
        total_models = 0

    return {
        'models': model_summaries,
        'consensus': {
            'risk': consensus_risk,
            'agreement': f"{consensus_count}/{total_models}",
            'models_agree': consensus_count,
            'total_models': total_models,
        },
        'best_model': 'gradient_boosting',
    }
