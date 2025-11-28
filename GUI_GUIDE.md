# Cross Guard GUI Guide

## Running the Application

### Quick Start
```bash
python run_gui.py
```

Or from the src directory:
```bash
python -m gui.app
```

## Current Features (Step 1 Complete ✅)

### File Upload Interface
The main window now includes:

- **HTML Files Section**: Upload and manage HTML files
- **CSS Files Section**: Upload and manage CSS files  
- **JavaScript Files Section**: Upload and manage JavaScript files

### File Management
Each section has:
- **➕ Add Files**: Browse and select multiple files
- **➖ Remove**: Remove selected file from list
- **🗑️ Clear All**: Clear all files in that section

### Actions
- **Clear All Files**: Remove all files from all sections
- **🔍 Analyze Compatibility**: Start analysis (placeholder for now)

## What You Can Do Now

1. **Launch the app**: Run `python run_gui.py`
2. **Add files**: Click "Add Files" buttons to select HTML/CSS/JS files
3. **Manage files**: Remove or clear files as needed
4. **See file count**: Window title updates with total files selected
5. **Try analysis**: Click "Analyze Compatibility" to see confirmation dialog

## UI Features

- ✨ Modern, clean design with rounded corners
- 🎨 Color-coded buttons (green=add, orange=remove, red=clear, blue=analyze)
- 📋 File lists show selected files by name
- 💬 Confirmation dialogs before analysis
- ⚠️ Warning if no files selected

## Next Steps

**Step 2**: Browser selection panel (Chrome, Firefox, Safari, Edge with version inputs)

**Step 3**: Connect to analyzer engine and show progress

**Step 4**: Display results with charts and tables

## File Structure

```
src/gui/
├── __init__.py          # GUI module exports
├── app.py               # Application entry point
└── main_window.py       # Main window with file selection

run_gui.py               # Launcher script (use this!)
```

## Tips

- You can select multiple files at once using Shift/Cmd+Click
- File paths are stored but only filenames are displayed
- The app remembers your selections until you clear them
- Window title shows total file count

---

**Status**: Step 1 Complete ✅  
**Next**: Browser Selection Panel
