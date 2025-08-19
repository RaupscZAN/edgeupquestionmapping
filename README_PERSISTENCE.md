# Session Persistence Feature

## Overview

The Question Tagging Tool now includes automatic session persistence that protects your work even if your internet connection is lost. Your tagging progress is automatically saved every 10 seconds and whenever you make changes.

## How to Use

### Running the App with Persistence

To use the version with session persistence, run:

```bash
streamlit run app_with_persistence.py
```

### Features

1. **Automatic Saving**
   - Your work is automatically saved every 10 seconds
   - Auto-save status indicator shows when your work was last saved
   - No manual intervention needed

2. **Offline Protection**
   - If you lose internet connection, your work continues to be saved locally
   - When connection is restored, you can continue where you left off

3. **Session Recovery**
   - When you reload the page, your previous session is automatically restored
   - Includes all tagged questions, mappings, and even the uploaded file reference

4. **Clear Button**
   - "🔄 Clear" button in the top-right corner to start fresh
   - Removes all data and returns to initial state
   - All data stored locally in `session_backup.pkl`

## Technical Details

### Storage Method
- Uses Python's pickle module to serialize session data
- Stores data in a local file (`session_backup.pkl`)
- Includes all question tags, mappings, and column configurations

### What's Saved
- Question tags and mappings
- Selected subjects, topics, and subtopics
- Uploaded file reference and data
- Column names from the Questions file
- Timestamp of last save

### Limitations
- The persistence file is stored locally on the server
- If using Streamlit Cloud, persistence only works within the same session
- For true offline capability, run the app locally

## Running Locally for Best Offline Support

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   streamlit run app_with_persistence.py
   ```

3. Your work will be saved to `session_backup.pkl` in the app directory

## Fallback Options

If you need to manually backup/restore your session:

1. The app creates a `session_backup.pkl` file
2. Copy this file to backup your session
3. Place it in the app directory to restore a session

## Original Version

The original app without persistence is still available:
```bash
streamlit run app.py
```