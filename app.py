"""
Question Tagging Tool with Session Persistence - Streamlit App

This version includes automatic session persistence that survives internet disconnections.
Session data is saved to a local file and automatically restored on page reload.
"""

import streamlit as st
import pandas as pd
import io
import json
import os
from typing import Dict, List, Tuple
from datetime import datetime
import pickle

# Page configuration
st.set_page_config(
    page_title="Question Tagging Tool",
    page_icon="📚",
    layout="wide"
)

# Session file path
SESSION_FILE = "session_backup.pkl"
AUTO_SAVE_INTERVAL = 10  # seconds

def save_session_to_file():
    """Save the current session state to a local file."""
    try:
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'question_tags': st.session_state.get('question_tags', {}),
            'question_mappings': st.session_state.get('question_mappings', {}),
            'question_col': st.session_state.get('question_col', 'Question'),
            'answer_col': st.session_state.get('answer_col', 'Answer'),
            'uploaded_file_name': st.session_state.get('uploaded_file_name', None),
            'questions_data': st.session_state.get('questions_data', None)
        }
        
        with open(SESSION_FILE, 'wb') as f:
            pickle.dump(session_data, f)
        
        st.session_state.last_save_time = datetime.now()
        return True
    except Exception as e:
        print(f"Error saving session: {e}")
        return False

def load_session_from_file():
    """Load session state from a local file."""
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'rb') as f:
                session_data = pickle.load(f)
            
            # Restore session state
            st.session_state.question_tags = session_data.get('question_tags', {})
            st.session_state.question_mappings = session_data.get('question_mappings', {})
            st.session_state.question_col = session_data.get('question_col', 'Question')
            st.session_state.answer_col = session_data.get('answer_col', 'Answer')
            st.session_state.uploaded_file_name = session_data.get('uploaded_file_name', None)
            st.session_state.questions_data = session_data.get('questions_data', None)
            st.session_state.session_restored = True
            
            return session_data.get('timestamp', None)
    except Exception as e:
        print(f"Error loading session: {e}")
    return None

def auto_save_check():
    """Check if it's time to auto-save."""
    if 'last_save_time' not in st.session_state:
        st.session_state.last_save_time = datetime.now()
    
    time_since_save = (datetime.now() - st.session_state.last_save_time).total_seconds()
    if time_since_save > AUTO_SAVE_INTERVAL:
        save_session_to_file()

def load_subjects_data() -> pd.DataFrame:
    """Load the subjects hierarchy from Excel file."""
    try:
        # Try the double extension first, then single extension
        try:
            df = pd.read_excel("Subjects.xlsx.xlsx")
        except FileNotFoundError:
            df = pd.read_excel("Subjects.xlsx")
        
        # Ensure required columns exist
        required_cols = ['Subject', 'Topic', 'Subtopic']
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Missing required column '{col}' in Subjects file. Found columns: {list(df.columns)}")
                return pd.DataFrame()
        
        return df
    except Exception as e:
        st.error(f"Error loading Subjects file: {str(e)}")
        return pd.DataFrame()

def get_hierarchy_data(subjects_df: pd.DataFrame) -> Dict:
    """Create hierarchy dictionary for dependent dropdowns."""
    hierarchy = {}
    
    for _, row in subjects_df.iterrows():
        subject = row['Subject']
        topic = row['Topic']
        subtopic = row['Subtopic']
        
        if subject not in hierarchy:
            hierarchy[subject] = {}
        
        if topic not in hierarchy[subject]:
            hierarchy[subject][topic] = []
        
        if subtopic not in hierarchy[subject][topic]:
            hierarchy[subject][topic].append(subtopic)
    
    return hierarchy

