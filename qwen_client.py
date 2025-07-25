#!/usr/bin/env python3
"""
千问API客户端模块 - by 阮阮  
专门处理千问(Qwen)模型的API调用
"""

import json
import requests
from typing import Optional, Dict, Any, Iterator
from ai_config import get_config
from color_utils import print_error, print_success, print_warning, print_progress, print_debug


class QwenClient:
    """千问API客户端"""
    
    def __init__(self, api_key: str = None):
        self.config = get_config()
        qwen_config = self.config.get("qwen_config", {})
        
        self.api_key = api_key or qwen_config.get("api_key", "")
        self.api_url = qwen_config.get("api_url", "")
        self.model_name = qwen_config.get("model_name", "qwen-turbo")
        self.workspace_id = qwen_config.get("workspace_id", "")
        
        if not self.api_key:
            raise ValueError("千问API密钥未配置，请设置api_key")
        
        self._session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置会话headers"""
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable"  # 启用SSE流式响应
        })
        
        if self.workspace_id:
            self._session.headers["X-DashScope-WorkSpace"] = self.workspace_id
    
    def _build_request_data(self,
                           prompt: str,
                           max_tokens: int = 4096,
                           temperature: float = 0.7,
                           stream: bool = False,
                           **kwargs) -> Dict[str, Any]:
        """构建千问API请求数据"""
        data = {
            "model": self.model_name,
            "input": {
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "incremental_output": stream,  # 千问的流式参数
                **kwargs
            }
        }
        
        return data
    
    def _make_request(self, data: Dict[str, Any]) -> requests.Response:
        """发送千问API请求"""
        if self.config.debug:
            print_debug(f"千问API请求: {self.model_name}")
            print_debug(f"温度: {data['parameters']['temperature']}")
            print_debug(f"最大tokens: {data['parameters']['max_tokens']}")
        
        response = self._session.post(
            self.api_url,
            json=data,
            timeout=self.config.timeout,
            stream=data['parameters'].get('incremental_output', False)
        )
        
        return response
    
    def _parse_response(self, response: requests.Response) -> str:
        """解析千问API响应"""
        if response.status_code != 200:
            error_msg = f"千问API调用失败，状态码: {response.status_code}"
            if response.text:
                error_msg += f", 错误信息: {response.text}"
            raise Exception(error_msg)
        
        try:
            result = response.json()
        except ValueError as e:
            raise Exception(f"响应JSON解析失败: {e}")
        
        # 千问API响应格式
        if 'output' not in result:
            raise Exception("千问API响应格式错误：缺少output字段")
        
        output = result['output']
        if 'text' not in output:
            raise Exception("千问API响应格式错误：缺少output.text字段")
        
        return output['text']
    
    def _parse_stream_response(self, response: requests.Response) -> Iterator[str]:
        """解析千问流式API响应"""
        if response.status_code != 200:
            error_msg = f"千问API调用失败，状态码: {response.status_code}"
            if response.text:
                error_msg += f", 错误信息: {response.text}"
            raise Exception(error_msg)
        
        try:
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data:'):
                        data_str = line_str[5:].strip()  # 移除 'data:' 前缀
                        
                        if data_str == '[DONE]':
                            break
                        
                        try:
                            chunk_data = json.loads(data_str)
                            if 'output' in chunk_data and 'text' in chunk_data['output']:
                                content = chunk_data['output']['text']
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue  # 跳过无效的JSON行
                            
        except Exception as e:
            raise Exception(f"千问流式响应解析失败: {e}")
    
    def chat(self,
             prompt: str,
             max_tokens: int = 4096,
             temperature: float = 0.7,
             stream: bool = False,
             **kwargs) -> str:
        """千问对话接口"""
        try:
            print_progress("正在调用千问API...")
            
            data = self._build_request_data(prompt, max_tokens, temperature, stream, **kwargs)
            response = self._make_request(data)
            
            if stream:
                # 流式模式：收集所有内容
                full_content = ""
                for chunk in self._parse_stream_response(response):
                    full_content += chunk
                content = full_content
            else:
                # 批量模式：解析完整响应
                content = self._parse_response(response)
            
            print_success("千问API调用成功")
            return content
            
        except Exception as e:
            print_error(f"千问API调用失败: {e}")
            raise
    
    def chat_stream(self,
                   prompt: str,
                   max_tokens: int = 4096,
                   temperature: float = 0.7,
                   on_chunk=None,
                   **kwargs) -> str:
        """千问流式对话接口"""
        try:
            print_progress("正在调用千问流式API...")
            
            data = self._build_request_data(prompt, max_tokens, temperature, True, **kwargs)
            response = self._make_request(data)
            
            full_content = ""
            for chunk in self._parse_stream_response(response):
                full_content += chunk
                if on_chunk:
                    on_chunk(chunk)
            
            print_success("千问流式API调用成功")
            return full_content
            
        except Exception as e:
            print_error(f"千问流式API调用失败: {e}")
            raise
    
    def generate_with_context(self,
                             prompt: str,
                             context_docs: list,
                             max_tokens: int = 4096,
                             temperature: float = 0.7) -> str:
        """结合上下文文档生成回答"""
        # 构建包含上下文的提示词
        context_text = "\n\n".join([f"文档{i+1}: {doc.title}\n{doc.content}" 
                                   for i, doc in enumerate(context_docs)])
        
        enhanced_prompt = f"""基于以下上下文文档回答问题：

上下文文档：
{context_text}

问题：{prompt}

请基于上述文档内容回答问题，如果文档中没有相关信息，请说明。"""
        
        return self.chat(enhanced_prompt, max_tokens, temperature)
    
    def check_connection(self) -> bool:
        """检查千问API连接"""
        try:
            response = self.chat("你好", max_tokens=10, temperature=0.1)
            return bool(response and response.strip())
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取千问模型信息"""
        return {
            "model_name": self.model_name,
            "provider": "qwen",
            "api_url": self.api_url,
            "workspace_id": self.workspace_id
        }


# 全局千问客户端实例
_global_qwen_client: Optional[QwenClient] = None


def get_qwen_client(api_key: str = None) -> QwenClient:
    """获取全局千问客户端实例"""
    global _global_qwen_client
    if _global_qwen_client is None:
        _global_qwen_client = QwenClient(api_key)
    return _global_qwen_client


def set_qwen_client(client: QwenClient) -> None:
    """设置全局千问客户端实例"""
    global _global_qwen_client
    _global_qwen_client = client


if __name__ == "__main__":
    # 测试千问客户端
    print("测试千问客户端...")
    
    try:
        # 注意：需要配置千问API密钥才能测试
        client = QwenClient("your-qwen-api-key-here")
        
        # 测试连接
        print("检查连接...")
        if client.check_connection():
            print("✅ 千问连接正常")
        else:
            print("❌ 千问连接失败")
        
        # 测试对话
        print("测试对话...")
        response = client.chat("请简单介绍一下你自己", max_tokens=100)
        print(f"千问回复: {response}")
        
        # 显示模型信息
        print("\n千问模型信息:")
        info = client.get_model_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print("✅ 千问客户端测试成功")
        
    except Exception as e:
        print(f"❌ 千问客户端测试失败: {e}")
        print("提示：请配置正确的千问API密钥")