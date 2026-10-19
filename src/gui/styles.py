"""
GUI 样式定义 — 白色纯净风格，参考 Claude 桌面版
"""

# 颜色系统
COLORS = {
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F9F9F9",
    "bg_sidebar": "#F5F5F5",
    "bg_input": "#FFFFFF",
    "bg_hover": "#EEEEEE",
    "bg_user_bubble": "#F0F0F0",
    "bg_agent_bubble": "#FFFFFF",
    "bg_button_primary": "#1A1A1A",
    "bg_button_primary_hover": "#333333",
    "bg_button_secondary": "#E8E8E8",
    "bg_button_secondary_hover": "#D8D8D8",
    "bg_card": "#FAFAFA",
    "bg_card_border": "#E5E5E5",

    "text_primary": "#1A1A1A",
    "text_secondary": "#666666",
    "text_tertiary": "#999999",
    "text_inverse": "#FFFFFF",
    "text_link": "#2563EB",

    "border": "#E5E5E5",
    "border_light": "#F0F0F0",
    "border_focus": "#2563EB",

    "accent": "#2563EB",
    "accent_hover": "#1D4ED8",
    "success": "#16A34A",
    "warning": "#F59E0B",
    "error": "#DC2626",
}

# 字体
FONT_FAMILY = "'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif"
FONT_MONO = "'Cascadia Code', 'Consolas', 'Courier New', monospace"

# 全局 QSS
GLOBAL_QSS = f"""
QMainWindow {{
    background-color: {COLORS['bg_primary']};
}}

QWidget {{
    font-family: {FONT_FAMILY};
    font-size: 14px;
    color: {COLORS['text_primary']};
    background-color: {COLORS['bg_primary']};
}}

QScrollArea {{
    border: none;
    background-color: {COLORS['bg_primary']};
}}

QScrollBar:vertical {{
    border: none;
    background: {COLORS['bg_secondary']};
    width: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['text_tertiary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
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
    padding: 16px;
    border-bottom: 1px solid {COLORS['border']};
}}

#sidebar_title {{
    font-size: 16px;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

#new_chat_btn {{
    background-color: {COLORS['bg_button_primary']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 500;
}}

#new_chat_btn:hover {{
    background-color: {COLORS['bg_button_primary_hover']};
}}

#conversation_list {{
    background-color: {COLORS['bg_sidebar']};
    border: none;
}}

#conversation_item {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 12px;
    text-align: left;
    font-size: 13px;
    color: {COLORS['text_secondary']};
}}

#conversation_item:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

#conversation_item:selected {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
    font-weight: 500;
}}

#settings_btn {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 12px;
    text-align: left;
    font-size: 13px;
    color: {COLORS['text_secondary']};
}}

#settings_btn:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
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
    padding: 16px;
}}

#message_input {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent']};
}}

#message_input:focus {{
    border-color: {COLORS['border_focus']};
}}

#send_btn {{
    background-color: {COLORS['bg_button_primary']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 14px;
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
    background-color: {COLORS['bg_button_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 13px;
}}

#export_btn:hover {{
    background-color: {COLORS['bg_button_secondary_hover']};
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
    border-radius: 12px;
    padding: 12px 16px;
    margin: 4px 40px 4px 80px;
}}

#agent_bubble {{
    background-color: {COLORS['bg_agent_bubble']};
    border: 1px solid {COLORS['border_light']};
    border-radius: 12px;
    padding: 12px 16px;
    margin: 4px 80px 4px 40px;
}}

#message_label {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    font-size: 14px;
    line-height: 1.6;
}}

#plan_card {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['bg_card_border']};
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    font-family: {FONT_MONO};
    font-size: 13px;
}}

#search_result {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['bg_card_border']};
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}}

#search_result_title {{
    font-size: 14px;
    font-weight: 600;
    color: {COLORS['text_link']};
}}

#search_result_meta {{
    font-size: 12px;
    color: {COLORS['text_secondary']};
}}

#search_result_abstract {{
    font-size: 13px;
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
    font-size: 18px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    padding: 16px;
    border-bottom: 1px solid {COLORS['border']};
}}

QLabel {{
    font-size: 13px;
    color: {COLORS['text_secondary']};
}}

QLineEdit {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
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
    font-size: 13px;
}}

QSpinBox {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}}

QCheckBox {{
    font-size: 13px;
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
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
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 500;
}}

#save_btn:hover {{
    background-color: {COLORS['bg_button_primary_hover']};
}}

#cancel_btn {{
    background-color: {COLORS['bg_button_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
}}

#cancel_btn:hover {{
    background-color: {COLORS['bg_button_secondary_hover']};
}}
"""
