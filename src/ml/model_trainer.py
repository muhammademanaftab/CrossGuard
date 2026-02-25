"""Training pipelines for Random Forest, Logistic Regression, and Gradient Boosting."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np

from ..utils.config import get_logger, PROJECT_ROOT

logger = get_logger('ml.model_trainer')

try:
    from sklearn.model_selection import (
        train_test_split,
        cross_val_score,
        StratifiedKFold,
    )
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import (
        RandomForestClassifier,
        GradientBoostingClassifier,
    )
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
        roc_auc_score,
    )
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not installed. Run: pip install scikit-learn")

from .feature_extractor import extract_all_features, FEATURE_NAMES
from .risk_labels import generate_all_labels

PRETRAINED_DIR = Path(__file__).parent / 'pretrained'


@dataclass
class TrainingResult:
    """Metrics and metadata from training a single model."""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    auc_roc: float
    cv_scores: List[float]
    feature_importances: Optional[Dict[str, float]] = None
    training_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_name': self.model_name,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1': self.f1,
            'auc_roc': self.auc_roc,
            'cv_scores': self.cv_scores,
            'feature_importances': self.feature_importances,
            'training_time': self.training_time,
        }


class ModelTrainer:
    """Handles the full training pipeline: data prep, training, CV, and persistence."""

    def __init__(
        self,
        test_size: float = 0.2,
        random_state: int = 42,
        n_cv_folds: int = 5,
    ):
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required. Install with: pip install scikit-learn")

        self.test_size = test_size
        self.random_state = random_state
        self.n_cv_folds = n_cv_folds

        self.scaler = StandardScaler()
        self.models = {}
        self.results = {}

        PRETRAINED_DIR.mkdir(parents=True, exist_ok=True)

    def prepare_data(
        self,
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
        feature_ids: Optional[List[str]] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Split and scale data. Extracts features/labels automatically if not provided."""
        if X is None or y is None:
            logger.info("Extracting features and generating labels...")
            X, feature_ids, _ = extract_all_features()
            y, _, _ = generate_all_labels()

        logger.info(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features")
        logger.info(f"Class distribution: {np.sum(y == 1)} HIGH RISK, {np.sum(y == 0)} LOW RISK")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y,
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        logger.info(f"Training set: {X_train_scaled.shape[0]} samples")
        logger.info(f"Test set: {X_test_scaled.shape[0]} samples")

        return X_train_scaled, X_test_scaled, y_train, y_test

    def prepare_temporal_split(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_ids: List[str],
        temporal_features: Optional[List[str]] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str], List[str]]:
        """Train on older features, test on newer ones. Key thesis experiment."""
        if temporal_features is None:
            # Low-usage features are likely newer -- not perfect but a reasonable proxy
            usage_threshold = 85.0
            newer_mask = X[:, 0] < usage_threshold  # usage_perc_y is index 0
            logger.info(f"Using usage threshold {usage_threshold}% as proxy for newer features")
        else:
            newer_mask = np.array([fid in temporal_features for fid in feature_ids])

        X_train = X[~newer_mask]
        X_test = X[newer_mask]
        y_train = y[~newer_mask]
        y_test = y[newer_mask]

        train_ids = [fid for fid, is_new in zip(feature_ids, newer_mask) if not is_new]
        test_ids = [fid for fid, is_new in zip(feature_ids, newer_mask) if is_new]

        logger.info(f"Temporal split: {len(train_ids)} training, {len(test_ids)} test features")

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test, train_ids, test_ids

    def train_random_forest(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> TrainingResult:
        """Train Random Forest -- primary model since it gives feature importances."""
        import time
        start_time = time.time()

        logger.info("Training Random Forest...")

        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=self.random_state,
            n_jobs=-1,
        )

        cv = StratifiedKFold(n_splits=self.n_cv_folds, shuffle=True, random_state=self.random_state)
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        feature_importance_dict = {
            name: float(imp) for name, imp in zip(FEATURE_NAMES, model.feature_importances_)
        }

        self.models['random_forest'] = model
        self._save_model(model, 'random_forest')

        training_time = time.time() - start_time

        result = TrainingResult(
            model_name='random_forest',
            accuracy=float(accuracy_score(y_test, y_pred)),
            precision=float(precision_score(y_test, y_pred, zero_division=0)),
            recall=float(recall_score(y_test, y_pred, zero_division=0)),
            f1=float(f1_score(y_test, y_pred, zero_division=0)),
            auc_roc=float(roc_auc_score(y_test, y_prob)),
            cv_scores=[float(s) for s in cv_scores],
            feature_importances=feature_importance_dict,
            training_time=training_time,
        )

        self.results['random_forest'] = result
        logger.info(f"Random Forest: Accuracy={result.accuracy:.3f}, F1={result.f1:.3f}, AUC={result.auc_roc:.3f}")

        return result

    def train_logistic_regression(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> TrainingResult:
        """Train Logistic Regression as a baseline for comparison."""
        import time
        start_time = time.time()

        logger.info("Training Logistic Regression...")

        model = LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            random_state=self.random_state,
        )

        cv = StratifiedKFold(n_splits=self.n_cv_folds, shuffle=True, random_state=self.random_state)
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        # Use absolute coefficient values as feature importance proxy
        coef_importance = {
            name: float(abs(coef)) for name, coef in zip(FEATURE_NAMES, model.coef_[0])
        }

        self.models['logistic_regression'] = model
        self._save_model(model, 'logistic_regression')

        training_time = time.time() - start_time

        result = TrainingResult(
            model_name='logistic_regression',
            accuracy=float(accuracy_score(y_test, y_pred)),
            precision=float(precision_score(y_test, y_pred, zero_division=0)),
            recall=float(recall_score(y_test, y_pred, zero_division=0)),
            f1=float(f1_score(y_test, y_pred, zero_division=0)),
            auc_roc=float(roc_auc_score(y_test, y_prob)),
            cv_scores=[float(s) for s in cv_scores],
            feature_importances=coef_importance,
            training_time=training_time,
        )

        self.results['logistic_regression'] = result
        logger.info(f"Logistic Regression: Accuracy={result.accuracy:.3f}, F1={result.f1:.3f}, AUC={result.auc_roc:.3f}")

        return result

    def train_gradient_boosting(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> TrainingResult:
        """Train Gradient Boosting -- usually best accuracy but slowest."""
        import time
        start_time = time.time()

        logger.info("Training Gradient Boosting...")

        model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=self.random_state,
        )

        cv = StratifiedKFold(n_splits=self.n_cv_folds, shuffle=True, random_state=self.random_state)
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        feature_importance_dict = {
            name: float(imp) for name, imp in zip(FEATURE_NAMES, model.feature_importances_)
        }

        self.models['gradient_boosting'] = model
        self._save_model(model, 'gradient_boosting')

        training_time = time.time() - start_time

        result = TrainingResult(
            model_name='gradient_boosting',
            accuracy=float(accuracy_score(y_test, y_pred)),
            precision=float(precision_score(y_test, y_pred, zero_division=0)),
            recall=float(recall_score(y_test, y_pred, zero_division=0)),
            f1=float(f1_score(y_test, y_pred, zero_division=0)),
            auc_roc=float(roc_auc_score(y_test, y_prob)),
            cv_scores=[float(s) for s in cv_scores],
            feature_importances=feature_importance_dict,
            training_time=training_time,
        )

        self.results['gradient_boosting'] = result
        logger.info(f"Gradient Boosting: Accuracy={result.accuracy:.3f}, F1={result.f1:.3f}, AUC={result.auc_roc:.3f}")

        return result

    def train_all_models(
        self,
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
    ) -> Dict[str, TrainingResult]:
        """Train all three models and save everything."""
        X_train, X_test, y_train, y_test = self.prepare_data(X, y)

        self.train_random_forest(X_train, y_train, X_test, y_test)
        self.train_logistic_regression(X_train, y_train, X_test, y_test)
        self.train_gradient_boosting(X_train, y_train, X_test, y_test)

        self._save_scaler()
        self._save_results_summary()

        return self.results

    def _save_model(self, model: Any, name: str):
        model_path = PRETRAINED_DIR / f'{name}.joblib'
        joblib.dump(model, model_path)
        logger.info(f"Saved model to {model_path}")

    def _save_scaler(self):
        scaler_path = PRETRAINED_DIR / 'feature_scaler.joblib'
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"Saved scaler to {scaler_path}")

    def _save_results_summary(self):
        summary_path = PRETRAINED_DIR / 'training_results.json'

        summary = {
            'timestamp': datetime.now().isoformat(),
            'models': {name: result.to_dict() for name, result in self.results.items()},
            'best_model': max(self.results.keys(), key=lambda k: self.results[k].f1),
        }

        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Saved results summary to {summary_path}")

    def get_best_model(self) -> Tuple[str, Any]:
        """Return the model with the highest F1 score."""
        if not self.results:
            raise ValueError("No models have been trained yet")

        best_name = max(self.results.keys(), key=lambda k: self.results[k].f1)
        return best_name, self.models[best_name]