def create_table_with_dropdowns(questions_df: pd.DataFrame, hierarchy: Dict):
    """Create an Excel-like table with dropdowns for tagging questions."""
    
    # Initialize session state for storing selections
    if 'question_tags' not in st.session_state:
        st.session_state.question_tags = {}
    
    # Initialize session state for multiple mappings per question
    if 'question_mappings' not in st.session_state:
        st.session_state.question_mappings = {}
    
    # Get all unique subjects for the subject dropdown
    all_subjects = list(hierarchy.keys())
    
    # Create table header
    st.markdown("### Tag Questions")
    
    # Auto-save status indicator
    col1, col2 = st.columns([8, 2])
    with col2:
        last_save = st.session_state.get('last_save_time', None)
        if last_save:
            time_ago = (datetime.now() - last_save).total_seconds()
            if time_ago < 60:
                st.caption(f"✅ Auto-saved {int(time_ago)}s ago")
            else:
                st.caption(f"✅ Auto-saved {int(time_ago/60)}m ago")
    
    # Create the table structure using columns
    header_cols = st.columns([0.3, 2.0, 2.0, 1.2, 1.2, 1.2, 0.8])  # Added Answer column
    with header_cols[0]:
        st.markdown("**#**")
    with header_cols[1]:
        st.markdown("**Question**")
    with header_cols[2]:
        st.markdown("**Answer**")
    with header_cols[3]:
        st.markdown("**Subject**")
    with header_cols[4]:
        st.markdown("**Topic**")
    with header_cols[5]:
        st.markdown("**Subtopic**")
    with header_cols[6]:
        st.markdown("**Actions**")
    
    st.markdown("---")
    
    # Track if any changes were made
    changes_made = False
    
    # Create rows for each question
    for idx, row in questions_df.iterrows():
        question = row[st.session_state.get('question_col', 'Question')]
        answer = row[st.session_state.get('answer_col', 'Answer')]
        
        # Initialize mappings for this question if not exists
        if idx not in st.session_state.question_mappings:
            st.session_state.question_mappings[idx] = [{'Subject': '', 'Topic': '', 'Subtopic': ''}]
        
        # Display each mapping for this question
        for mapping_idx, mapping in enumerate(st.session_state.question_mappings[idx]):
            # Create columns for this row
            row_cols = st.columns([0.3, 2.0, 2.0, 1.2, 1.2, 1.2, 0.8])
            
            # Number column (only show for first mapping)
            with row_cols[0]:
                if mapping_idx == 0:
                    st.markdown(f"**{idx + 1}**")
                else:
                    st.markdown("")
            
            # Question column (only show for first mapping)
            with row_cols[1]:
                if mapping_idx == 0:
                    st.markdown(f"*{question}*")
                else:
                    st.markdown("")
            
            # Answer column (only show for first mapping)
            with row_cols[2]:
                if mapping_idx == 0:
                    st.markdown(f"*{answer}*")
                else:
                    st.markdown("")
            
            # Subject dropdown
            with row_cols[3]:
                subject_key = f"subject_{idx}_{mapping_idx}"
                current_subject = mapping.get('Subject', '')
                subject_index = all_subjects.index(current_subject) + 1 if current_subject in all_subjects else 0
                
                selected_subject = st.selectbox(
                    "",
                    options=[""] + all_subjects,
                    key=subject_key,
                    index=subject_index,
                    label_visibility="collapsed"
                )
                
                if selected_subject != current_subject:
                    changes_made = True
            
            # Topic dropdown (dependent on subject)
            with row_cols[4]:
                topic_options = [""]
                topic_index = 0
                
                if selected_subject and selected_subject != "":
                    topic_options = [""] + list(hierarchy[selected_subject].keys())
                    current_topic = mapping.get('Topic', '')
                    if current_topic in topic_options:
                        topic_index = topic_options.index(current_topic)
                
                topic_key = f"topic_{idx}_{mapping_idx}"
                selected_topic = st.selectbox(
                    "",
                    options=topic_options,
                    key=topic_key,
                    index=topic_index,
                    label_visibility="collapsed"
                )
                
                if selected_topic != mapping.get('Topic', ''):
                    changes_made = True
            
            # Subtopic dropdown (dependent on subject and topic)
            with row_cols[5]:
                subtopic_options = [""]
                subtopic_index = 0
                
                if selected_subject and selected_topic and selected_subject != "" and selected_topic != "":
                    subtopic_options = [""] + hierarchy[selected_subject][selected_topic]
                    current_subtopic = mapping.get('Subtopic', '')
                    if current_subtopic in subtopic_options:
                        subtopic_index = subtopic_options.index(current_subtopic)
                
                subtopic_key = f"subtopic_{idx}_{mapping_idx}"
                selected_subtopic = st.selectbox(
                    "",
                    options=subtopic_options,
                    key=subtopic_key,
                    index=subtopic_index,
                    label_visibility="collapsed"
                )
                
                if selected_subtopic != mapping.get('Subtopic', ''):
                    changes_made = True
            
            # Action buttons
            with row_cols[6]:
                button_cols = st.columns(2)
                
                # Add mapping button (only show for last mapping)
                if mapping_idx == len(st.session_state.question_mappings[idx]) - 1:
                    with button_cols[0]:
                        if st.button("➕", key=f"add_{idx}", help="Add another mapping"):
                            st.session_state.question_mappings[idx].append({'Subject': '', 'Topic': '', 'Subtopic': ''})
                            changes_made = True
                            st.rerun()
                
                # Delete mapping button (only show if more than one mapping)
                if len(st.session_state.question_mappings[idx]) > 1:
                    with button_cols[1]:
                        if st.button("🗑️", key=f"delete_{idx}_{mapping_idx}", help="Delete this mapping"):
                            st.session_state.question_mappings[idx].pop(mapping_idx)
                            changes_made = True
                            st.rerun()
            
            # Update the mapping in session state
            st.session_state.question_mappings[idx][mapping_idx] = {
                'Subject': selected_subject if selected_subject != "" else '',
                'Topic': selected_topic if selected_topic != "" else '',
                'Subtopic': selected_subtopic if selected_subtopic != "" else ''
            }
        
        # Store question and answer data for export
        st.session_state.question_tags[idx] = {
            'Question': question,
            'Answer': answer,
            'Mappings': st.session_state.question_mappings[idx]
        }
        
        # Add separator line between questions
        st.markdown("---")
    
    # Auto-save if changes were made
    if changes_made:
        save_session_to_file()

