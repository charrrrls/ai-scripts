#!/usr/bin/env python3
"""
AI配置管理模块 - by 阮阮
统一管理所有AI相关配置，支持多环境配置
"""

import os
import json
from typing import Dict, Any, Optional
from enum import Enum


class Environment(Enum):
    """环境类型枚举"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class AIProvider(Enum):
    """AI服务提供商枚举"""
    SILICONFLOW = "siliconflow"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"
    DASHSCOPE = "dashscope"


class AIConfig:
    """AI配置管理类"""
    
    def __init__(self, env: Environment = Environment.PRODUCTION):
        self.env = env
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        # 基础配置
        base_config = {
            "provider": AIProvider.SILICONFLOW.value,
            "api_key": "sk-luicbwpmghinywzxkumosqyvurpohzgycdmumowkhlwleuwp",
            "api_url": "https://api.siliconflow.cn/v1/chat/completions",
            "model_name": "THUDM/GLM-4-32B-0414",
            "timeout": 60,
            "max_retries": 3,
            "retry_delay": 2,  # 秒
            "max_tokens": 4096,
            "temperature": 0.7,
            "stream": False,  # 默认批量模式

            # 流式模式配置
            "enable_streaming": True,  # 是否支持流式模式
            "stream_chunk_size": 1,    # 流式输出块大小
            "stream_delay": 0.005,      # 流式输出延迟（秒）
            "show_thinking": True,     # 是否显示思考状态

            # 场景特定配置
            "scenarios": {
                "chat": {
                    "stream": True,      # 对话使用流式模式
                    "temperature": 0.8,  # 对话更有创造性
                    "show_thinking": True
                },
                "commit": {
                    "stream": False,     # commit信息使用批量模式
                    "temperature": 0.3,  # commit信息更稳定
                    "max_tokens": 100,
                    "show_thinking": False
                },
                "blog": {
                    "stream": False,     # 博客生成使用批量模式
                    "temperature": 0.7,
                    "max_tokens": 3000,
                    "show_thinking": False
                },
                "qwen": {
                    "stream": True,      # 千问支持流式
                    "temperature": 0.7,
                    "max_tokens": 4096,
                    "show_thinking": False
                },
                "vector_query": {
                    "stream": False,     # 向量查询使用批量模式
                    "temperature": 0.5,  # 查询更精确
                    "max_tokens": 2000,
                    "show_thinking": False
                },
                "vision": {
                    "stream": True,      # 视觉分析使用流式模式
                    "temperature": 0.7,  # 视觉描述需要一定创造性
                    "max_tokens": 2000,
                    "model_name": "Qwen/Qwen2.5-VL-72B-Instruct",  # 视觉模型
                    "show_thinking": False
                }
            },
            
            # 千问配置
            "qwen_config": {
                "api_key": "",  # 需要配置
                "api_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                "model_name": "qwen-turbo",
                "workspace_id": ""  # 可选
            },
            
            # 向量库配置
            "vector_config": {
                "enabled": True,
                "db_path": "./vector_db",
                "embedding_model": "text-embedding-v1",
                "chunk_size": 1000,
                "chunk_overlap": 100,
                "similarity_threshold": 0.7
            }
        }
        
        # 环境特定配置
        env_configs = {
            Environment.DEVELOPMENT: {
                "timeout": 30,
                "max_retries": 2,
                "temperature": 0.8,
                "debug": True
            },
            Environment.PRODUCTION: {
                "timeout": 60,
                "max_retries": 3,
                "temperature": 0.7,
                "debug": False
            },
            Environment.TESTING: {
                "timeout": 15,
                "max_retries": 1,
                "temperature": 0.5,
                "debug": True,
                "model_name": "THUDM/GLM-4-9B-Chat"  # 测试用较小模型
            }
        }
        
        # 合并配置
        config = base_config.copy()
        if self.env in env_configs:
            config.update(env_configs[self.env])
        
        # 从环境变量覆盖配置
        self._load_from_env(config)
        
        # 从配置文件覆盖配置
        self._load_from_file(config)
        
        return config
    
    def _load_from_env(self, config: Dict[str, Any]) -> None:
        """从环境变量加载配置"""
        env_mappings = {
            "AI_API_KEY": "api_key",
            "AI_API_URL": "api_url", 
            "AI_MODEL_NAME": "model_name",
            "AI_TIMEOUT": "timeout",
            "AI_MAX_RETRIES": "max_retries",
            "AI_TEMPERATURE": "temperature"
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                # 类型转换
                if config_key in ["timeout", "max_retries"]:
                    config[config_key] = int(value)
                elif config_key in ["temperature"]:
                    config[config_key] = float(value)
                else:
                    config[config_key] = value
    
    def _load_from_file(self, config: Dict[str, Any]) -> None:
        """从配置文件加载配置"""
        config_file = f"ai_config_{self.env.value}.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                config.update(file_config)
            except Exception:
                pass  # 忽略配置文件错误
    
    @property
    def api_key(self) -> str:
        """API密钥"""
        return self._config["api_key"]
    
    @property
    def api_url(self) -> str:
        """API URL"""
        return self._config["api_url"]
    
    @property
    def model_name(self) -> str:
        """模型名称"""
        return self._config["model_name"]
    
    @property
    def timeout(self) -> int:
        """超时时间（秒）"""
        return self._config["timeout"]
    
    @property
    def max_retries(self) -> int:
        """最大重试次数"""
        return self._config["max_retries"]
    
    @property
    def retry_delay(self) -> int:
        """重试延迟（秒）"""
        return self._config["retry_delay"]
    
    @property
    def max_tokens(self) -> int:
        """最大token数"""
        return self._config["max_tokens"]
    
    @property
    def temperature(self) -> float:
        """温度参数"""
        return self._config["temperature"]
    
    @property
    def stream(self) -> bool:
        """是否流式输出"""
        return self._config["stream"]
    
    @property
    def debug(self) -> bool:
        """是否调试模式"""
        return self._config.get("debug", False)
    
    @property
    def provider(self) -> str:
        """服务提供商"""
        return self._config["provider"]
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self._config.get(key, default)
    
    def update(self, **kwargs) -> None:
        """更新配置"""
        self._config.update(kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self._config.copy()

    def get_scenario_config(self, scenario: str) -> Dict[str, Any]:
        """获取特定场景的配置"""
        scenarios = self._config.get("scenarios", {})
        scenario_config = scenarios.get(scenario, {})

        # 合并基础配置和场景配置
        merged_config = self._config.copy()
        merged_config.update(scenario_config)

        return merged_config

    def is_streaming_enabled(self) -> bool:
        """检查是否启用流式模式"""
        return self._config.get("enable_streaming", False)

    def should_show_thinking(self, scenario: str = None) -> bool:
        """检查是否应该显示思考状态"""
        if scenario:
            scenario_config = self.get_scenario_config(scenario)
            return scenario_config.get("show_thinking", False)
        return self._config.get("show_thinking", False)

    @property
    def stream_delay(self) -> float:
        """流式输出延迟"""
        return self._config.get("stream_delay", 0.02)

    @property
    def stream_chunk_size(self) -> int:
        """流式输出块大小"""
        return self._config.get("stream_chunk_size", 1)


# 全局配置实例
_global_config: Optional[AIConfig] = None


def get_config(env: Environment = Environment.PRODUCTION) -> AIConfig:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None or _global_config.env != env:
        _global_config = AIConfig(env)
    return _global_config


def set_environment(env: Environment) -> None:
    """设置环境"""
    global _global_config
    _global_config = AIConfig(env)


# 便捷函数
def get_api_key() -> str:
    """获取API密钥"""
    return get_config().api_key


def get_model_name() -> str:
    """获取模型名称"""
    return get_config().model_name


def get_api_url() -> str:
    """获取API URL"""
    return get_config().api_url


if __name__ == "__main__":
    # 测试配置
    config = get_config()
    print("AI配置信息:")
    print(f"环境: {config.env.value}")
    print(f"提供商: {config.provider}")
    print(f"模型: {config.model_name}")
    print(f"API URL: {config.api_url}")
    print(f"超时: {config.timeout}秒")
    print(f"重试: {config.max_retries}次")
    print(f"调试: {config.debug}")
