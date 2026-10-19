"""
设计系统 — 温暖中性色 + 陶土色点缀，参考成熟商业桌面应用
间距基准 4px，字号阶梯 11/12/13/14/16/20
"""

COLORS = {
    # 强调色（陶土色）
    "accent": "#D97757",
    "accent_hover": "#C96442",
    "accent_soft": "#F7EBE5",

    # 背景
    "bg_main": "#FFFFFF",
    "bg_titlebar": "#FAF9F7",
    "bg_sidebar": "#F5F4F0",
    "bg_subtle": "#F7F6F3",
    "bg_user_bubble": "#F0EFE9",
    "bg_hover": "#ECEAE4",
    "bg_selected": "#E8E6DF",

    # 文字
    "text_primary": "#2B2A26",
    "text_secondary": "#6E6C66",
    "text_tertiary": "#A3A19A",
    "text_inverse": "#FFFFFF",

    # 边框
    "border": "#E7E5E0",
    "border_light": "#F0EEEA",
    "border_strong": "#D9D7D1",

    # 状态
    "success": "#3F8F5B",
    "warning": "#C98A2D",
    "error": "#C4483E",

    # 兼容旧键
    "primary": "#D97757",
    "primary_hover": "#C96442",
}

FONT_FAMILY = "'Segoe UI', 'Microsoft YaHei UI', 'PingFang SC', sans-serif"
FONT_MONO = "'Cascadia Code', 'Consolas', 'Microsoft YaHei UI', monospace"

# ---------------------------------------------------------------- 全局

GLOBAL_QSS = f"""
* {{
    outline: none;
}}

QMainWindow {{
    background-color: {COLORS['bg_main']};
}}

QWidget {{
    font-family: {FONT_FAMILY};
    font-size: 13px;
    color: {COLORS['text_primary']};
}}

QLabel {{
    background: transparent;
}}

QToolTip {{
    background-color: {COLORS['text_primary']};
    color: {COLORS['text_inverse']};
    border: none;
    padding: 5px 9px;
    font-size: 12px;
    border-radius: 4px;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 10px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['border_strong']};
    border-radius: 3px;
    min-height: 36px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['text_tertiary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    height: 0;
}}
"""

# ---------------------------------------------------------------- 标题栏

TITLEBAR_QSS = f"""
#titlebar {{
    background-color: {COLORS['bg_titlebar']};
    border-bottom: 1px solid {COLORS['border']};
}}

#titlebar_logo {{
    background-color: {COLORS['accent']};
    color: {COLORS['text_inverse']};
    border-radius: 5px;
    font-size: 11px;
    font-weight: 700;
}}

#titlebar_title {{
    font-size: 12px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
}}

#win_btn {{
    background: transparent;
    border: none;
    border-radius: 6px;
    color: {COLORS['text_secondary']};
    font-size: 11px;
    min-width: 40px;
    max-width: 40px;
    min-height: 28px;
    max-height: 28px;
}}

#win_btn:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

#win_close {{
    background: transparent;
    border: none;
    border-radius: 6px;
    color: {COLORS['text_secondary']};
    font-size: 11px;
    min-width: 40px;
    max-width: 40px;
    min-height: 28px;
    max-height: 28px;
}}

#win_close:hover {{
    background-color: {COLORS['error']};
    color: {COLORS['text_inverse']};
}}
"""

# ---------------------------------------------------------------- 侧边栏