def main():
    # Title and clear button in the same row
    col1, col2 = st.columns([10, 1])
    with col1:
        st.title("📚 Question Tagging Tool")
    with col2:
        st.write("")  # Add spacing
        st.write("")  # Add spacing
        if st.button("🔄 Clear", help="Clear all data and start fresh"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Delete session file
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            
            st.rerun()
    
    st.markdown("Upload your Questions.xlsx file and tag each question with Subject → Topic → Subtopic")
    
    # Check for and load existing session
    if 'session_restored' not in st.session_state:
        restore_time = load_session_from_file()
        if restore_time:
            st.info(f"♻️ Restored previous session from {restore_time}")
    
    # Auto-save check
    auto_save_check()
    
    # Load subjects data
    subjects_df = load_subjects_data()
    if subjects_df.empty:
        st.error("Could not load Subjects.xlsx file. Please ensure it exists in the project directory.")
        return
    
    # Create hierarchy for dropdowns
    hierarchy = get_hierarchy_data(subjects_df)
    
    st.success(f"Loaded {len(subjects_df)} subject-topic-subtopic combinations")
    
    # File upload or use restored data
    uploaded_file = st.file_uploader("Upload Questions.xlsx", type=['xlsx'])
    
    # Check if we have restored questions data
    if uploaded_file is None and 'questions_data' in st.session_state and st.session_state.questions_data is not None:
        # Use restored data
        questions_df = st.session_state.questions_data
        st.info(f"Using previously uploaded file: {st.session_state.get('uploaded_file_name', 'Questions.xlsx')}")
    elif uploaded_file is not None:
        try:
            # Read questions file
            questions_df = pd.read_excel(uploaded_file)
            
            # Store for session persistence
            st.session_state.questions_data = questions_df
            st.session_state.uploaded_file_name = uploaded_file.name
            
            # Save session after upload
            save_session_to_file()
            
            # Check for required columns (case-insensitive)
            columns_lower = [col.strip().lower() for col in questions_df.columns]
            required_columns = ['question', 'answer']
            
            # Find actual column names
            question_col = None
            answer_col = None
            
            for col in questions_df.columns:
                if col.strip().lower() == 'question':
                    question_col = col
                elif col.strip().lower() == 'answer':
                    answer_col = col
            
            missing_columns = []
            if not question_col:
                missing_columns.append('Question')
            if not answer_col:
                missing_columns.append('Answer')
            
            if missing_columns:
                st.error(f"Questions file must contain columns: Question, Answer. Missing: {', '.join(missing_columns)}")
                st.info(f"Found columns: {list(questions_df.columns)}")
                return
            
            # Store column names in session state
            st.session_state.question_col = question_col
            st.session_state.answer_col = answer_col
            
            st.success(f"Loaded {len(questions_df)} questions")
            
        except Exception as e:
            st.error(f"Error processing questions file: {str(e)}")
            return
    else:
        questions_df = None
    
    if questions_df is not None:
        # Display questions in table format with dropdowns
        st.markdown("---")
        create_table_with_dropdowns(questions_df, hierarchy)
        
        # Export functionality
        st.markdown("### Export Tagged Questions")
        
        # Check if all questions are tagged
        tagged_count = 0
        total_mappings = 0
        for tags in st.session_state.question_tags.values():
            for mapping in tags.get('Mappings', []):
                total_mappings += 1
                if mapping['Subject'] and mapping['Topic'] and mapping['Subtopic']:
                    tagged_count += 1
        
        st.info(f"Tagged mappings: {tagged_count}/{total_mappings}")
        
        if st.button("📥 Export Tagged Questions", type="primary"):
            # Create export DataFrame with multiple rows for multiple mappings
            export_data = []
            for idx, tags in st.session_state.question_tags.items():
                mappings = tags.get('Mappings', [])
                
                # If there are valid mappings, create a row for each
                valid_mappings = [m for m in mappings if m['Subject'] or m['Topic'] or m['Subtopic']]
                
                if valid_mappings:
                    for mapping in valid_mappings:
                        export_data.append({
                            'Question': tags['Question'],
                            'Answer': tags['Answer'],
                            'Subject': mapping['Subject'] or '',
                            'Topic': mapping['Topic'] or '',
                            'Subtopic': mapping['Subtopic'] or ''
                        })
                else:
                    # If no valid mappings, still include the question with empty tags
                    export_data.append({
                        'Question': tags['Question'],
                        'Answer': tags['Answer'],
                        'Subject': '',
                        'Topic': '',
                        'Subtopic': ''
                    })
            
            export_df = pd.DataFrame(export_data)
            
            # Convert to Excel bytes
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Tagged Questions')
            
            excel_data = output.getvalue()
            
            # Download button
            st.download_button(
                label="📥 Download Tagged Questions Excel",
                data=excel_data,
                file_name="tagged_questions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success("✅ Export ready! Click the download button above.")
            
            # Show preview
            with st.expander("Preview Export Data"):
                st.dataframe(export_df)
    
    # Sidebar information
    with st.sidebar:
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. **Upload** your Questions.xlsx file
        2. **Select** Subject → Topic → Subtopic for each question
        3. **Export** and download the tagged questions
        """)
        
        st.markdown("### 📊 File Requirements")
        st.markdown("""
        **Subjects.xlsx:** Should contain columns:
        - Subject
        - Topic  
        - Subtopic
        
        **Questions.xlsx:** Should contain columns:
        - Question
        - Answer
        """)
        
        st.markdown("### 🔄 Auto-Save Enabled")
        st.markdown("""
        ✅ Your work is automatically saved every 10 seconds
        
        ✅ Session persists even if internet disconnects
        
        ✅ Automatically restored when you reload the page
        """)
        
        # Show session file info
        if os.path.exists(SESSION_FILE):
            file_size = os.path.getsize(SESSION_FILE) / 1024  # KB
            file_time = datetime.fromtimestamp(os.path.getmtime(SESSION_FILE))
            st.caption(f"Session file: {file_size:.1f} KB")
            st.caption(f"Last saved: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()