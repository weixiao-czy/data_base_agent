"""
GUI 样式定义 — 现代 IDE 风格，参考 Cursor/VS Code
"""

# 颜色系统 — 深色侧边栏 + 浅色内容区
COLORS = {
    # 顶栏
    "titlebar_bg": "#FFFFFF",
    "titlebar_text": "#1A1A1A",
    "titlebar_btn_hover": "#F0F0F0",

    # 侧边栏（深色）
    "sidebar_bg": "#252526",
    "sidebar_text": "#CCCCCC",
    "sidebar_text_active": "#FFFFFF",
    "sidebar_hover": "#2A2D2E",
    "sidebar_active": "#37373D",
    "sidebar_icon": "#858585",
    "sidebar_icon_active": "#FFFFFF",
    "sidebar_section": "#6E6E6E",
    "sidebar_border": "#1E1E1E",

    # 内容区
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F9F9F9",
    "bg_input": "#FFFFFF",
    "bg_hover": "#F0F0F0",
    "bg_user_bubble": "#F0F0F0",
    "bg_agent_bubble": "#FFFFFF",

    # 按钮
    "bg_button_primary": "#1A1A1A",
    "bg_button_primary_hover": "#333333",
    "bg_button_secondary": "#E8E8E8",
    "bg_button_secondary_hover": "#D8D8D8",

    # 文字
    "text_primary": "#1A1A1A",
    "text_secondary": "#666666",
    "text_tertiary": "#999999",
    "text_inverse": "#FFFFFF",
    "text_link": "#2563EB",
    "text_sidebar": "#CCCCCC",
    "text_sidebar_active": "#FFFFFF",

    # 边框
    "border": "#E5E5E5",
    "border_light": "#F0F0F0",
    "border_focus": "#2563EB",
    "border_sidebar": "#3C3C3C",

    # 强调色
    "accent": "#2563EB",
    "accent_hover": "#1D4ED8",
    "success": "#16A34A",
    "warning": "#F59E0B",
    "error": "#DC2626",

    # Badge
    "badge_bg": "#2563EB",
    "badge_text": "#FFFFFF",
}

# 字体
FONT_FAMILY = "'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif"
FONT_MONO = "'Cascadia Code', 'Consolas', 'Courier New', monospace"
FONT_ICON = "'Segoe Fluent Icons', 'Font Awesome 6 Free', sans-serif"

# 全局 QSS
GLOBAL_QSS = f"""
QMainWindow {{
    background-color: {COLORS['bg_primary']};
}}

QWidget {{
    font-family: {FONT_FAMILY};
    font-size: 13px;
    color: {COLORS['text_primary']};
    background-color: {COLORS['bg_primary']};
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['text_tertiary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""

# 自定义顶栏
TITLEBAR_QSS = f"""
#titlebar {{
    background-color: {COLORS['titlebar_bg']};
    border-bottom: 1px solid {COLORS['border']};
    min-height: 36px;
    max-height: 36px;
}}

#titlebar_title {{
    font-size: 12px;
    color: {COLORS['titlebar_text']};
    padding-left: 12px;
}}

#titlebar_btn {{
    background-color: transparent;
    border: none;
    color: {COLORS['titlebar_text']};
    font-size: 16px;
    padding: 0 12px;
    min-width: 36px;
    max-width: 36px;
}}

#titlebar_btn:hover {{
    background-color: {COLORS['titlebar_btn_hover']};
}}

#titlebar_close:hover {{
    background-color: {COLORS['error']};
    color: {COLORS['text_inverse']};
}}
"""

# 侧边栏（现代 IDE 风格）
SIDEBAR_QSS = f"""
#sidebar {{
    background-color: {COLORS['sidebar_bg']};
    border-right: 1px solid {COLORS['border_sidebar']};
}}

#sidebar_top {{
    background-color: {COLORS['sidebar_bg']};
    padding: 8px 0;
    border-bottom: 1px solid {COLORS['border_sidebar']};
}}

#sidebar_mode_btn {{
    background-color: {COLORS['sidebar_hover']};
    color: {COLORS['text_sidebar_active']};
    border: 1px solid {COLORS['border_sidebar']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    font-weight: 500;
    margin: 0 8px;
}}

#sidebar_mode_btn:hover {{
    background-color: {COLORS['sidebar_active']};
}}

#sidebar_nav {{
    background-color: {COLORS['sidebar_bg']};
    border: none;
    padding: 8px 0;
}}

#sidebar_nav::item {{
    background-color: transparent;
    color: {COLORS['text_sidebar']};
    padding: 8px 12px;
    font-size: 13px;
    border: none;
}}

#sidebar_nav::item:hover {{
    background-color: {COLORS['sidebar_hover']};
    color: {COLORS['text_sidebar_active']};
}}

#sidebar_nav::item:selected {{
    background-color: {COLORS['sidebar_active']};
    color: {COLORS['text_sidebar_active']};
}}

