"""
LLM 客户端模块：封装大语言模型调用
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv


def _env_candidates():
    """按优先级列出可能放着 .env 的目录。

    PyInstaller 打包后 sys.frozen 为真，python-dotenv 的 find_dotenv() 此时
    改为从「当前工作目录」向上查找，而不是从 exe 或代码所在位置。双击 exe
    通常把 cwd 设为 exe 目录还能侥幸找到，但经由桌面快捷方式 / 开始菜单启动
    时 cwd 是桌面或 System32，.env 永远找不到 —— 密钥为空，上层再静默降级
    成模拟 LLM，表现就是「看起来完全没调用大模型」。
    这里改为显式枚举候选目录，不依赖调用方的 cwd。
    """
    dirs = []
    if getattr(sys, "frozen", False):
        # 打包后：exe 同级目录，用户最可能把 .env 放在这里
        dirs.append(Path(sys.executable).parent)
        _meipass = getattr(sys, "_MEIPASS", None)
        if _meipass:
            dirs.append(Path(_meipass))
    # 源码运行：从本文件逐级向上，能覆盖项目根
    dirs.extend(Path(__file__).resolve().parents)
    # 最后兜底再试工作目录
    dirs.append(Path.cwd())
    dirs.extend(Path.cwd().parents)
    return dirs


def _load_env() -> Optional[str]:
    """逐个候选目录找 .env，返回实际加载的文件路径（找不到返回 None）"""
    seen = set()
    for d in _env_candidates():
        try:
            d = d.resolve()
        except OSError:
            continue
        if d in seen:
            continue
        seen.add(d)
        f = d / ".env"
        try:
            if f.is_file():
                load_dotenv(f, override=False)
                return str(f)
        except OSError:
            continue
    return None


# 实际加载到的 .env 路径，供 GUI 诊断显示
ENV_FILE = _load_env()


class LLMClient(ABC):
    """LLM 客户端抽象基类"""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            **kwargs: 其他参数
            
        Returns:
            模型回复文本
        """
        pass


