"""
提示词管理器：加载和管理提示词模板
"""

import os
from typing import Dict, Any
from pathlib import Path


class PromptManager:
    """提示词管理器"""
    
    def __init__(self, prompts_dir: str = None):
        """
        初始化提示词管理器
        
        Args:
            prompts_dir: 提示词模板目录，默认为 src/prompts
        """
        if prompts_dir is None:
            # 默认使用 src/prompts 目录
            self.prompts_dir = Path(__file__).parent.parent / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载所有提示词模板"""
        if not self.prompts_dir.exists():
            return
        
        for file_path in self.prompts_dir.glob("*.md"):
            template_name = file_path.stem
            with open(file_path, 'r', encoding='utf-8') as f:
                self.templates[template_name] = f.read()
    
    def get_prompt(self, template_name: str, **kwargs) -> str:
        """
        获取格式化后的提示词
        
        Args:
            template_name: 模板名称
            **kwargs: 模板变量
            
        Returns:
            格式化后的提示词
        """
        if template_name not in self.templates:
            raise ValueError(f"提示词模板 '{template_name}' 不存在")
        
        template = self.templates[template_name]
        
        # 简单的变量替换
        for key, value in kwargs.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        return template
    
    def build_restate_prompt(self, user_input: str) -> str:
        """构建复述提示词"""
        template = self.templates.get("restate", "")
        
        prompt = f"""{template}

用户输入：{user_input}

请根据上述规则，复述用户输入并给出 2-3 种可能的解读。"""
        
        return prompt
    
    def build_probe_prompt(self, interpretation: str, history: str) -> str:
        """构建追问提示词"""
        template = self.templates.get("probe", "")
        
        prompt = f"""{template}

当前理解：{interpretation}

对话历史：
{history}

请根据上述规则，提出一个关键分叉问题。"""
        
        return prompt
    
    def build_plan_card_prompt(self, history: str, user_input: str, interpretation: str) -> str:
        """构建需求翻译卡生成提示词"""
        template = self.templates.get("plan_card", "")
        
        prompt = f"""{template}

用户原始输入：{user_input}
确认的研究方向：{interpretation}

对话历史：
{history}

请根据上述规则，生成需求翻译卡。"""
        
        return prompt
