"""
Styles for Cross Guard GUI
Centralized stylesheet definitions.
"""

# Design Tokens
COLORS = {
    'primary': '#2196F3',
    'primary_dark': '#1976D2',
    'primary_light': '#BBDEFB',
    'success': '#4CAF50',
    'success_dark': '#45a049',
    'warning': '#FF9800',
    'warning_dark': '#e68900',
    'danger': '#F44336',
    'danger_dark': '#da190b',
    'text_primary': '#333333',
    'text_secondary': '#555555',
    'text_muted': '#666666',
    'background': '#F5F5F5',
    'surface': '#FFFFFF',
    'surface_alt': '#f9f9f9',
    'border': '#E0E0E0',
    'border_light': '#dddddd',
}

SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 16,
    'lg': 24,
    'xl': 32,
}

FONTS = {
    'size_small': 12,
    'size_normal': 13,
    'size_medium': 14,
    'size_large': 16,
    'size_title': 20,
    'size_header': 24,
}


def get_color(name: str) -> str:
    """Get a color value by name."""
    return COLORS.get(name, '#000000')


def get_spacing(name: str) -> int:
    """Get a spacing value by name."""
    return SPACING.get(name, 8)


def get_main_stylesheet() -> str:
    """Get the main application stylesheet.
    
    Returns:
        CSS stylesheet string
    """
    return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        #headerFrame {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 10px;
        }
        
        QGroupBox {
            font-weight: bold;
            font-size: 14px;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin-top: 12px;
            margin-bottom: 8px;
            padding-top: 20px;
            padding-bottom: 12px;
            padding-left: 12px;
            padding-right: 12px;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 8px;
            padding: 2px 5px;
            color: #333;
        }
        
        #browserCard {
            background-color: #f9f9f9;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 8px;
        }
        
        QListWidget {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 5px;
            background-color: #fafafa;
            font-size: 13px;
            color: #333;
        }
        
        QListWidget::item {
            padding: 5px;
            border-radius: 3px;
            color: #333;
        }
        
        QListWidget::item:selected {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        
        QPushButton {
            border: none;
            border-radius: 5px;
            padding: 10px 15px;
            font-family: Arial, sans-serif;
            font-weight: bold;
            font-size: 14px;
            color: #FFFFFF;
            text-align: center;
        }
        
        #addButton {
            background-color: #4CAF50;
            color: white;
            font-size: 12px;
            margin-bottom: 8px;
        }
        
        #addButton:hover {
            background-color: #45a049;
        }
        
        #removeButton {
            background-color: #FF9800;
            color: white;
            font-size: 12px;
            margin-top: 8px;
        }
        
        #removeButton:hover {
            background-color: #e68900;
        }
        
        #clearButton {
            background-color: #f44336;
            color: white;
        }
        
        #clearButton:hover {
            background-color: #da190b;
        }
        
        #clearAllButton {
            background-color: #9e9e9e;
            color: white;
            font-size: 13px;
        }
        
        #clearAllButton:hover {
            background-color: #757575;
        }
        
        #analyzeButton {
            background-color: #2196F3;
            color: white;
            font-size: 14px;
        }
        
        #analyzeButton:hover {
            background-color: #0b7dda;
        }
        
        #updateDbButton {
            background-color: #2196F3;
            color: white;
            font-size: 13px;
            font-weight: bold;
        }
        
        #updateDbButton:hover {
            background-color: #1976D2;
        }
        
        #backButton {
            background-color: #f8f9fa;
            color: #333;
            font-size: 14px;
            font-weight: bold;
            border: 1px solid #ddd;
        }
        
        #backButton:hover {
            background-color: #e9ecef;
        }
        
        #exportPdfButton {
            background-color: #f8f9fa;
            color: #333;
            font-size: 14px;
            font-weight: bold;
            border: 1px solid #ddd;
            border-radius: 6px;
        }
        
        #exportPdfButton:hover {
            background-color: #e9ecef;
        }
        
        #exportJsonButton {
            background-color: #f8f9fa;
            color: #333;
            font-size: 14px;
            font-weight: bold;
            border: 1px solid #ddd;
            border-radius: 6px;
        }
        
        #exportJsonButton:hover {
            background-color: #e9ecef;
        }
        
        #resultsScroll {
            border: none;
            background-color: transparent;
        }
        
        QPushButton:pressed {
            padding-top: 10px;
            padding-bottom: 6px;
        }

        /* Drop Zone Styles */
        #dropZone {
            border: 2px dashed #ccc;
            border-radius: 8px;
            background-color: #fafafa;
            min-height: 60px;
        }

        #dropZone:hover {
            border-color: #2196F3;
            background-color: #e3f2fd;
        }

        #dropZoneActive {
            border: 2px solid #2196F3;
            border-radius: 8px;
            background-color: #e3f2fd;
            min-height: 60px;
        }

        /* Score Card Styles */
        #scoreCard {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
        }

        /* Enhanced Browser Card */
        #enhancedBrowserCard {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 12px;
        }

        #enhancedBrowserCard:hover {
            border-color: #2196F3;
            background-color: #fafafa;
        }
    """
