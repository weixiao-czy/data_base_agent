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
        
        # 返回完整的提示词，包含用户输入
        prompt = f"""{template}

---

现在请根据以上模板和规则，处理以下用户输入：

用户输入："{user_input}"

请输出复述和选项："""
        
        return prompt
    
    def build_probe_prompt(self, interpretation: str, history: str, 
                          current_round: int, max_rounds: int) -> str:
        """构建追问提示词"""
        template = self.templates.get("probe", "")
        remaining = max_rounds - current_round
        
        prompt = f"""{template}

---

现在请根据以上模板和规则，针对以下情况生成追问：

当前理解：{interpretation}
当前轮次：第 {current_round} 轮
剩余机会：{remaining} 轮

对话历史：
{history}

请输出追问问题："""
        
        return prompt
    
    def build_plan_card_prompt(self, history: str, user_input: str, 
                              interpretation: str, rounds: int) -> str:
        """构建需求翻译卡生成提示词"""
        template = self.templates.get("plan_card", "")
        
        prompt = f"""{template}

---

现在请根据以上模板和规则，生成需求翻译卡：

用户原始输入：{user_input}
确认的研究方向：{interpretation}
对话轮次：{rounds} 轮

对话历史：
{history}

请输出 YAML 格式的需求翻译卡："""
        
        return prompt
