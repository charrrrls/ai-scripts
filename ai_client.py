#!/usr/bin/env python3
"""
统一AI API调用模块 - by 阮阮
封装所有AI API调用逻辑，提供统一接口
"""

import time
import json
import requests
from typing import Optional, Dict, Any, List, Iterator, Callable
from ai_config import get_config, AIConfig, Environment
from color_utils import print_error, print_success, print_warning, print_progress, print_debug, colored_print, MessageType


class AIClientError(Exception):
    """AI客户端异常"""
    pass


class AIClient:
    """统一AI API调用客户端"""
    
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or get_config()
        self._session = requests.Session()
        self._setup_session()
    
    def _setup_session(self) -> None:
        """设置会话"""
        self._session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": "AI-Helper/1.0"
        })
    
    def _build_request_data(self,
                           prompt: str,
                           max_tokens: Optional[int] = None,
                           temperature: Optional[float] = None,
                           model_name: Optional[str] = None,
                           image_base64: Optional[str] = None,
                           **kwargs) -> Dict[str, Any]:
        """构建请求数据，支持视觉输入"""
        
        # 构建消息内容
        if image_base64:
            # 视觉模型请求格式
            message_content = [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    }
                }
            ]
        else:
            # 纯文本请求
            message_content = prompt
        
        data = {
            "model": model_name or self.config.model_name,
            "messages": [{"role": "user", "content": message_content}],
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": kwargs.get("stream", self.config.stream)  # 优先使用传入的stream参数
        }

        # 添加额外参数（排除已处理的参数）
        extra_kwargs = {k: v for k, v in kwargs.items() if k not in ["stream", "model_name", "image_base64"]}
        data.update(extra_kwargs)
        
        return data
    
    def _make_request(self, data: Dict[str, Any], attempt: int = 1) -> requests.Response:
        """发送API请求"""
        if self.config.debug:
            print_debug(f"API请求 (尝试 {attempt}/{self.config.max_retries})")
            print_debug(f"模型: {data['model']}")
            print_debug(f"温度: {data['temperature']}")
            print_debug(f"最大tokens: {data['max_tokens']}")
        
        response = self._session.post(
            self.config.api_url,
            json=data,
            timeout=self.config.timeout
        )
        
        return response
    
    def _parse_response(self, response: requests.Response) -> str:
        """解析API响应"""
        if response.status_code != 200:
            error_msg = f"API调用失败，状态码: {response.status_code}"
            if response.text:
                error_msg += f", 错误信息: {response.text}"
            raise AIClientError(error_msg)
        
        try:
            result = response.json()
        except ValueError as e:
            raise AIClientError(f"响应JSON解析失败: {e}")
        
        if 'choices' not in result or len(result['choices']) == 0:
            raise AIClientError("API响应格式错误：缺少choices字段")
        
        choice = result['choices'][0]
        if 'message' not in choice or 'content' not in choice['message']:
            raise AIClientError("API响应格式错误：缺少message.content字段")
        
        return choice['message']['content']

    def _parse_stream_response(self, response: requests.Response) -> Iterator[str]:
        """解析流式API响应"""
        if response.status_code != 200:
            error_msg = f"API调用失败，状态码: {response.status_code}"
            if response.text:
                error_msg += f", 错误信息: {response.text}"
            raise AIClientError(error_msg)

        try:
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 移除 'data: ' 前缀

                        if data_str.strip() == '[DONE]':
                            break

                        try:
                            chunk_data = json.loads(data_str)
                            if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                choice = chunk_data['choices'][0]
                                if 'delta' in choice and 'content' in choice['delta']:
                                    content = choice['delta']['content']
                                    if content:  # 过滤空内容
                                        yield content
                        except json.JSONDecodeError:
                            continue  # 跳过无效的JSON行

        except Exception as e:
            raise AIClientError(f"流式响应解析失败: {e}")

    def _call_with_retry(self,
                        prompt: str,
                        max_tokens: Optional[int] = None,
                        temperature: Optional[float] = None,
                        stream: Optional[bool] = None,
                        **kwargs) -> str:
        """带重试机制的API调用"""
        # 如果没有指定stream，使用配置中的默认值
        if stream is None:
            stream = self.config.stream

        data = self._build_request_data(prompt, max_tokens, temperature, stream=stream, **kwargs)
        
        last_error = None
        
        for attempt in range(1, self.config.max_retries + 1):
            try:
                if attempt > 1:
                    print_progress(f"正在重试API调用... (尝试 {attempt}/{self.config.max_retries})")
                
                response = self._make_request(data, attempt)

                if data.get("stream", False):
                    # 流式模式：收集所有内容
                    full_content = ""
                    for chunk in self._parse_stream_response(response):
                        full_content += chunk
                    content = full_content
                else:
                    # 批量模式：解析完整响应
                    content = self._parse_response(response)

                if self.config.debug:
                    print_success("API调用成功")

                return content
                
            except requests.exceptions.Timeout:
                last_error = f"API调用超时 (尝试 {attempt})"
                if self.config.debug:
                    print_warning(last_error)
                    
            except requests.exceptions.RequestException as e:
                last_error = f"网络错误: {e} (尝试 {attempt})"
                if self.config.debug:
                    print_warning(last_error)
                    
            except AIClientError as e:
                last_error = f"API错误: {e} (尝试 {attempt})"
                if self.config.debug:
                    print_warning(last_error)
                    
            except Exception as e:
                last_error = f"未知错误: {e} (尝试 {attempt})"
                if self.config.debug:
                    print_warning(last_error)
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.config.max_retries:
                wait_time = self.config.retry_delay * (2 ** (attempt - 1))  # 指数退避
                if self.config.debug:
                    print_debug(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        # 所有重试都失败
        error_msg = f"所有API调用尝试都失败了。最后错误: {last_error}"
        print_error(error_msg)
        raise AIClientError(error_msg)
    
    def chat(self,
             prompt: str,
             max_tokens: Optional[int] = None,
             temperature: Optional[float] = None,
             stream: Optional[bool] = None,
             **kwargs) -> str:
        """通用对话接口"""
        return self._call_with_retry(prompt, max_tokens, temperature, stream, **kwargs)

    def chat_stream(self,
                   prompt: str,
                   max_tokens: Optional[int] = None,
                   temperature: Optional[float] = None,
                   on_chunk: Optional[Callable[[str], None]] = None,
                   **kwargs) -> str:
        """流式对话接口，支持实时回调"""
        data = self._build_request_data(prompt, max_tokens, temperature, stream=True, **kwargs)

        try:
            response = self._make_request(data, 1)
            full_content = ""

            for chunk in self._parse_stream_response(response):
                full_content += chunk
                if on_chunk:
                    on_chunk(chunk)

            return full_content

        except Exception as e:
            if self.config.debug:
                print_error(f"流式对话失败: {e}")
            raise AIClientError(f"流式对话失败: {e}")
    
    def generate(self, 
                prompt: str,
                max_tokens: Optional[int] = None,
                temperature: Optional[float] = None,
                **kwargs) -> str:
        """内容生成接口"""
        return self._call_with_retry(prompt, max_tokens, temperature, **kwargs)
    
    def complete(self, 
                prompt: str,
                max_tokens: Optional[int] = None,
                temperature: Optional[float] = None,
                **kwargs) -> str:
        """文本补全接口"""
        return self._call_with_retry(prompt, max_tokens, temperature, **kwargs)
    
    def generate_commit_message(self, changes_summary: str) -> str:
        """生成commit信息的专用接口"""
        prompt = f"""请根据以下文件更改信息，生成一个简洁、专业的Git commit信息。

文件更改摘要：{changes_summary}

要求：
1. 使用中文
2. 简洁明了，20-50字
3. 描述具体做了什么改动
4. 符合Git commit最佳实践
5. 不要包含"更新"、"修改"等通用词汇，要具体描述改动内容
6. 只返回commit信息本身，不要有任何解释

示例格式：
- 新增文章：深度学习在图像识别中的应用
- 优化主题配置和CSS样式
- 修复导航栏在移动端的显示问题
- 更新关于页面内容和联系方式

请直接返回一个commit信息："""
        
        return self.chat(prompt, max_tokens=100, temperature=0.3)
    
    def generate_blog_article(self, title: str, user_config: str = "") -> str:
        """生成博客文章的专用接口"""
        from datetime import datetime
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        prompt = f"""{user_config or "你是一个专业的技术博客写作助手。"}

请为标题"{title}"创建一个完整的技术博客文章结构。

要求：
1. 生成完整的Markdown格式文章
2. 包含Front Matter（title, date, tags, categories, description）
3. 文章结构清晰，包含引言、主要内容、实践应用、总结等部分
4. 内容专业且实用，适合技术博客
5. 标签2-3个，与技术内容相关
6. 分类1个，技术领域分类
7. 大纲不超过5点，每点15字以内，使用h2格式
8. 可以在每个大纲下生成必要的子要点，每个大纲下不超过三个h3格式
9. 描述简洁，突出核心价值

当前时间：{current_time}

请直接输出完整的Markdown内容，不要有任何解释性文字。"""
        
        return self.generate(prompt, max_tokens=2500, temperature=0.7)

    def chat_with_scenario(self,
                          prompt: str,
                          scenario: str = "chat",
                          on_chunk: Optional[Callable[[str], None]] = None,
                          image_base64: Optional[str] = None) -> str:
        """根据场景配置进行对话，支持视觉输入"""
        scenario_config = self.config.get_scenario_config(scenario)

        max_tokens = scenario_config.get("max_tokens", self.config.max_tokens)
        temperature = scenario_config.get("temperature", self.config.temperature)
        stream = scenario_config.get("stream", self.config.stream)
        
        # 如果是视觉场景，使用指定的视觉模型
        model_name = scenario_config.get("model_name", self.config.model_name)

        if stream and on_chunk:
            # 流式模式，使用回调
            return self.chat_stream(prompt, max_tokens, temperature, on_chunk, 
                                  model_name=model_name, image_base64=image_base64)
        else:
            # 批量模式或无回调
            return self.chat(prompt, max_tokens, temperature, stream, 
                           model_name=model_name, image_base64=image_base64)

    def check_connection(self) -> bool:
        """检查API连接"""
        try:
            # 发送简单的测试请求
            response = self.chat("测试连接", max_tokens=10, temperature=0.1)
            return bool(response and response.strip())
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": self.config.model_name,
            "provider": self.config.provider,
            "api_url": self.config.api_url,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "timeout": self.config.timeout,
            "max_retries": self.config.max_retries
        }


