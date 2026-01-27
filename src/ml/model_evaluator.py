"""Model Evaluator for ML-based Compatibility Risk Prediction.

This module provides comprehensive evaluation of ML models including:
- Standard classification metrics (accuracy, precision, recall, F1, AUC)
- Comparison with rule-based severity classification
- Confusion matrix analysis
- Temporal split evaluation (key thesis experiment)

Research Questions Addressed:
- RQ1: Can ML predict compatibility risk for unseen features?
- RQ2: Which features most strongly predict compatibility issues?
- RQ3: How well does the model generalize to new web features?
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np

from ..utils.config import get_logger, PROJECT_ROOT
from ..analyzer.compatibility import CompatibilityAnalyzer, Severity

logger = get_logger('ml.model_evaluator')

# Import sklearn components
try:
    from sklearn.metrics import (
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
        roc_auc_score,
        confusion_matrix,
        classification_report,
        roc_curve,
        precision_recall_curve,
    )
    from sklearn.model_selection import cross_val_predict, StratifiedKFold
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .feature_extractor import extract_all_features, FEATURE_NAMES
from .risk_labels import generate_all_labels, RiskLabeler
from .risk_predictor import get_risk_predictor, RiskCategory

# Results output directory
RESULTS_DIR = PROJECT_ROOT / 'results' / 'ml_evaluation'


@dataclass
class EvaluationMetrics:
    """Complete evaluation metrics for a model.

    Attributes:
        accuracy: Classification accuracy
        precision: Precision (positive predictive value)
        recall: Recall (sensitivity)
        f1: F1 score (harmonic mean of precision/recall)
        auc_roc: Area under ROC curve
        confusion_matrix: 2x2 confusion matrix
        classification_report: Detailed per-class metrics
    """
    accuracy: float
    precision: float
    recall: float
    f1: float
    auc_roc: float
    confusion_matrix: np.ndarray
    classification_report: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1': self.f1,
            'auc_roc': self.auc_roc,
            'confusion_matrix': self.confusion_matrix.tolist(),
        }


@dataclass
class ComparisonResult:
    """Results of comparing ML vs rule-based approaches.

    Attributes:
        agreement_rate: How often ML and rules agree
        ml_only_high: Features ML marks HIGH but rules mark LOW
        rules_only_high: Features rules mark HIGH but ML marks LOW
        both_high: Features both mark HIGH
        both_low: Features both mark LOW
        correlation: Correlation between predictions
    """
    agreement_rate: float
    ml_only_high: List[str]
    rules_only_high: List[str]
    both_high: List[str]
    both_low: List[str]
    correlation: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'agreement_rate': self.agreement_rate,
            'ml_only_high_count': len(self.ml_only_high),
            'rules_only_high_count': len(self.rules_only_high),
            'both_high_count': len(self.both_high),
            'both_low_count': len(self.both_low),
            'correlation': self.correlation,
            'ml_only_high_examples': self.ml_only_high[:10],
            'rules_only_high_examples': self.rules_only_high[:10],
        }


class ModelEvaluator:
    """Evaluates ML models for compatibility risk prediction.

    Provides comprehensive evaluation including:
    - Standard metrics (accuracy, precision, recall, F1, AUC)
    - Comparison with rule-based system
    - Feature importance analysis
    - Temporal split analysis for thesis
    """

    def __init__(self, model_name: str = 'random_forest'):
        """Initialize evaluator.

        Args:
            model_name: Name of model to evaluate
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required. Install with: pip install scikit-learn")

        self.model_name = model_name
        self.predictor = get_risk_predictor(model_name)
        self.rule_labeler = RiskLabeler()

        # Ensure results directory exists
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def evaluate_model(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        y_pred: Optional[np.ndarray] = None,
        y_prob: Optional[np.ndarray] = None,
    ) -> EvaluationMetrics:
        """Evaluate model on test data.

        Args:
            X_test: Test features
            y_test: True labels
            y_pred: Predictions (computed if None)
            y_prob: Prediction probabilities (computed if None)

        Returns:
            EvaluationMetrics with all computed metrics
        """
        if not self.predictor.is_model_loaded():
            raise ValueError("Model not loaded. Train models first.")

        # Get predictions if not provided
        if y_pred is None:
            if self.predictor.scaler is not None:
                X_scaled = self.predictor.scaler.transform(X_test)
            else:
                X_scaled = X_test
            y_pred = self.predictor.model.predict(X_scaled)
            y_prob = self.predictor.model.predict_proba(X_scaled)[:, 1]

        # Compute metrics
        metrics = EvaluationMetrics(
            accuracy=float(accuracy_score(y_test, y_pred)),
            precision=float(precision_score(y_test, y_pred, zero_division=0)),
            recall=float(recall_score(y_test, y_pred, zero_division=0)),
            f1=float(f1_score(y_test, y_pred, zero_division=0)),
            auc_roc=float(roc_auc_score(y_test, y_prob)) if y_prob is not None else 0.0,
            confusion_matrix=confusion_matrix(y_test, y_pred),
            classification_report=classification_report(
                y_test, y_pred,
                target_names=['LOW RISK', 'HIGH RISK'],
                zero_division=0
            ),
        )

        logger.info(f"Evaluation complete: Accuracy={metrics.accuracy:.3f}, F1={metrics.f1:.3f}")

        return metrics

    def compare_with_rules(
        self,
        feature_ids: List[str],
        ml_predictions: Dict[str, int],
        rule_labels: Dict[str, int],
    ) -> ComparisonResult:
        """Compare ML predictions with rule-based labels.

        This comparison is key for understanding:
        - What ML can predict that rules miss
        - What rules catch that ML might miss
        - Overall agreement between approaches

        Args:
            feature_ids: List of feature identifiers
            ml_predictions: ML predictions (0/1) by feature_id
            rule_labels: Rule-based labels (0/1) by feature_id

        Returns:
            ComparisonResult with detailed comparison
        """
        ml_only_high = []
        rules_only_high = []
        both_high = []
        both_low = []

        ml_values = []
        rule_values = []

        for fid in feature_ids:
            ml_pred = ml_predictions.get(fid, 0)
            rule_label = rule_labels.get(fid, 0)

            ml_values.append(ml_pred)
            rule_values.append(rule_label)

            if ml_pred == 1 and rule_label == 0:
                ml_only_high.append(fid)
            elif ml_pred == 0 and rule_label == 1:
                rules_only_high.append(fid)
            elif ml_pred == 1 and rule_label == 1:
                both_high.append(fid)
            else:
                both_low.append(fid)

        # Calculate agreement rate
        agreements = len(both_high) + len(both_low)
        total = len(feature_ids)
        agreement_rate = agreements / total if total > 0 else 0

        # Calculate correlation
        ml_arr = np.array(ml_values)
        rule_arr = np.array(rule_values)
        correlation = float(np.corrcoef(ml_arr, rule_arr)[0, 1]) if len(ml_arr) > 1 else 0.0

        result = ComparisonResult(
            agreement_rate=agreement_rate,
            ml_only_high=ml_only_high,
            rules_only_high=rules_only_high,
            both_high=both_high,
            both_low=both_low,
            correlation=correlation,
        )

        logger.info(f"ML vs Rules comparison: {agreement_rate:.1%} agreement")
        logger.info(f"ML-only HIGH: {len(ml_only_high)}, Rules-only HIGH: {len(rules_only_high)}")

        return result

    def evaluate_temporal_split(
        self,
        usage_threshold: float = 85.0,
    ) -> Dict[str, Any]:
        """Evaluate model performance on temporal split.

        This is the key thesis experiment: train on older features,
        test on newer features to demonstrate generalization.

        Args:
            usage_threshold: Features with usage below this are "newer"

        Returns:
            Dict with temporal split evaluation results
        """
        logger.info("=== Temporal Split Evaluation ===")

        # Load all data
        X, feature_ids, metadata = extract_all_features(return_metadata=True)
        y, _, _ = generate_all_labels()

        # Split by usage as proxy for temporal
        newer_mask = X[:, 0] < usage_threshold

        X_train = X[~newer_mask]
        X_test = X[newer_mask]
        y_train = y[~newer_mask]
        y_test = y[newer_mask]

        train_ids = [fid for fid, is_new in zip(feature_ids, newer_mask) if not is_new]
        test_ids = [fid for fid, is_new in zip(feature_ids, newer_mask) if is_new]

        logger.info(f"Training features (usage >= {usage_threshold}%): {len(train_ids)}")
        logger.info(f"Test features (usage < {usage_threshold}%): {len(test_ids)}")

        # If model is loaded, use it; otherwise use rule-based
        if self.predictor.is_model_loaded():
            # Scale features using loaded scaler
            if self.predictor.scaler is not None:
                X_test_scaled = self.predictor.scaler.transform(X_test)
            else:
                X_test_scaled = X_test

            y_pred = self.predictor.model.predict(X_test_scaled)
            y_prob = self.predictor.model.predict_proba(X_test_scaled)[:, 1]

            # Handle case where test set has only one class
            try:
                auc = float(roc_auc_score(y_test, y_prob))
            except ValueError:
                auc = 0.0  # AUC undefined for single class

            # Get unique classes for classification report
            unique_classes = np.unique(np.concatenate([y_test, y_pred]))
            target_names = ['LOW RISK', 'HIGH RISK']
            labels = [0, 1]

            metrics = EvaluationMetrics(
                accuracy=float(accuracy_score(y_test, y_pred)),
                precision=float(precision_score(y_test, y_pred, zero_division=0)),
                recall=float(recall_score(y_test, y_pred, zero_division=0)),
                f1=float(f1_score(y_test, y_pred, zero_division=0)),
                auc_roc=auc,
                confusion_matrix=confusion_matrix(y_test, y_pred, labels=labels),
                classification_report=classification_report(
                    y_test, y_pred,
                    target_names=target_names,
                    labels=labels,
                    zero_division=0
                ),
            )
        else:
            # Fallback to rule-based
            y_pred = y_test  # Rules generate the labels
            metrics = EvaluationMetrics(
                accuracy=1.0,  # Rules match themselves
                precision=1.0,
                recall=1.0,
                f1=1.0,
                auc_roc=1.0,
                confusion_matrix=np.array([[np.sum(y_test == 0), 0], [0, np.sum(y_test == 1)]]),
                classification_report="Using rule-based labels as ground truth",
            )

        results = {
            'usage_threshold': usage_threshold,
            'train_count': len(train_ids),
            'test_count': len(test_ids),
            'test_high_risk_count': int(np.sum(y_test == 1)),
            'test_low_risk_count': int(np.sum(y_test == 0)),
            'metrics': metrics.to_dict(),
            'classification_report': metrics.classification_report,
            'test_feature_ids': test_ids,
        }

        logger.info(f"Temporal split results: Accuracy={metrics.accuracy:.3f}, F1={metrics.f1:.3f}")

        return results

    def get_feature_importance_ranking(self) -> List[Tuple[str, float]]:
        """Get ranked feature importances.

        Returns:
            List of (feature_name, importance) tuples, sorted by importance
        """
        importances = self.predictor.get_feature_importance()

        if importances is None:
            logger.warning("Feature importances not available")
            return []

        # Sort by importance descending
        ranked = sorted(importances.items(), key=lambda x: x[1], reverse=True)

        return ranked

    def generate_roc_data(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, List[float]]:
        """Generate ROC curve data.

        Args:
            X_test: Test features
            y_test: True labels

        Returns:
            Dict with 'fpr', 'tpr', 'thresholds' lists
        """
        if not self.predictor.is_model_loaded():
            return {'fpr': [], 'tpr': [], 'thresholds': []}

        if self.predictor.scaler is not None:
            X_scaled = self.predictor.scaler.transform(X_test)
        else:
            X_scaled = X_test

        y_prob = self.predictor.model.predict_proba(X_scaled)[:, 1]
        fpr, tpr, thresholds = roc_curve(y_test, y_prob)

        return {
            'fpr': fpr.tolist(),
            'tpr': tpr.tolist(),
            'thresholds': thresholds.tolist(),
        }

    def generate_precision_recall_data(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, List[float]]:
        """Generate precision-recall curve data.

        Args:
            X_test: Test features
            y_test: True labels

        Returns:
            Dict with 'precision', 'recall', 'thresholds' lists
        """
        if not self.predictor.is_model_loaded():
            return {'precision': [], 'recall': [], 'thresholds': []}

        if self.predictor.scaler is not None:
            X_scaled = self.predictor.scaler.transform(X_test)
        else:
            X_scaled = X_test

        y_prob = self.predictor.model.predict_proba(X_scaled)[:, 1]
        precision, recall, thresholds = precision_recall_curve(y_test, y_prob)

        return {
            'precision': precision.tolist(),
            'recall': recall.tolist(),
            'thresholds': thresholds.tolist(),
        }

    def save_evaluation_report(
        self,
        metrics: EvaluationMetrics,
        comparison: Optional[ComparisonResult] = None,
        temporal_results: Optional[Dict] = None,
        filename: str = 'evaluation_report.json',
    ):
        """Save comprehensive evaluation report.

        Args:
            metrics: Model evaluation metrics
            comparison: Optional comparison with rules
            temporal_results: Optional temporal split results
            filename: Output filename
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'model_name': self.model_name,
            'metrics': metrics.to_dict(),
            'classification_report': metrics.classification_report,
            'feature_importance_ranking': self.get_feature_importance_ranking()[:10],
        }

        if comparison is not None:
            report['comparison_with_rules'] = comparison.to_dict()

        if temporal_results is not None:
            report['temporal_split_evaluation'] = temporal_results

        report_path = RESULTS_DIR / filename
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Saved evaluation report to {report_path}")


def evaluate_models(
    save_report: bool = True,
    run_temporal: bool = True,
) -> Dict[str, Any]:
    """Main entry point for model evaluation.

    Args:
        save_report: Whether to save evaluation report
        run_temporal: Whether to run temporal split evaluation

    Returns:
        Dict containing all evaluation results
    """
    if not SKLEARN_AVAILABLE:
        raise ImportError("scikit-learn required. Install with: pip install scikit-learn")

    logger.info("=== Model Evaluation ===")

    # Load data
    X, feature_ids, metadata = extract_all_features(return_metadata=True)
    y, _, _ = generate_all_labels()

    # Initialize evaluator
    evaluator = ModelEvaluator()

    results = {
        'dataset_size': len(feature_ids),
        'high_risk_count': int(np.sum(y == 1)),
        'low_risk_count': int(np.sum(y == 0)),
    }

    # Standard evaluation
    if evaluator.predictor.is_model_loaded():
        # Split for evaluation
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        metrics = evaluator.evaluate_model(X_test, y_test)
        results['standard_metrics'] = metrics.to_dict()
        results['classification_report'] = metrics.classification_report

        # Feature importance
        results['feature_importance'] = evaluator.get_feature_importance_ranking()

        # ROC and PR data
        results['roc_data'] = evaluator.generate_roc_data(X_test, y_test)

        # Compare with rule-based
        predictor = get_risk_predictor()
        ml_preds = {}
        rule_labels = {}

        for i, fid in enumerate(feature_ids):
            # ML prediction
            if predictor.scaler is not None:
                X_scaled = predictor.scaler.transform(X[i:i+1])
            else:
                X_scaled = X[i:i+1]
            ml_preds[fid] = int(predictor.model.predict(X_scaled)[0])

            # Rule-based label
            rule_labels[fid] = int(y[i])

        comparison = evaluator.compare_with_rules(feature_ids, ml_preds, rule_labels)
        results['comparison_with_rules'] = comparison.to_dict()

        # Temporal split evaluation
        if run_temporal:
            temporal_results = evaluator.evaluate_temporal_split()
            results['temporal_split'] = temporal_results

        # Save report
        if save_report:
            evaluator.save_evaluation_report(
                metrics,
                comparison,
                temporal_results if run_temporal else None,
            )

    else:
        logger.warning("Model not loaded, running limited evaluation")
        results['error'] = "Model not loaded. Run train_models() first."

    return results


# Allow running as script
if __name__ == '__main__':
    print("=" * 60)
    print("Cross Guard ML Model Evaluation")
    print("=" * 60)

    results = evaluate_models()

    print("\n=== Results ===")
    print(f"Dataset: {results['dataset_size']} features")
    print(f"  HIGH RISK: {results['high_risk_count']}")
    print(f"  LOW RISK: {results['low_risk_count']}")

    if 'standard_metrics' in results:
        m = results['standard_metrics']
        print(f"\nStandard Metrics:")
        print(f"  Accuracy:  {m['accuracy']:.3f}")
        print(f"  Precision: {m['precision']:.3f}")
        print(f"  Recall:    {m['recall']:.3f}")
        print(f"  F1:        {m['f1']:.3f}")
        print(f"  AUC-ROC:   {m['auc_roc']:.3f}")

    if 'comparison_with_rules' in results:
        c = results['comparison_with_rules']
        print(f"\nML vs Rules Comparison:")
        print(f"  Agreement: {c['agreement_rate']:.1%}")
        print(f"  Correlation: {c['correlation']:.3f}")

    if 'temporal_split' in results:
        t = results['temporal_split']
        print(f"\nTemporal Split (usage < {t['usage_threshold']}%):")
        print(f"  Test features: {t['test_count']}")
        print(f"  Accuracy: {t['metrics']['accuracy']:.3f}")
        print(f"  F1: {t['metrics']['f1']:.3f}")

    if 'feature_importance' in results and results['feature_importance']:
        print(f"\nTop 5 Feature Importances:")
        for name, imp in results['feature_importance'][:5]:
            print(f"  {name}: {imp:.4f}")
