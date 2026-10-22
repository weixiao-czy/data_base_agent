"""
设计系统 — 商业级三层架构

1. 设计令牌（Tokens）：颜色 / 字阶 / 圆角 / 间距全部集中在顶部常量，
   组件样式只引用令牌，不写死色值。
2. 状态模型：每个可交互组件统一实现五态
   normal → hover（加深一档）→ pressed（再加深一档，主按钮附带 1px 按压位移）
   focus（陶土色焦点环）→ disabled（降饱和降对比）。
   QSS 不支持 CSS transition，流畅感靠「同色相阶梯式加深」而非跳色。
3. 组件样式块：GLOBAL → TITLEBAR → SIDEBAR → CHAT → MESSAGE → SETTINGS，
   块内按「容器 → 交互控件 → 文字标签」排序。
"""

COLORS = {
    # 品牌色（陶土色阶梯）
    "accent": "#D97757",
    "accent_hover": "#C96442",
    "accent_pressed": "#B6532F",
    "accent_soft": "#F7EBE5",
    "accent_soft_hover": "#F1DFD2",

    # 背景层级（从底到顶）
    "bg_main": "#FFFFFF",
    "bg_titlebar": "#FAF9F7",
    "bg_sidebar": "#F5F4F0",
    "bg_subtle": "#F7F6F3",
    "bg_card_hover": "#FBFAF7",
    "bg_user_bubble": "#F0EFE9",
    "bg_hover": "#ECEAE4",
    "bg_pressed": "#E2E0D9",
    "bg_selected": "#E8E6DF",

    # 文字
    "text_primary": "#2B2A26",
    "text_secondary": "#6E6C66",
    "text_tertiary": "#A3A19A",
    "text_inverse": "#FFFFFF",

    # 边框
    "border": "#E7E5E0",
    "border_hover": "#CFCDC5",
    "border_light": "#F0EEEA",
    "border_strong": "#D9D7D1",

    # 语义
    "success": "#3F8F5B",
    "warning": "#C98A2D",
    "error": "#C4483E",
    "error_hover": "#B03A31",
    "error_pressed": "#99322A",
    "error_soft": "#FBEAE7",
    "error_soft_hover": "#F7DCD7",
    "error_soft_pressed": "#F2CFC9",
    "error_soft_disabled": "#FCF3F1",
    "error_border": "#F0C7C0",
    "error_border_hover": "#E5A89F",
    "error_border_pressed": "#DB958B",
    "error_border_disabled": "#F3DFDB",
    "error_text_disabled": "#C9A6A1",

    # 兼容旧键
    "primary": "#D97757",
    "primary_hover": "#C96442",
}

FONT_FAMILY = "'Segoe UI', 'Microsoft YaHei UI', 'PingFang SC', sans-serif"
FONT_MONO = "'Cascadia Code', 'Consolas', 'Microsoft YaHei UI', monospace"

# 圆角阶梯：控件 sm / 按钮 md / 卡片 lg / 气泡 xl
RADIUS = {"sm": "6px", "md": "9px", "lg": "13px", "xl": "16px"}

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
    border-radius: {RADIUS['sm']};
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

QScrollBar::handle:vertical:pressed {{
    background: {COLORS['text_secondary']};
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
    border-radius: {RADIUS['sm']};
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

#win_btn:pressed {{
    background-color: {COLORS['bg_pressed']};
    color: {COLORS['text_primary']};
}}

#win_close {{
    background: transparent;
    border: none;
    border-radius: {RADIUS['sm']};
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

#win_close:pressed {{
    background-color: {COLORS['error_pressed']};
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
    border-radius: {RADIUS['md']};
    padding: 9px 14px;
    font-size: 13px;
    font-weight: 600;
    text-align: left;
}}

#new_chat_btn:hover {{
    background-color: {COLORS['accent_hover']};
}}

#new_chat_btn:pressed {{
    background-color: {COLORS['accent_pressed']};
    padding: 10px 14px 8px 14px;
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
    padding: 0px;
    border-radius: 8px;
    margin: 1px 0;
    border: none;
}}

#conv_list::item:hover {{
    background-color: {COLORS['bg_hover']};
}}

#conv_list::item:selected {{
    background-color: {COLORS['bg_selected']};
}}

#conv_row_label {{
    color: {COLORS['text_secondary']};
    font-size: 12.5px;
    background: transparent;
}}

#conv_row_label[selected="true"] {{
    color: {COLORS['text_primary']};
    font-weight: 600;
}}

#conv_del_btn {{
    background: transparent;
    border: none;
    border-radius: {RADIUS['sm']};
    color: {COLORS['text_tertiary']};
    font-size: 10px;
}}

#conv_del_btn:hover {{
    background-color: #F4E0DC;
    color: {COLORS['error']};
}}

