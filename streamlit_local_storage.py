"""
Enhanced local storage integration for Streamlit using components.
This module provides a more robust way to persist data in the browser.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from typing import Any, Dict

# Create a custom component for local storage operations
_local_storage_component = components.declare_component(
    "local_storage",
    path=None  # We'll use inline HTML/JS
)

def get_local_storage_manager():
    """Get or create the local storage manager component."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <script>
        // LocalStorage manager for Streamlit
        class LocalStorageManager {
            constructor() {
                this.storageKey = 'questionTaggingSession';
                this.initializeMessageHandler();
            }
            
            initializeMessageHandler() {
                window.addEventListener('message', (event) => {
                    if (event.data.type === 'save') {
                        this.saveData(event.data.payload);
                    } else if (event.data.type === 'load') {
                        this.loadData();
                    } else if (event.data.type === 'clear') {
                        this.clearData();
                    }
                });
            }
            
            saveData(data) {
                try {
                    localStorage.setItem(this.storageKey, JSON.stringify(data));
                    this.sendMessage('save_success', true);
                } catch (e) {
                    console.error('Failed to save:', e);
                    this.sendMessage('save_error', e.message);
                }
            }
            
            loadData() {
                try {
                    const data = localStorage.getItem(this.storageKey);
                    const parsed = data ? JSON.parse(data) : null;
                    this.sendMessage('load_success', parsed);
                } catch (e) {
                    console.error('Failed to load:', e);
                    this.sendMessage('load_error', e.message);
                }
            }
            
            clearData() {
                try {
                    localStorage.removeItem(this.storageKey);
                    this.sendMessage('clear_success', true);
                } catch (e) {
                    console.error('Failed to clear:', e);
                    this.sendMessage('clear_error', e.message);
                }
            }
            
            sendMessage(type, data) {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: { type, data }
                }, '*');
            }
        }
        
        // Initialize manager
        const manager = new LocalStorageManager();
        
        // Auto-load on startup
        setTimeout(() => manager.loadData(), 100);
        </script>
    </head>
    <body>
        <div id="status" style="font-size: 12px; color: #666;">
            LocalStorage Manager Ready
        </div>
    </body>
    </html>
    """
    
    return components.html(html_content, height=30)

def create_persistent_state():
    """Create a persistent state manager using cookies as fallback."""
    
    # JavaScript code for cookie-based persistence
    cookie_js = """
    <script>
    // Cookie-based persistence for offline support
    function setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = name + '=' + encodeURIComponent(value) + ';expires=' + expires.toUTCString() + ';path=/';
    }
    
    function getCookie(name) {
        const nameEQ = name + '=';
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) {
                return decodeURIComponent(c.substring(nameEQ.length, c.length));
            }
        }
        return null;
    }
    
    // Save session data to cookie
    window.saveSessionToCookie = function(data) {
        setCookie('question_tagging_session', JSON.stringify(data), 7); // 7 days
    };
    
    // Load session data from cookie
    window.loadSessionFromCookie = function() {
        const data = getCookie('question_tagging_session');
        return data ? JSON.parse(data) : null;
    };
    </script>
    """
    
    st.components.v1.html(cookie_js, height=0)

def save_state_with_persistence(key: str, value: Any):
    """Save state to both session state and browser storage."""
    st.session_state[key] = value
    
    # Prepare data for storage
    storage_data = {
        'question_tags': st.session_state.get('question_tags', {}),
        'question_mappings': st.session_state.get('question_mappings', {}),
        'question_col': st.session_state.get('question_col', 'Question'),
        'answer_col': st.session_state.get('answer_col', 'Answer'),
        'timestamp': str(pd.Timestamp.now())
    }
    
    # Convert to JSON-serializable format
    storage_data['question_tags'] = {str(k): v for k, v in storage_data['question_tags'].items()}
    storage_data['question_mappings'] = {str(k): v for k, v in storage_data['question_mappings'].items()}
    
    # Save using JavaScript
    js_code = f"""
    <script>
    (function() {{
        const data = {json.dumps(storage_data)};
        
        // Save to localStorage
        try {{
            localStorage.setItem('questionTaggingSession', JSON.stringify(data));
        }} catch (e) {{
            console.error('LocalStorage failed:', e);
        }}
        
        // Save to cookie as fallback
        window.saveSessionToCookie(data);
    }})();
    </script>
    """
    
    st.components.v1.html(js_code, height=0)