class OpenAIClient(LLMClient):
    """OpenAI API 客户端"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化 OpenAI 客户端
        
        Args:
            api_key: OpenAI API Key，如果不提供则从环境变量 OPENAI_API_KEY 读取
            model: 模型名称，如果不提供则从环境变量 OPENAI_MODEL 读取，默认为 gpt-3.5-turbo
            base_url: API base URL，如果不提供则从环境变量 OPENAI_BASE_URL 读取
        """
        # 注意用 `is None` 判断：显式传空字符串代表「我就是要用空的」，
        # 不能让它退回读环境变量，否则校验永远走不到「未配置」分支
        raw_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.api_key = (raw_key or "").strip()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        
        self._validate_api_key()
        
        try:
            from openai import OpenAI
            # 使用新的 API 接口
            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            # 关键：交大等服务部署在校园网内网地址，
            # 若系统/环境变量里配了代理，openai 库会自动读取并走代理，导致连接超时。
            # 显式传 http_client 并禁用环境代理，可确保直连。
            try:
                import httpx
                client_kwargs["http_client"] = httpx.Client(trust_env=False, timeout=60.0)
            except ImportError:
                pass
            self.client = OpenAI(**client_kwargs)
        except ImportError:
            raise ImportError("请先安装 openai 包：pip install openai")
    
    # 常见占位符：直接复制 .env.example 时残留的值
    _PLACEHOLDER_HINTS = (
        "your-api-key", "your_api_key", "your-key", "yourkey",
        "sk-xxx", "api-key-here", "replace-me", "changeme",
    )
    
    def _validate_api_key(self) -> None:
        """提前校验 API Key，避免拿着占位符去请求、最后只拿到一个 401
        
        原始实现只判断「是否为空」，而 .env.example 里的 your-api-key-here
        是非空字符串，会一路走到服务端才报 401：
            LiteLLM Virtual Key expected. Received=your****here
        这个错误对使用者几乎没有指向性，所以在本地就拦下来。
        """
        key = self.api_key
        
        if not key:
            raise ValueError(
                "未配置 API Key。\n"
                "  请复制 .env.example 为 .env，并把 OPENAI_API_KEY 填成真实密钥。\n"
                "  上海交大师生可在 https://models.sjtu.edu.cn 申请（密钥以 sk- 开头）。"
            )
        
        lowered = key.lower()
        if any(h in lowered for h in self._PLACEHOLDER_HINTS):
            raise ValueError(
                f"OPENAI_API_KEY 仍是示例占位符（当前值：{self._masked_key()}）。\n"
                "  请把它替换为真实密钥，密钥以 sk- 开头。\n"
                "  上海交大师生可在 https://models.sjtu.edu.cn 申请。"
            )
        
        # OpenAI 兼容服务的密钥通常以 sk- 开头，长度也远大于 20
        if not key.startswith("sk-") and len(key) < 20:
            raise ValueError(
                f"OPENAI_API_KEY 格式可疑（当前值：{self._masked_key()}，长度 {len(key)}）。\n"
                "  OpenAI 兼容服务的密钥通常以 sk- 开头且长度在 20 以上。\n"
                "  服务端会返回 401「LiteLLM Virtual Key expected」。"
            )
    
    def _masked_key(self) -> str:
        """脱敏显示，避免把密钥打到日志里"""
        key = self.api_key
        if len(key) <= 8:
            return key[:2] + "*" * max(0, len(key) - 2)
        return f"{key[:4]}{'*' * 8}{key[-4:]}"
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        调用 OpenAI Chat API
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数（temperature, max_tokens 等）
            
        Returns:
            模型回复
        """
        try:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs
                )
            except Exception as e:
                # 推理模型（deepseek-reasoner、o1/o3 等）不接受 temperature/top_p 等
                # 采样参数，调用方却普遍会传。这里自动去掉后重试一次，
                # 避免为了兼容某个模型去改所有调用点。
                if self._is_sampling_param_error(e) and any(
                    k in kwargs for k in ("temperature", "top_p", "presence_penalty",
                                          "frequency_penalty")
                ):
                    for k in ("temperature", "top_p", "presence_penalty",
                              "frequency_penalty"):
                        kwargs.pop(k, None)
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        **kwargs
                    )
                else:
                    raise
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API 调用失败: {self._explain_error(e)}")
    
    @staticmethod
    def _is_sampling_param_error(e: Exception) -> bool:
        """判断是否为「不支持采样参数」类错误"""
        text = str(e).lower()
        if not any(k in text for k in ("temperature", "top_p", "sampling")):
            return False
        return "400" in text or "invalid" in text or "unsupported" in text
    
    def _explain_error(self, e: Exception) -> str:
        """把常见的接口错误翻译成可操作的中文提示"""
        text = str(e)
        low = text.lower()
        
        if "401" in text or "auth_error" in text or "invalid_api_key" in text:
            return (
                f"{text}\n"
                "  → 鉴权失败：API Key 无效、过期，或不属于当前 base_url 对应的服务。\n"
                "     请确认 OPENAI_API_KEY 与 {base_url} 是同一平台申请的。"
            ).replace("{base_url}", self.base_url or "OpenAI 官方")
        
        if "timeout" in low or "timed out" in low or "connect" in low:
            return (
                f"{text}\n"
                "  → 连接失败：如果使用的是校园网/内网接口（如 models.sjtu.edu.cn），\n"
                "     请关闭代理，或在 .env 中设置 NO_PROXY=models.sjtu.edu.cn"
            )
        
        if "404" in text or "model" in low and "not found" in low:
            return (
                f"{text}\n"
                f"  → 模型不存在：请检查 OPENAI_MODEL={self.model} 是否为该平台支持的模型名。"
            )
        
        if "400" in text and any(k in low for k in ("temperature", "top_p", "reasoning")):
            return (
                f"{text}\n"
                f"  → 参数不被支持：{self.model} 可能是推理模型，"
                "不接受 temperature / top_p 等采样参数。"
            )
        
        return text



class MockLLMClient(LLMClient):
    """模拟 LLM 客户端（用于测试）"""
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """返回模拟回复"""
        last_message = messages[-1]["content"] if messages else ""
        
        # 简单的规则回复
        if "复述" in last_message or "解读" in last_message:
            return "我理解你关注的是这个研究方向。你更接近哪个方向？\n1. 理论研究\n2. 应用实践\n3. 系统实现"
        elif "追问" in last_message or "分叉" in last_message:
            return "你更关心理论分析还是实验验证？\nA. 理论分析\nB. 实验验证\nC. 都关心"
        else:
            return "这是一个很好的研究方向。"
