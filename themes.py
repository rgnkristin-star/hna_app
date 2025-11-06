# themes.py

LIGHT_THEME_CSS = """
<style>
/* FORCE LIGHT THEME - IGNORE SYSTEM PREFERENCE */
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] * {
    color-scheme: light only !important;
    forced-color-adjust: none !important;
}

/* Override any dark theme variables from Streamlit */
:root {
    --primary-color: #007bff !important;
    --secondary-color: #0056b3 !important;
    --background-color: #f8f9fa !important;
    --sidebar-background: #e9ecef !important;
    --card-background: #ffffff !important;
    --text-color: #212529 !important;
    --border-color: #dee2e6 !important;
    --success-color: #28a745 !important;
    --warning-color: #ffc107 !important;
    --error-color: #dc3545 !important;
    --info-color: #17a2b8 !important;
}

/* Force light theme on all Streamlit containers */
[data-testid="stAppViewContainer"] {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
    color-scheme: light only !important;
}

.main .block-container {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}

/* Sidebar - force light colors */
[data-testid="stSidebar"] {
    background-color: var(--sidebar-background) !important;
    color: var(--text-color) !important;
    border-right: 2px solid var(--primary-color) !important;
}

/* Force all text to be dark */
[data-testid="stAppViewContainer"] * {
    color: var(--text-color) !important;
}

/* Specifically target sidebar text */
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: var(--text-color) !important;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: var(--primary-color) !important;
}

/* Buttons */
.stButton button {
    background-color: var(--primary-color) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
}

.stButton button:hover {
    background-color: var(--secondary-color) !important;
    color: white !important;
}

/* Input fields - ensure white background */
.stTextInput input, 
.stSelectbox select, 
.stNumberInput input,
.stTextArea textarea {
    background-color: white !important;
    color: var(--text-color) !important;
    border: 2px solid var(--border-color) !important;
}

/* Radio buttons */
.stRadio > div {
    background-color: white !important;
    color: var(--text-color) !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    background-color: white !important;
    color: var(--text-color) !important;
}

/* Forms */
[data-testid="stForm"] {
    background-color: var(--card-background) !important;
    border: 1px solid var(--border-color) !important;
}

/* Alerts */
div[data-testid="stAlert"] {
    background-color: rgba(23, 162, 184, 0.1) !important;
    border: 1px solid var(--info-color) !important;
    color: var(--text-color) !important;
}

/* Markdown */
.stMarkdown {
    color: var(--text-color) !important;
}

.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: var(--primary-color) !important;
}

/* Override any dark theme classes that Streamlit might add */
[data-theme="dark"],
[theme="dark"] {
    display: none !important;
}

/* Force light scrollbars */
::-webkit-scrollbar {
    background: #f1f1f1 !important;
}

::-webkit-scrollbar-thumb {
    background: #c1c1c1 !important;
}

</style>
"""

DARK_THEME_CSS = """
<style>
/* Dark theme - juga force independent dari sistem */
* {
    color-scheme: dark only !important;
}

:root {
    --primary-color: #6c8eff !important;
    --secondary-color: #8fa8ff !important;
    --background-color: #0e1117 !important;
    --sidebar-background: #1e1e1e !important;
    --card-background: #2d2d2d !important;
    --text-color: #f0f0f0 !important;
    --border-color: #444444 !important;
    --success-color: #00d4aa !important;
    --warning-color: #ffb300 !important;
    --error-color: #ff4b4b !important;
    --info-color: #00c0f2 !important;
}

[data-testid="stAppViewContainer"] {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}

.main .block-container {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}

section[data-testid="stSidebar"] {
    background-color: var(--sidebar-background) !important;
    color: var(--text-color) !important;
}

.stButton button {
    background-color: var(--primary-color) !important;
    color: #000000 !important;
}

div, p, span, label, h1, h2, h3, h4, h5, h6 {
    color: var(--text-color) !important;
}

</style>
"""

FULL_COLOR_THEME_CSS = """
<style>
/* Full color theme - force independent */
* {
    color-scheme: light only !important;
}

:root {
    --primary-color: #ff6b6b !important;
    --secondary-color: #ff8e8e !important;
    --background-color: #f7f9fc !important;
    --sidebar-background: #4ecdc4 !important;
    --card-background: #ffffff !important;
    --text-color: #2c3e50 !important;
    --border-color: #45b7af !important;
    --success-color: #1dd1a1 !important;
    --warning-color: #feca57 !important;
    --error-color: #ff6b6b !important;
    --info-color: #48dbfb !important;
}

[data-testid="stAppViewContainer"] {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}

.main .block-container {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}

section[data-testid="stSidebar"] {
    background: var(--sidebar-background) !important;
    color: #ffffff !important;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

.stButton button {
    background-color: var(--primary-color) !important;
    color: white !important;
}

div, p, span, label, h1, h2, h3, h4, h5, h6 {
    color: var(--text-color) !important;
}

</style>
"""

def get_theme_css(theme_name):
    """Return CSS based on theme name"""
    themes = {
        "light": LIGHT_THEME_CSS,
        "dark": DARK_THEME_CSS,
        "full_color": FULL_COLOR_THEME_CSS
    }
    return themes.get(theme_name, LIGHT_THEME_CSS)