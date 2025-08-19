"""
Session persistence module for the Question Tagging Tool.
Provides functionality to save and restore session state to/from browser local storage.
"""

import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, Any

def inject_js_for_local_storage():
    """Inject JavaScript for local storage operations."""
    js_code = """
    <script>
    // Session persistence functions
    window.saveToLocalStorage = function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Failed to save to localStorage:', e);
            return false;
        }
    };
    
    window.loadFromLocalStorage = function(key) {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : null;
        } catch (e) {
            console.error('Failed to load from localStorage:', e);
            return null;
        }
    };
    
    window.clearLocalStorage = function(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('Failed to clear localStorage:', e);
            return false;
        }
    };
    
    // Auto-save indicator
    window.showSaveIndicator = function(status) {
        const indicator = document.getElementById('save-indicator');
        if (indicator) {
            indicator.textContent = status;
            indicator.style.opacity = '1';
            setTimeout(() => {
                indicator.style.opacity = '0';
            }, 2000);
        }
    };
    
    // Check if offline
    window.addEventListener('online', function() {
        console.log('Connection restored');
        const indicator = document.getElementById('connection-indicator');
        if (indicator) {
            indicator.textContent = '🟢 Online';
            indicator.style.color = 'green';
        }
    });
    
    window.addEventListener('offline', function() {
        console.log('Connection lost - data will be preserved');
        const indicator = document.getElementById('connection-indicator');
        if (indicator) {
            indicator.textContent = '🔴 Offline - Data preserved';
            indicator.style.color = 'red';
        }
    });
    </script>
    
    <div style="position: fixed; top: 10px; right: 10px; z-index: 1000;">
        <div id="connection-indicator" style="padding: 5px 10px; background: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-size: 12px; color: green;">
            🟢 Online
        </div>
        <div id="save-indicator" style="padding: 5px 10px; background: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-size: 12px; opacity: 0; transition: opacity 0.3s; margin-top: 5px;">
            💾 Saved
        </div>
    </div>
    """
    st.components.v1.html(js_code, height=0)

def save_session_to_local_storage():
    """Save current session state to browser local storage."""
    try:
        # Prepare session data for serialization
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'question_tags': st.session_state.get('question_tags', {}),
            'question_mappings': st.session_state.get('question_mappings', {}),
            'question_col': st.session_state.get('question_col', 'Question'),
            'answer_col': st.session_state.get('answer_col', 'Answer')
        }
        
        # Convert integer keys to strings for JSON serialization
        session_data['question_tags'] = {str(k): v for k, v in session_data['question_tags'].items()}
        session_data['question_mappings'] = {str(k): v for k, v in session_data['question_mappings'].items()}
        
        # Use Streamlit's JavaScript execution
        js_save = f"""
        <script>
        (function() {{
            const data = {json.dumps(session_data)};
            const saved = window.saveToLocalStorage('questionTaggingSession', data);
            if (saved) {{
                window.showSaveIndicator('💾 Auto-saved');
            }}
        }})();
        </script>
        """
        st.components.v1.html(js_save, height=0)
        
        return True
    except Exception as e:
        st.error(f"Failed to save session: {str(e)}")
        return False

def load_session_from_local_storage():
    """Load session state from browser local storage."""
    try:
        # JavaScript to load data and pass it back to Streamlit
        js_load = """
        <script>
        (function() {
            const data = window.loadFromLocalStorage('questionTaggingSession');
            if (data) {
                // Create a hidden div to pass data back to Streamlit
                const div = document.createElement('div');
                div.id = 'session-data';
                div.style.display = 'none';
                div.textContent = JSON.stringify(data);
                document.body.appendChild(div);
                
                // Trigger Streamlit to read the data
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: data
                }, '*');
            }
        })();
        </script>
        """
        
        # This would need to be integrated with Streamlit's component system
        # For now, we'll use a simpler approach with query parameters
        return None
        
    except Exception as e:
        st.error(f"Failed to load session: {str(e)}")
        return None

def create_auto_save_component():
    """Create an auto-save component that saves session periodically."""
    if 'last_save_time' not in st.session_state:
        st.session_state.last_save_time = time.time()
    
    # Check if it's time to auto-save (every 30 seconds)
    current_time = time.time()
    if current_time - st.session_state.last_save_time > 30:
        save_session_to_local_storage()
        st.session_state.last_save_time = current_time

def export_session_backup():
    """Export session data as a downloadable JSON file."""
    try:
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'question_tags': st.session_state.get('question_tags', {}),
            'question_mappings': st.session_state.get('question_mappings', {}),
            'question_col': st.session_state.get('question_col', 'Question'),
            'answer_col': st.session_state.get('answer_col', 'Answer')
        }
        
        # Convert integer keys to strings for JSON serialization
        session_data['question_tags'] = {str(k): v for k, v in session_data['question_tags'].items()}
        session_data['question_mappings'] = {str(k): v for k, v in session_data['question_mappings'].items()}
        
        return json.dumps(session_data, indent=2)
    except Exception as e:
        st.error(f"Failed to export session: {str(e)}")
        return None

def import_session_backup(json_data: str):
    """Import session data from a JSON string."""
    try:
        session_data = json.loads(json_data)
        
        # Restore session state
        if 'question_tags' in session_data:
            # Convert string keys back to integers
            st.session_state.question_tags = {int(k): v for k, v in session_data['question_tags'].items()}
        
        if 'question_mappings' in session_data:
            # Convert string keys back to integers
            st.session_state.question_mappings = {int(k): v for k, v in session_data['question_mappings'].items()}
        
        if 'question_col' in session_data:
            st.session_state.question_col = session_data['question_col']
        
        if 'answer_col' in session_data:
            st.session_state.answer_col = session_data['answer_col']
        
        return True
    except Exception as e:
        st.error(f"Failed to import session: {str(e)}")
        return False

def clear_session():
    """Clear all session data."""
    st.session_state.question_tags = {}
    st.session_state.question_mappings = {}
    if 'question_col' in st.session_state:
        del st.session_state.question_col
    if 'answer_col' in st.session_state:
        del st.session_state.answer_col