SIDEBAR_QSS = f"""
#sidebar {{
    background-color: {COLORS['bg_sidebar']};
    border-right: 1px solid {COLORS['border']};
}}

#new_chat_btn {{
    background-color: {COLORS['accent']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 9px;
    padding: 9px 14px;
    font-size: 13px;
    font-weight: 600;
    text-align: left;
}}

#new_chat_btn:hover {{
    background-color: {COLORS['accent_hover']};
}}

#new_chat_btn:pressed {{
    background-color: {COLORS['accent_hover']};
}}

#section_title {{
    color: {COLORS['text_tertiary']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    background: transparent;
}}

#conv_list {{
    background: transparent;
    border: none;
    font-size: 12.5px;
}}

#conv_list::item {{
    background: transparent;
    color: {COLORS['text_secondary']};
    padding: 9px 12px;
    border-radius: 8px;
    margin: 1px 0;
    border: none;
}}

#conv_list::item:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

#conv_list::item:selected {{
    background-color: {COLORS['bg_selected']};
    color: {COLORS['text_primary']};
    font-weight: 600;
}}

#sidebar_footer {{
    background: transparent;
    border-top: 1px solid {COLORS['border']};
}}

#footer_btn {{
    background: transparent;
    border: none;
    border-radius: 8px;
    color: {COLORS['text_secondary']};
    font-size: 12.5px;
    text-align: left;
    padding: 8px 12px;
}}

#footer_btn:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}
"""

# ---------------------------------------------------------------- 聊天区

CHAT_QSS = f"""
#chat_panel {{
    background-color: {COLORS['bg_main']};
}}

#messages_container {{
    background-color: {COLORS['bg_main']};
}}

#chat_header {{
    background-color: {COLORS['bg_main']};
    border-bottom: 1px solid {COLORS['border_light']};
}}

#chat_header_title {{
    font-size: 13.5px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    background: transparent;
}}

#chat_header_status {{
    font-size: 12px;
    color: {COLORS['text_tertiary']};
    background: transparent;
}}

#ghost_btn {{
    background: transparent;
    border: none;
    border-radius: 7px;
    color: {COLORS['text_secondary']};
    font-size: 12px;
    padding: 6px 11px;
}}

#ghost_btn:hover {{
    background-color: {COLORS['bg_subtle']};
    color: {COLORS['text_primary']};
}}

#ghost_btn:disabled {{
    color: {COLORS['text_tertiary']};
}}

#input_dock {{
    background-color: {COLORS['bg_main']};
}}

#input_card {{
    background-color: {COLORS['bg_main']};
    border: 1px solid {COLORS['border']};
    border-radius: 14px;
}}

#message_input {{
    background: transparent;
    border: none;
    font-size: 13.5px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_soft']};
    selection-color: {COLORS['text_primary']};
}}

#input_hint {{
    color: {COLORS['text_tertiary']};
    font-size: 11px;
    background: transparent;
}}

#send_btn {{
    background-color: {COLORS['accent']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 17px;
    font-size: 15px;
    font-weight: 600;
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
}}

#send_btn:hover {{
    background-color: {COLORS['accent_hover']};
}}

#send_btn:disabled {{
    background-color: {COLORS['border']};
    color: {COLORS['text_tertiary']};
}}
"""

# ---------------------------------------------------------------- 消息与卡片