#conv_del_btn:pressed {{
    background-color: #EDD3CD;
    color: {COLORS['error_hover']};
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

#footer_btn:pressed {{
    background-color: {COLORS['bg_pressed']};
    color: {COLORS['text_primary']};
    padding: 9px 12px 7px 12px;
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

#ghost_btn:pressed {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
    padding: 7px 11px 5px 11px;
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

#input_card[focused="true"] {{
    border: 1px solid {COLORS['accent']};
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

#send_btn:pressed {{
    background-color: {COLORS['accent_pressed']};
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
    border-radius: {RADIUS['xl']};
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

#suggestion_chip:pressed {{
    border-color: {COLORS['accent_hover']};
    color: {COLORS['text_primary']};
    background-color: {COLORS['accent_soft_hover']};
    padding: 11px 14px 9px 14px;
}}

/* ---- 可点击选项（替代命令行敲 1 / 敲 A） ---- */

#option_btn {{
    background-color: {COLORS['bg_main']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    color: {COLORS['text_primary']};
    font-size: 13px;
    padding: 8px 14px;
    text-align: left;
}}

#option_btn:hover {{
    border-color: {COLORS['accent']};
    background-color: {COLORS['accent_soft']};
}}

#option_btn:pressed {{
    border-color: {COLORS['accent_hover']};
    background-color: {COLORS['accent_soft_hover']};
    padding: 9px 14px 7px 14px;
}}

#option_btn:disabled {{
    color: {COLORS['text_tertiary']};
    background-color: {COLORS['bg_subtle']};
    border-color: {COLORS['border_light']};
}}

#option_btn_other {{
    background-color: transparent;
    border: 1px dashed {COLORS['border_strong']};
    border-radius: 10px;
    color: {COLORS['text_secondary']};
    font-size: 12.5px;
    padding: 8px 14px;
    text-align: left;
}}

#option_btn_other:hover {{
    border-color: {COLORS['accent']};
    color: {COLORS['accent']};
    background-color: {COLORS['accent_soft']};
}}

#option_btn_other:pressed {{
    background-color: {COLORS['accent_soft_hover']};
    color: {COLORS['accent_hover']};
    padding: 9px 14px 7px 14px;
}}

#option_btn_other:disabled {{
    color: {COLORS['text_tertiary']};
    border-color: {COLORS['border_light']};
    background-color: transparent;
}}

/* 澄清阶段的「跳过」：浅红底 + 红色描边，与普通选项明显区分 */
#option_btn_skip {{
    background-color: {COLORS['error_soft']};
    border: 1px solid {COLORS['error_border']};
    border-radius: 10px;
    color: {COLORS['error']};
    font-size: 12.5px;
    padding: 8px 14px;
    text-align: left;
}}

#option_btn_skip:hover {{
    background-color: {COLORS['error_soft_hover']};
    border-color: {COLORS['error_border_hover']};
    color: {COLORS['error_hover']};
}}

#option_btn_skip:pressed {{
    background-color: {COLORS['error_soft_pressed']};
    border-color: {COLORS['error_border_pressed']};
    color: {COLORS['error_pressed']};
    padding: 9px 14px 7px 14px;
}}

#option_btn_skip:disabled {{
    background-color: {COLORS['error_soft_disabled']};
    border-color: {COLORS['error_border_disabled']};
    color: {COLORS['error_text_disabled']};
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
    background-color: {COLORS['bg_card_hover']};
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
    background: transparent;
}}

#settings_card {{
    background-color: {COLORS['bg_main']};
    border: 1px solid {COLORS['border']};
    border-radius: {RADIUS['lg']};
}}

#settings_title {{
    font-size: 15px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    background: transparent;
}}

#settings_close {{
    background: transparent;
    border: none;
    border-radius: {RADIUS['sm']};
    color: {COLORS['text_tertiary']};
    font-size: 14px;
}}

#settings_close:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

#settings_close:pressed {{
    background-color: {COLORS['bg_pressed']};
    color: {COLORS['text_primary']};
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
    background-color: {COLORS['bg_subtle']};
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

QLineEdit:hover {{
    border-color: {COLORS['border_hover']};
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

QSpinBox:hover {{
    border-color: {COLORS['border_hover']};
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

#save_btn:pressed {{
    background-color: {COLORS['accent_pressed']};
    padding: 10px 26px 8px 26px;
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
    border-color: {COLORS['border_hover']};
}}

#cancel_btn:pressed {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
    padding: 10px 26px 8px 26px;
}}
"""

# ---------------------------------------------------------------- 内嵌文献地图
MAP_QSS = f"""
#map_panel {{
    background-color: {COLORS['bg_main']};
}}

#map_header {{
    background-color: {COLORS['bg_titlebar']};
    border-bottom: 1px solid {COLORS['border']};
}}