#sidebar_section_title {{
    background-color: transparent;
    color: {COLORS['sidebar_section']};
    font-size: 11px;
    font-weight: 600;
    padding: 12px 12px 6px 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

#sidebar_conv_list {{
    background-color: {COLORS['sidebar_bg']};
    border: none;
    padding: 0 8px;
}}

#sidebar_conv_list::item {{
    background-color: transparent;
    color: {COLORS['text_sidebar']};
    padding: 6px 8px;
    font-size: 12px;
    border-radius: 4px;
    margin: 2px 0;
}}

#sidebar_conv_list::item:hover {{
    background-color: {COLORS['sidebar_hover']};
    color: {COLORS['text_sidebar_active']};
}}

#sidebar_conv_list::item:selected {{
    background-color: {COLORS['sidebar_active']};
    color: {COLORS['text_sidebar_active']};
}}

#sidebar_bottom {{
    background-color: {COLORS['sidebar_bg']};
    border-top: 1px solid {COLORS['border_sidebar']};
    padding: 8px 0;
}}

#sidebar_settings_btn {{
    background-color: transparent;
    color: {COLORS['text_sidebar']};
    border: none;
    padding: 8px 12px;
    font-size: 13px;
    text-align: left;
    border-radius: 4px;
    margin: 0 8px;
}}

#sidebar_settings_btn:hover {{
    background-color: {COLORS['sidebar_hover']};
    color: {COLORS['text_sidebar_active']};
}}

#badge {{
    background-color: {COLORS['badge_bg']};
    color: {COLORS['badge_text']};
    font-size: 10px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 10px;
    margin-left: 8px;
}}
"""

# 聊天区域
CHAT_QSS = f"""
#chat_area {{
    background-color: {COLORS['bg_primary']};
}}

#input_area {{
    background-color: {COLORS['bg_primary']};
    border-top: 1px solid {COLORS['border']};
    padding: 12px 16px;
}}

#message_input {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent']};
}}

#message_input:focus {{
    border-color: {COLORS['border_focus']};
}}

#message_input::placeholder {{
    color: {COLORS['text_tertiary']};
}}

#send_btn {{
    background-color: {COLORS['bg_button_primary']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 500;
}}

#send_btn:hover {{
    background-color: {COLORS['bg_button_primary_hover']};
}}

#send_btn:disabled {{
    background-color: {COLORS['bg_button_secondary']};
    color: {COLORS['text_tertiary']};
}}

#export_btn {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
}}

#export_btn:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

#toolbar {{
    background-color: {COLORS['bg_primary']};
    border-bottom: 1px solid {COLORS['border_light']};
    padding: 8px 16px;
}}
"""

# 消息气泡
MESSAGE_QSS = f"""
#user_bubble {{
    background-color: {COLORS['bg_user_bubble']};
    border-radius: 10px;
    padding: 10px 14px;
    margin: 4px 40px 4px 80px;
}}

#agent_bubble {{
    background-color: {COLORS['bg_agent_bubble']};
    border: 1px solid {COLORS['border_light']};
    border-radius: 10px;
    padding: 10px 14px;
    margin: 4px 80px 4px 40px;
}}

#message_label {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    font-size: 13px;
    line-height: 1.6;
}}

#plan_card {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    font-family: {FONT_MONO};
    font-size: 12px;
}}

#search_result {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}}

#search_result_title {{
    font-size: 13px;
    font-weight: 600;
    color: {COLORS['text_link']};
}}

#search_result_meta {{
    font-size: 11px;
    color: {COLORS['text_secondary']};
}}

#search_result_abstract {{
    font-size: 12px;
    color: {COLORS['text_secondary']};
    margin-top: 6px;
}}
"""

# 设置对话框
SETTINGS_QSS = f"""
#settings_dialog {{
    background-color: {COLORS['bg_primary']};
}}

#settings_title {{
    font-size: 16px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    padding: 16px 20px;
    border-bottom: 1px solid {COLORS['border']};
}}

QLabel {{
    font-size: 12px;
    color: {COLORS['text_secondary']};
}}

QLineEdit {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    color: {COLORS['text_primary']};
}}

QLineEdit:focus {{
    border-color: {COLORS['border_focus']};
}}

QComboBox {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}}

QSpinBox {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}}

QCheckBox {{
    font-size: 12px;
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {COLORS['border']};
    border-radius: 3px;
    background-color: {COLORS['bg_input']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent']};
    border-color: {COLORS['accent']};
}}

#save_btn {{
    background-color: {COLORS['bg_button_primary']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
}}

#save_btn:hover {{
    background-color: {COLORS['bg_button_primary_hover']};
}}

#cancel_btn {{
    background-color: {COLORS['bg_button_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
}}

#cancel_btn:hover {{
    background-color: {COLORS['bg_button_secondary_hover']};
}}
"""
