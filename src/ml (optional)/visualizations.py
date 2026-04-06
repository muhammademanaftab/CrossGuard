"""Publication-quality charts for the thesis (feature importance, ROC, confusion matrix, etc.)."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from ..utils.config import get_logger, PROJECT_ROOT

logger = get_logger('ml.visualizations')

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not installed. Visualizations unavailable.")

FIGURES_DIR = PROJECT_ROOT / 'results' / 'figures'

# Tuned for academic paper readability
PAPER_STYLE = {
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.figsize': (6, 4),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3,
}

COLORS = {
    'primary': '#2563eb',
    'secondary': '#7c3aed',
    'success': '#16a34a',
    'warning': '#ea580c',
    'danger': '#dc2626',
    'muted': '#6b7280',
    'high_risk': '#ef4444',
    'low_risk': '#22c55e',
}


def setup_style():
    """Apply academic paper matplotlib style."""
    if not MATPLOTLIB_AVAILABLE:
        return
    plt.rcParams.update(PAPER_STYLE)


def plot_feature_importance(
    importances: List[Tuple[str, float]],
    top_n: int = 15,
    title: str = 'Feature Importance for Risk Prediction',
    save_path: Optional[Path] = None,
    show: bool = False,
) -> Optional[Figure]:
    """Horizontal bar chart of top feature importances."""
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("matplotlib not available")
        return None

    setup_style()

    top_features = importances[:top_n]
    names = [name.replace('_', ' ').title() for name, _ in top_features]
    values = [imp for _, imp in top_features]

    fig, ax = plt.subplots(figsize=(8, 6))

    y_pos = np.arange(len(names))
    bars = ax.barh(y_pos, values, color=COLORS['primary'], alpha=0.8)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlabel('Importance Score')
    ax.set_title(title, fontweight='bold', pad=15)

    for bar, value in zip(bars, values):
        ax.text(value + 0.002, bar.get_y() + bar.get_height()/2,
                f'{value:.3f}', va='center', fontsize=8)

    plt.tight_layout()

    if save_path is None:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        save_path = FIGURES_DIR / 'feature_importance.png'

    fig.savefig(save_path)
    logger.info(f"Saved feature importance chart to {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig


def plot_roc_curve(
    fpr: List[float],
    tpr: List[float],
    auc_score: float,
    title: str = 'ROC Curve for Risk Prediction',
    save_path: Optional[Path] = None,
    show: bool = False,
) -> Optional[Figure]:
    """ROC curve with AUC shading and random-classifier baseline."""
    if not MATPLOTLIB_AVAILABLE:
        return None

    setup_style()

    fig, ax = plt.subplots(figsize=(6, 6))

    ax.plot(fpr, tpr, color=COLORS['primary'], lw=2,
            label=f'ROC curve (AUC = {auc_score:.3f})')

    ax.plot([0, 1], [0, 1], color=COLORS['muted'], lw=1.5, linestyle='--',
            label='Random classifier')

    ax.fill_between(fpr, tpr, alpha=0.2, color=COLORS['primary'])

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title(title, fontweight='bold', pad=15)
    ax.legend(loc='lower right')
    ax.set_aspect('equal')

    plt.tight_layout()

    if save_path is None:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        save_path = FIGURES_DIR / 'roc_curve.png'

    fig.savefig(save_path)
    logger.info(f"Saved ROC curve to {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig


def plot_confusion_matrix(
    cm: np.ndarray,
    title: str = 'Confusion Matrix',
    labels: List[str] = ['LOW RISK', 'HIGH RISK'],
    save_path: Optional[Path] = None,
    show: bool = False,
) -> Optional[Figure]:
    """Annotated confusion matrix heatmap."""
    if not MATPLOTLIB_AVAILABLE:
        return None

    setup_style()

    fig, ax = plt.subplots(figsize=(6, 5))

    im = ax.imshow(cm, interpolation='nearest', cmap='Blues')

    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Count', rotation=-90, va='bottom')

    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

    thresh = cm.max() / 2.
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, format(cm[i, j], 'd'),
                    ha='center', va='center',
                    color='white' if cm[i, j] > thresh else 'black',
                    fontsize=14, fontweight='bold')

    ax.set_xlabel('Predicted Label')
    ax.set_ylabel('True Label')
    ax.set_title(title, fontweight='bold', pad=15)

    plt.tight_layout()

    if save_path is None:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        save_path = FIGURES_DIR / 'confusion_matrix.png'

    fig.savefig(save_path)
    logger.info(f"Saved confusion matrix to {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig


def plot_ml_vs_rules_comparison(
    comparison_data: Dict[str, Any],
    title: str = 'ML vs Rule-Based Risk Classification',
    save_path: Optional[Path] = None,
    show: bool = False,
) -> Optional[Figure]:
    """Side-by-side pie chart and bar chart showing ML/rules agreement."""
    if not MATPLOTLIB_AVAILABLE:
        return None

    setup_style()

    both_high = comparison_data.get('both_high_count', 0)
    both_low = comparison_data.get('both_low_count', 0)
    ml_only = comparison_data.get('ml_only_high_count', 0)
    rules_only = comparison_data.get('rules_only_high_count', 0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    sizes = [both_high, both_low, ml_only, rules_only]
    labels = ['Both HIGH', 'Both LOW', 'ML-only HIGH', 'Rules-only HIGH']
    colors = [COLORS['danger'], COLORS['success'], COLORS['warning'], COLORS['secondary']]
    explode = (0, 0, 0.05, 0.05)  # pop out the disagreements

    ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=False, startangle=90)
    ax1.set_title('Classification Agreement', fontweight='bold')

    categories = ['Agree HIGH', 'Agree LOW', 'ML only', 'Rules only']
    values = [both_high, both_low, ml_only, rules_only]

    x = np.arange(len(categories))
    bars = ax2.bar(x, values, color=[COLORS['danger'], COLORS['success'],
                                      COLORS['warning'], COLORS['secondary']])

    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, rotation=15, ha='right')
    ax2.set_ylabel('Number of Features')
    ax2.set_title('Classification Breakdown', fontweight='bold')

    for bar, val in zip(bars, values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                 str(val), ha='center', va='bottom', fontsize=9)

    agreement = comparison_data.get('agreement_rate', 0)
    fig.text(0.5, 0.02, f'Overall Agreement: {agreement:.1%}',
             ha='center', fontsize=10, fontweight='bold')

    plt.suptitle(title, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path is None:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        save_path = FIGURES_DIR / 'ml_vs_rules.png'

    fig.savefig(save_path)
    logger.info(f"Saved ML vs Rules comparison to {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig


def plot_temporal_split_results(
    standard_metrics: Dict[str, float],
    temporal_metrics: Dict[str, float],
    title: str = 'Model Performance: Standard vs Temporal Split',
    save_path: Optional[Path] = None,
    show: bool = False,
) -> Optional[Figure]:
    """Grouped bar chart comparing standard vs temporal split -- shows generalization."""
    if not MATPLOTLIB_AVAILABLE:
        return None

    setup_style()

    fig, ax = plt.subplots(figsize=(8, 5))

    metrics = ['Accuracy', 'Precision', 'Recall', 'F1', 'AUC']
    metric_keys = ['accuracy', 'precision', 'recall', 'f1', 'auc_roc']

    standard_vals = [standard_metrics.get(k, 0) for k in metric_keys]
    temporal_vals = [temporal_metrics.get(k, 0) for k in metric_keys]

    x = np.arange(len(metrics))
    width = 0.35

    bars1 = ax.bar(x - width/2, standard_vals, width, label='Standard Split',
                   color=COLORS['primary'], alpha=0.8)
    bars2 = ax.bar(x + width/2, temporal_vals, width, label='Temporal Split',
                   color=COLORS['secondary'], alpha=0.8)

    ax.set_ylabel('Score')
    ax.set_title(title, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.set_ylim(0, 1.1)

    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.02,
                f'{height:.2f}', ha='center', va='bottom', fontsize=8)

    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.02,
                f'{height:.2f}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()

    if save_path is None:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        save_path = FIGURES_DIR / 'temporal_split_comparison.png'

    fig.savefig(save_path)
    logger.info(f"Saved temporal split comparison to {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig


def plot_model_comparison(
    results: Dict[str, Dict[str, float]],
    title: str = 'Model Performance Comparison',
    save_path: Optional[Path] = None,
    show: bool = False,
) -> Optional[Figure]:
    """Grouped bar chart comparing all three models across metrics."""
    if not MATPLOTLIB_AVAILABLE:
        return None

    setup_style()

    fig, ax = plt.subplots(figsize=(10, 5))

    models = list(results.keys())
    metrics = ['accuracy', 'precision', 'recall', 'f1', 'auc_roc']
    metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1', 'AUC']

    x = np.arange(len(metrics))
    width = 0.25

    colors_list = [COLORS['primary'], COLORS['secondary'], COLORS['success']]

    for i, (model_name, model_metrics) in enumerate(results.items()):
        values = [model_metrics.get(m, 0) for m in metrics]
        offset = (i - len(models)/2 + 0.5) * width
        bars = ax.bar(x + offset, values, width, label=model_name.replace('_', ' ').title(),
                     color=colors_list[i % len(colors_list)], alpha=0.8)

    ax.set_ylabel('Score')
    ax.set_title(title, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels)
    ax.legend()
    ax.set_ylim(0, 1.1)

    plt.tight_layout()

    if save_path is None:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        save_path = FIGURES_DIR / 'model_comparison.png'

    fig.savefig(save_path)
    logger.info(f"Saved model comparison to {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig


def generate_all_thesis_figures(
    evaluation_results: Dict[str, Any],
    show: bool = False,
):
    """Generate all thesis figures from evaluation results."""
    if not MATPLOTLIB_AVAILABLE:
        logger.error("matplotlib required for visualizations")
        return

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Generating thesis figures in {FIGURES_DIR}")

    if 'feature_importance' in evaluation_results:
        plot_feature_importance(
            evaluation_results['feature_importance'],
            top_n=15,
            show=show,
        )

    if 'roc_data' in evaluation_results and evaluation_results['roc_data']['fpr']:
        auc = evaluation_results.get('standard_metrics', {}).get('auc_roc', 0)
        plot_roc_curve(
            evaluation_results['roc_data']['fpr'],
            evaluation_results['roc_data']['tpr'],
            auc,
            show=show,
        )

    if 'standard_metrics' in evaluation_results:
        cm = evaluation_results['standard_metrics'].get('confusion_matrix')
        if cm is not None:
            plot_confusion_matrix(
                np.array(cm),
                show=show,
            )

    if 'comparison_with_rules' in evaluation_results:
        plot_ml_vs_rules_comparison(
            evaluation_results['comparison_with_rules'],
            show=show,
        )

    if 'temporal_split' in evaluation_results and 'standard_metrics' in evaluation_results:
        plot_temporal_split_results(
            evaluation_results['standard_metrics'],
            evaluation_results['temporal_split']['metrics'],
            show=show,
        )

    logger.info("All thesis figures generated successfully")


if __name__ == '__main__':
    import json

    results_path = PROJECT_ROOT / 'results' / 'ml_evaluation' / 'evaluation_report.json'

    if results_path.exists():
        with open(results_path) as f:
            results = json.load(f)
        generate_all_thesis_figures(results, show=True)
    else:
        print(f"No evaluation results found at {results_path}")
        print("Run model_evaluator.py first to generate results.")
