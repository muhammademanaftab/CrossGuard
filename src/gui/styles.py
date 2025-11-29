"""
Styles for Cross Guard GUI
Centralized stylesheet definitions.
"""


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
            font-size: 13px;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 18px;
            padding-bottom: 5px;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 5px;
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
    """
