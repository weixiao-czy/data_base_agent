"""
GUI 样式定义 — 专业现代风格
"""

# 颜色系统
COLORS = {
    # 主色调
    "primary": "#0078D4",
    "primary_hover": "#106EBE",
    "primary_light": "#DEECF9",

    # 背景
    "bg_main": "#FFFFFF",
    "bg_sidebar": "#F3F2F1",
    "bg_header": "#FAFAFA",
    "bg_input": "#FFFFFF",
    "bg_hover": "#F3F2F1",
    "bg_selected": "#E5F3FF",
    "bg_user_msg": "#F3F2F1",
    "bg_agent_msg": "#FFFFFF",

    # 文字
    "text_primary": "#323130",
    "text_secondary": "#605E5C",
    "text_tertiary": "#A19F9D",
    "text_inverse": "#FFFFFF",
    "text_link": "#0078D4",

    # 边框
    "border": "#E1DFDD",
    "border_light": "#F3F2F1",
    "border_focus": "#0078D4",

    # 按钮
    "btn_primary": "#0078D4",
    "btn_primary_hover": "#106EBE",
    "btn_secondary": "#FFFFFF",
    "btn_secondary_hover": "#F3F2F1",
    "btn_secondary_border": "#8A8886",

    # 状态
    "success": "#107C10",
    "warning": "#FFB900",
    "error": "#D13438",

    # 侧边栏图标
    "icon_default": "#605E5C",
    "icon_active": "#0078D4",
}

# 字体
FONT_FAMILY = "'Segoe UI', 'Microsoft YaHei UI', 'PingFang SC', sans-serif"
FONT_MONO = "'Cascadia Code', 'Consolas', monospace"

# 全局样式
GLOBAL_QSS = f"""
QMainWindow {{
    background-color: {COLORS['bg_main']};
}}

QWidget {{
    font-family: {FONT_FAMILY};
    font-size: 13px;
    color: {COLORS['text_primary']};
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

# 顶栏
TITLEBAR_QSS = f"""
#titlebar {{
    background-color: {COLORS['bg_header']};
    border-bottom: 1px solid {COLORS['border']};
    min-height: 40px;
    max-height: 40px;
}}

#titlebar_title {{
    font-size: 12px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    padding-left: 16px;
}}

#titlebar_btn {{
    background-color: transparent;
    border: none;
    color: {COLORS['text_primary']};
    font-size: 10px;
    padding: 0;
    min-width: 46px;
    max-width: 46px;
    min-height: 40px;
    max-height: 40px;
}}

#titlebar_btn:hover {{
    background-color: {COLORS['bg_hover']};
}}

#titlebar_close:hover {{
    background-color: {COLORS['error']};
    color: {COLORS['text_inverse']};
}}
"""

# 侧边栏
SIDEBAR_QSS = f"""
#sidebar {{
    background-color: {COLORS['bg_sidebar']};
    border-right: 1px solid {COLORS['border']};
}}

#sidebar_header {{
    background-color: {COLORS['bg_sidebar']};
    padding: 16px 12px 12px 12px;
    border-bottom: 1px solid {COLORS['border']};
}}

#new_chat_btn {{
    background-color: {COLORS['btn_primary']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    width: 100%;
}}

#new_chat_btn:hover {{
    background-color: {COLORS['btn_primary_hover']};
}}

#sidebar_sections {{
    background-color: {COLORS['bg_sidebar']};
    border: none;
    padding: 8px 0;
}}

#sidebar_sections::item {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    padding: 8px 16px;
    font-size: 13px;
    border: none;
}}

#sidebar_sections::item:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

#sidebar_sections::item:selected {{
    background-color: {COLORS['bg_selected']};
    color: {COLORS['primary']};
    font-weight: 600;
}}

#section_title {{
    background-color: transparent;
    color: {COLORS['text_tertiary']};
    font-size: 11px;
    font-weight: 600;
    padding: 12px 16px 6px 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

#conv_list {{
    background-color: {COLORS['bg_sidebar']};
    border: none;
    padding: 0 8px;
}}

#conv_list::item {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    padding: 8px 12px;
    font-size: 12px;
    border-radius: 4px;
    margin: 2px 0;
    border: none;
}}

#conv_list::item:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

#conv_list::item:selected {{
    background-color: {COLORS['bg_selected']};
    color: {COLORS['primary']};
    font-weight: 500;
}}

#sidebar_footer {{
    background-color: {COLORS['bg_sidebar']};
    border-top: 1px solid {COLORS['border']};
    padding: 8px 12px;
}}

#settings_btn {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    padding: 8px 12px;
    font-size: 13px;
    text-align: left;
    border-radius: 4px;
    width: 100%;
}}

#settings_btn:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}
"""

# 聊天区
CHAT_QSS = f"""
#chat_container {{
    background-color: {COLORS['bg_main']};
}}

#toolbar {{
    background-color: {COLORS['bg_main']};
    border-bottom: 1px solid {COLORS['border_light']};
    padding: 8px 16px;
}}

#export_btn {{
    background-color: {COLORS['btn_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['btn_secondary_border']};
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    margin-right: 8px;
}}

#export_btn:hover {{
    background-color: {COLORS['btn_secondary_hover']};
}}

#input_area {{
    background-color: {COLORS['bg_main']};
    border-top: 1px solid {COLORS['border']};
    padding: 16px;
}}

#message_input {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 10px 14px;
    font-size: 13px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['primary_light']};
}}

#message_input:focus {{
    border-color: {COLORS['border_focus']};
}}

#message_input::placeholder {{
    color: {COLORS['text_tertiary']};
}}

#send_btn {{
    background-color: {COLORS['btn_primary']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    margin-left: 12px;
}}

#send_btn:hover {{
    background-color: {COLORS['btn_primary_hover']};
}}

#send_btn:disabled {{
    background-color: {COLORS['border']};
    color: {COLORS['text_tertiary']};
}}
"""

# 消息气泡
MESSAGE_QSS = f"""
#user_bubble {{
    background-color: {COLORS['bg_user_msg']};
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 60px 8px 100px;
    border: 1px solid {COLORS['border_light']};
}}

#agent_bubble {{
    background-color: {COLORS['bg_agent_msg']};
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 100px 8px 60px;
    border: 1px solid {COLORS['border']};
}}

#message_label {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    font-size: 13px;
    line-height: 1.6;
}}

#plan_card {{
    background-color: {COLORS['bg_header']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 12px;
    margin: 8px 0;
    font-family: {FONT_MONO};
    font-size: 12px;
}}

#search_result {{
    background-color: {COLORS['bg_header']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
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
    background-color: {COLORS['bg_main']};
}}

#settings_title {{
    font-size: 18px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    padding: 20px 24px;
    border-bottom: 1px solid {COLORS['border']};
}}

QLabel {{
    font-size: 12px;
    color: {COLORS['text_secondary']};
}}

QLineEdit {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
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
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 12px;
}}

QSpinBox {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
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
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

#save_btn {{
    background-color: {COLORS['btn_primary']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 4px;
    padding: 8px 24px;
    font-size: 13px;
    font-weight: 600;
}}

#save_btn:hover {{
    background-color: {COLORS['btn_primary_hover']};
}}

#cancel_btn {{
    background-color: {COLORS['btn_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['btn_secondary_border']};
    border-radius: 4px;
    padding: 8px 24px;
    font-size: 13px;
}}

#cancel_btn:hover {{
    background-color: {COLORS['btn_secondary_hover']};
}}
"""