#map_dot {{
    color: {COLORS['accent']};
    font-size: 13px;
}}

#map_title {{
    color: {COLORS['text_primary']};
    font-size: 13px;
    font-weight: 600;
}}

#map_hint {{
    background-color: {COLORS['accent_soft']};
    color: {COLORS['accent_pressed']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 10px 16px;
    font-size: 12px;
}}

#map_action {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border_strong']};
    border-radius: 7px;
    padding: 4px 10px;
    font-size: 12px;
}}

#map_action:hover {{
    background-color: {COLORS['accent_soft']};
    color: {COLORS['accent_hover']};
    border-color: {COLORS['accent']};
}}

#map_action:pressed {{
    background-color: {COLORS['accent_soft_hover']};
    color: {COLORS['accent_pressed']};
}}

#map_close {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border_strong']};
    border-radius: 7px;
    padding: 4px 10px;
    font-size: 12px;
}}

#map_close:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
    border-color: {COLORS['border_hover']};
}}

#map_close:pressed {{
    background-color: {COLORS['bg_pressed']};
}}

#map_body {{
    background-color: {COLORS['bg_main']};
}}

#map_fallback {{
    color: {COLORS['text_secondary']};
    font-size: 13px;
    padding: 28px;
}}
"""

# ---------------------------------------------------------------- 轻提示
#
# 破坏性操作的二次确认已改为 ConfirmDialog 弹窗（见下方 CONFIRM_DIALOG_QSS），
# 这里只保留不拦截操作、自动消失的轻提示。

CONFIRM_QSS = f"""
#app_toast {{
    background-color: rgba(43, 42, 38, 0.94);
    color: {COLORS['text_inverse']};
    border-radius: {RADIUS['md']};
    padding: 8px 16px;
    font-size: 12.5px;
}}
"""

# ---------------------------------------------------------------- 确认弹窗
#
# 破坏性操作的二次确认卡片：白底圆角 + 淡边框 + 外投影，按钮五态齐全。
# 删除按钮用 error 色阶梯，和侧栏行内按钮同一套语义色。

CONFIRM_DIALOG_QSS = f"""
#confirm_card,
#confirm_card * {{
    font-family: {FONT_FAMILY};
}}

#confirm_card {{
    background-color: {COLORS['bg_main']};
    border: 1px solid {COLORS['border']};
    border-radius: {RADIUS['lg']};
}}

#confirm_icon {{
    background-color: #FBEAE7;
    color: {COLORS['error']};
    border-radius: 11px;
    font-family: {FONT_MONO};
    font-size: 12px;
    font-weight: 700;
}}

#confirm_icon_info {{
    background-color: {COLORS['accent_soft']};
    color: {COLORS['accent_pressed']};
    border-radius: 11px;
    font-family: {FONT_MONO};
    font-size: 12px;
    font-weight: 700;
}}

#confirm_title {{
    color: {COLORS['text_primary']};
    font-size: 14.5px;
    font-weight: 600;
}}

#confirm_message {{
    color: {COLORS['text_secondary']};
    font-size: 13px;
}}

#confirm_cancel,
#confirm_ok,
#confirm_primary {{
    border-radius: {RADIUS['md']};
    font-size: 13px;
    font-weight: 600;
    padding: 7px 20px;
    min-width: 46px;
}}

#confirm_cancel {{
    background-color: {COLORS['bg_subtle']};
    border: 1px solid {COLORS['border']};
    color: {COLORS['text_secondary']};
}}

#confirm_cancel:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['border_hover']};
    color: {COLORS['text_primary']};
}}

#confirm_cancel:pressed {{
    background-color: {COLORS['bg_pressed']};
    border-color: {COLORS['border_strong']};
}}

#confirm_ok {{
    background-color: {COLORS['error']};
    border: 1px solid {COLORS['error']};
    color: {COLORS['text_inverse']};
}}

#confirm_ok:hover {{
    background-color: {COLORS['error_hover']};
    border-color: {COLORS['error_hover']};
}}

#confirm_ok:pressed {{
    background-color: {COLORS['error_pressed']};
    border-color: {COLORS['error_pressed']};
    padding-top: 8px;
    padding-bottom: 6px;
}}

#confirm_primary {{
    background-color: {COLORS['accent']};
    border: 1px solid {COLORS['accent']};
    color: {COLORS['text_inverse']};
}}

#confirm_primary:hover {{
    background-color: {COLORS['accent_hover']};
    border-color: {COLORS['accent_hover']};
}}

#confirm_primary:pressed {{
    background-color: {COLORS['accent_pressed']};
    border-color: {COLORS['accent_pressed']};
    padding-top: 8px;
    padding-bottom: 6px;
}}
"""