def train_models(
    save_dir: Optional[Path] = None,
    temporal_split: bool = False,
) -> Dict[str, TrainingResult]:
    """Main entry point: train all models with either random or temporal split."""
    if not SKLEARN_AVAILABLE:
        raise ImportError("scikit-learn is required. Install with: pip install scikit-learn")

    trainer = ModelTrainer()

    if temporal_split:
        X, feature_ids, _ = extract_all_features()
        y, _, _ = generate_all_labels()

        X_train, X_test, y_train, y_test, train_ids, test_ids = \
            trainer.prepare_temporal_split(X, y, feature_ids)

        logger.info(f"Training on {len(train_ids)} older features, testing on {len(test_ids)} newer")

        trainer.train_random_forest(X_train, y_train, X_test, y_test)
        trainer.train_logistic_regression(X_train, y_train, X_test, y_test)
        trainer.train_gradient_boosting(X_train, y_train, X_test, y_test)

        trainer._save_scaler()
        trainer._save_results_summary()

        return trainer.results

    else:
        return trainer.train_all_models()


if __name__ == '__main__':
    import sys

    temporal = '--temporal' in sys.argv

    print("=" * 60)
    print("Cross Guard ML Model Training")
    print("=" * 60)

    results = train_models(temporal_split=temporal)

    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)

    for name, result in results.items():
        print(f"\n{name.upper()}")
        print(f"  Accuracy:  {result.accuracy:.3f}")
        print(f"  Precision: {result.precision:.3f}")
        print(f"  Recall:    {result.recall:.3f}")
        print(f"  F1 Score:  {result.f1:.3f}")
        print(f"  AUC-ROC:   {result.auc_roc:.3f}")
        print(f"  CV Mean:   {np.mean(result.cv_scores):.3f} (+/- {np.std(result.cv_scores):.3f})")
