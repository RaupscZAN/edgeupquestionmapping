# Question Tagging Tool

A Streamlit-based application for tagging questions with hierarchical categories (Subject → Topic → Subtopic). Features automatic session persistence to protect your work even during internet disconnections.

## Features

- **Excel-like Interface**: Intuitive table layout for easy question tagging
- **Dependent Dropdowns**: Topic options update based on subject selection, subtopic options based on topic
- **Multiple Mappings**: Tag each question with multiple subject/topic/subtopic combinations
- **Auto-Save**: Your work is automatically saved every 10 seconds
- **Session Persistence**: Work is preserved even if internet connection is lost
- **Easy Export**: Download tagged questions as an Excel file

## Quick Start

### Option 1: Using Batch Files (Windows - Easiest)

1. **First time setup:**
   - Double-click `setup_windows.bat`

2. **Run the app:**
   - Double-click `run.bat`

### Option 2: Manual Installation

1. **Install Python** (if not already installed):
   - Download from https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at http://localhost:8501

## Usage

1. **Prepare your files:**
   - Ensure `Subjects.xlsx` is in the app directory (contains hierarchy data)
   - Have your `Questions.xlsx` file ready for upload

2. **Upload and Tag:**
   - Upload your Questions.xlsx file
   - For each question, select Subject → Topic → Subtopic
   - Use ➕ to add multiple mappings per question
   - Use 🗑️ to remove unwanted mappings

3. **Export Results:**
   - Click "Export Tagged Questions" when done
   - Download the Excel file with all tagged data

## Session Management

- **Auto-Save**: Work saves automatically every 10 seconds
- **Clear Button**: Click "🔄 Clear" in top-right to start fresh
- **Session Recovery**: Reload the page to restore previous session

## File Requirements

**Subjects.xlsx:**
- Must contain columns: Subject, Topic, Subtopic
- Defines the hierarchical structure for tagging

**Questions.xlsx:**
- Must contain columns: Question, Answer
- Your questions to be tagged

## Technical Details

- Built with Streamlit
- Uses pandas for data manipulation
- Session data stored in `session_backup.pkl`
- Supports offline work when run locally