# 全局客户端实例
_global_client: Optional[AIClient] = None


def get_client(config: Optional[AIConfig] = None) -> AIClient:
    """获取全局客户端实例"""
    global _global_client
    if _global_client is None:
        _global_client = AIClient(config)
    return _global_client


def set_client(client: AIClient) -> None:
    """设置全局客户端实例"""
    global _global_client
    _global_client = client


# 便捷函数
def chat(prompt: str, **kwargs) -> str:
    """便捷对话函数"""
    return get_client().chat(prompt, **kwargs)


def generate(prompt: str, **kwargs) -> str:
    """便捷生成函数"""
    return get_client().generate(prompt, **kwargs)


def generate_commit_message(changes_summary: str) -> str:
    """便捷commit信息生成函数"""
    return get_client().generate_commit_message(changes_summary)


def generate_blog_article(title: str, user_config: str = "") -> str:
    """便捷博客文章生成函数"""
    return get_client().generate_blog_article(title, user_config)


if __name__ == "__main__":
    # 测试AI客户端
    from ai_config import set_environment, Environment

    print("测试AI客户端...")

    # 设置测试环境
    set_environment(Environment.TESTING)

    try:
        client = get_client()

        # 测试连接
        print("检查连接...")
        if client.check_connection():
            print("✅ 连接正常")
        else:
            print("❌ 连接失败")

        # 测试对话
        print("测试对话...")
        response = client.chat("你好，请简单介绍一下你自己", max_tokens=100)
        print(f"AI回复: {response}")

        # 显示模型信息
        print("\n模型信息:")
        info = client.get_model_info()
        for key, value in info.items():
            print(f"  {key}: {value}")

        print("✅ AI客户端测试成功")
    except Exception as e:
        print(f"❌ AI客户端测试失败: {e}")
