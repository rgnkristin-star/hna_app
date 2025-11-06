import streamlit as st
from db import SessionLocal
from models import UserManager

class SidebarManager:
    def __init__(self, session):
        self.session = session
        self.user_mgr = UserManager(session)
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'login' not in st.session_state:
            st.session_state['login'] = False
            st.session_state['username'] = ""
            st.session_state['role'] = ""
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
    
    def render_theme_selector(self):
        """Render theme selector in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎨 Pilih Tema")
        
        theme_options = {
            "Light": "light",
            "Dark": "dark", 
            "Full Color": "full_color"
        }
        
        current_theme = st.session_state.theme
        current_theme_name = [k for k, v in theme_options.items() if v == current_theme][0]
        
        selected_theme_name = st.sidebar.selectbox(
            "Tema Aplikasi",
            options=list(theme_options.keys()),
            index=list(theme_options.keys()).index(current_theme_name),
            label_visibility="collapsed"
        )
        
        selected_theme = theme_options[selected_theme_name]
        
        if selected_theme != st.session_state.theme:
            st.session_state.theme = selected_theme
            st.rerun()
    
    def render_login_form(self):
        """Render login form in sidebar"""
        st.sidebar.title("🔐 Login")
        with st.sidebar.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            login_btn = st.form_submit_button("Login", use_container_width=True)
            
            if login_btn:
                if self.user_mgr.login(username, password):
                    st.success(f"Login berhasil! Halo {username}")
                    st.rerun()
                else:
                    st.error("Username atau password salah")
    
    def render_main_menu(self):
        """Render main menu after login"""
        # User info section
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"### 👋 Halo, {st.session_state['username']}")
        st.sidebar.markdown(f"**Role:** {st.session_state['role']}")
        
        # Theme selector
        self.render_theme_selector()
        
        st.sidebar.markdown("---")
        
        # Navigation menu
        menu_items = self._get_menu_items()
        
        # Create navigation
        selected_menu = st.sidebar.radio(
            "📋 Menu Navigasi",
            options=[item['label'] for item in menu_items],
            format_func=lambda x: f"{x}"
        )
        
        # Logout button at bottom
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            self.logout()
        
        return selected_menu
    
    def _get_menu_items(self):
        """Get available menu items based on user role"""
        base_menus = [
            {"label": "📤 Upload Data", "value": "Upload Data", "roles": ["user", "admin"]},
            {"label": "📊 Tampilan Data", "value": "Tampilan Data", "roles": ["user", "admin"]},
            {"label": "🩺 Upload Pemeriksaan Penunjang", "value": "Upload Penunjang", "roles": ["user", "admin"]},
            {"label": "📋 Tampilan Pemeriksaan Penunjang", "value": "Tampilan Penunjang", "roles": ["user", "admin"]},
        ]
        
        # Add admin-only menus
        if st.session_state['role'] == 'admin':
            base_menus.append({"label": "👥 Manajemen User", "value": "Manajemen User", "roles": ["admin"]})
        
        return base_menus
    
    def get_selected_page(self):
        """Get the actual page value from selected menu label"""
        menu_items = self._get_menu_items()
        selected_label = st.session_state.get('selected_menu', 'Upload Data')
        
        for item in menu_items:
            if item['label'] == selected_label:
                return item['value']
        return "Upload Data"
    
    def logout(self):
        """Handle logout process"""
        st.session_state['login'] = False
        st.session_state['username'] = ""
        st.session_state['role'] = ""
        st.session_state.pop('selected_menu', None)
        st.rerun()
    
    def render_sidebar(self):
        """Main method to render entire sidebar"""
        if not st.session_state['login']:
            self.render_login_form()
            return None
        else:
            selected_menu = self.render_main_menu()
            # Store selected menu in session state
            st.session_state['selected_menu'] = selected_menu
            
            # Return the actual page value
            return self._get_page_value_from_label(selected_menu)
    
    def _get_page_value_from_label(self, label):
        """Convert menu label to page value"""
        menu_items = self._get_menu_items()
        for item in menu_items:
            if item['label'] == label:
                return item['value']
        return "Upload Data"