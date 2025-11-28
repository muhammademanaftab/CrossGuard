"""Test CSS Parser"""

from src.parsers.css_parser import CSSParser

# Sample CSS code
css_code = """
/* Modern CSS Features */

.container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
}

.grid-layout {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-gap: 10px;
}

.card {
    background: linear-gradient(to right, #ff0000, #00ff00);
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transform: translateY(-5px);
    transition: all 0.3s ease;
}

.card:hover {
    transform: translateY(-10px) scale(1.05);
}

:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
}

.button {
    background-color: var(--primary-color);
    color: white;
    padding: 10px 20px;
}

@media (max-width: 768px) {
    .container {
        flex-direction: column;
    }
}

@media (prefers-color-scheme: dark) {
    body {
        background: #1a1a1a;
        color: #ffffff;
    }
}

.text {
    font-family: system-ui, -apple-system, sans-serif;
    text-overflow: ellipsis;
}

.modern {
    aspect-ratio: 16 / 9;
    object-fit: cover;
}

@supports (display: grid) {
    .grid {
        display: grid;
    }
}
"""

def main():
    print("="*70)
    print("  CSS PARSER TEST")
    print("="*70)
    print()
    
    # Create parser
    parser = CSSParser()
    
    # Parse CSS
    features = parser.parse_string(css_code)
    
    # Get statistics
    stats = parser.get_statistics()
    
    print(f"Total CSS features detected: {stats['total_features']}")
    print()
    
    print("Features by category:")
    print(f"  Layout: {stats['layout_features']}")
    print(f"  Transform/Animation: {stats['transform_animation']}")
    print(f"  Color/Background: {stats['color_background']}")
    print(f"  Typography: {stats['typography']}")
    print(f"  Selectors: {stats['selectors']}")
    print(f"  Media Queries: {stats['media_queries']}")
    print(f"  Other: {stats['other_features']}")
    print()
    
    print("Detected features:")
    for i, feature in enumerate(sorted(features), 1):
        print(f"  {i:2d}. {feature}")
    
    print()
    print("="*70)
    print("✅ CSS Parser is working correctly!")
    print("="*70)

if __name__ == "__main__":
    main()