MESSAGE_QSS = f"""
#agent_text {{
    color: {COLORS['text_primary']};
    font-size: 13.5px;
    background: transparent;
}}

#user_bubble {{
    background-color: {COLORS['bg_user_bubble']};
    border-radius: 16px;
    border: 1px solid {COLORS['border_light']};
}}

#user_bubble_text {{
    color: {COLORS['text_primary']};
    font-size: 13.5px;
    background: transparent;
}}

#avatar_agent {{
    background-color: {COLORS['accent']};
    color: {COLORS['text_inverse']};
    border-radius: 15px;
    font-size: 13px;
    font-weight: 700;
}}

#avatar_user {{
    background-color: {COLORS['bg_selected']};
    color: {COLORS['text_secondary']};
    border-radius: 15px;
    font-size: 12px;
    font-weight: 600;
}}

#thinking_label {{
    color: {COLORS['text_tertiary']};
    font-size: 13px;
    background: transparent;
}}

#welcome_title {{
    font-size: 21px;
    font-weight: 700;
    color: {COLORS['text_primary']};
    background: transparent;
}}

#welcome_sub {{
    font-size: 13px;
    color: {COLORS['text_secondary']};
    background: transparent;
}}

#welcome_logo {{
    background-color: {COLORS['accent']};
    color: {COLORS['text_inverse']};
    border-radius: 14px;
    font-size: 22px;
    font-weight: 700;
}}

#suggestion_chip {{
    background-color: {COLORS['bg_main']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    color: {COLORS['text_secondary']};
    font-size: 12.5px;
    padding: 10px 14px;
    text-align: left;
}}

#suggestion_chip:hover {{
    border-color: {COLORS['accent']};
    color: {COLORS['text_primary']};
    background-color: {COLORS['accent_soft']};
}}

#plan_card_widget {{
    background-color: {COLORS['bg_main']};
    border: 1px solid {COLORS['border']};
    border-radius: 14px;
}}

#plan_card_header {{
    background-color: {COLORS['bg_subtle']};
    border-top-left-radius: 13px;
    border-top-right-radius: 13px;
    border-bottom: 1px solid {COLORS['border_light']};
}}

#plan_card_title {{
    font-size: 14px;
    font-weight: 700;
    color: {COLORS['text_primary']};
    background: transparent;
}}

#plan_card_badge {{
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    color: {COLORS['accent']};
    background: transparent;
}}

#plan_section_label {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    color: {COLORS['text_tertiary']};
    background: transparent;
}}

#plan_section_value {{
    font-size: 13px;
    color: {COLORS['text_primary']};
    background: transparent;
}}

#paper_card {{
    background-color: {COLORS['bg_main']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
}}

#paper_card:hover {{
    border-color: {COLORS['border_strong']};
}}

#paper_title {{
    font-size: 13.5px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    background: transparent;
}}

#paper_meta {{
    font-size: 12px;
    color: {COLORS['text_secondary']};
    background: transparent;
}}

#paper_abstract {{
    font-size: 12.5px;
    color: {COLORS['text_secondary']};
    background: transparent;
}}

#paper_badge {{
    font-size: 10px;
    font-weight: 600;
    color: {COLORS['accent']};
    background-color: {COLORS['accent_soft']};
    border-radius: 4px;
    padding: 2px 7px;
}}

#paper_link {{
    font-size: 11.5px;
    color: {COLORS['text_tertiary']};
    background: transparent;
}}

#results_count_label {{
    font-size: 12px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
    background: transparent;
}}
"""

# ---------------------------------------------------------------- 设置对话框

SETTINGS_QSS = f"""
#settings_dialog {{
    background-color: {COLORS['bg_main']};
}}

#settings_title {{
    font-size: 17px;
    font-weight: 700;
    color: {COLORS['text_primary']};
    padding: 18px 24px 14px 24px;
    background: transparent;
}}

QTabWidget::pane {{
    border: none;
    border-top: 1px solid {COLORS['border']};
    background: {COLORS['bg_main']};
}}

QTabBar::tab {{
    background: transparent;
    color: {COLORS['text_secondary']};
    font-size: 13px;
    padding: 9px 18px;
    border: none;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
    color: {COLORS['accent']};
    font-weight: 600;
    border-bottom: 2px solid {COLORS['accent']};
}}

QTabBar::tab:hover {{
    color: {COLORS['text_primary']};
}}

QLabel {{
    font-size: 12.5px;
    color: {COLORS['text_secondary']};
    background: transparent;
}}

QLineEdit {{
    background-color: {COLORS['bg_main']};
    border: 1px solid {COLORS['border_strong']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_soft']};
}}

QLineEdit:focus {{
    border-color: {COLORS['accent']};
}}

QSpinBox {{
    background-color: {COLORS['bg_main']};
    border: 1px solid {COLORS['border_strong']};
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 13px;
}}

QSpinBox:focus {{
    border-color: {COLORS['accent']};
}}

#save_btn {{
    background-color: {COLORS['accent']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 8px;
    padding: 9px 26px;
    font-size: 13px;
    font-weight: 600;
}}

#save_btn:hover {{
    background-color: {COLORS['accent_hover']};
}}

#cancel_btn {{
    background-color: {COLORS['bg_main']};
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border_strong']};
    border-radius: 8px;
    padding: 9px 26px;
    font-size: 13px;
}}

#cancel_btn:hover {{
    background-color: {COLORS['bg_subtle']};
    color: {COLORS['text_primary']};
}}
"""
