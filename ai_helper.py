#!/usr/bin/env python3
"""
AI助手核心脚本 - by 阮阮
提供AI调用、对话、博客生成等功能
"""

import os
import time
import threading
import tempfile
import base64
from datetime import datetime
from typing import Optional
import argparse
import re
from PIL import Image, ImageGrab
from rich_utils import (print_error, print_success, print_warning, print_info, print_progress,
                       display_ai_response, display_statistics, create_streaming_callback, rich_output)
from ai_client import get_client, AIClientError
from ai_config import get_config


class AIHelper:
    def __init__(self):
        self.client = get_client()
        self.config = get_config()
        self.config_dir = "/Users/leion/scripts/config"
        self.default_prompt_file = f"{self.config_dir}/default_prompt.txt"
        
    def get_default_prompt(self) -> str:
        """获取默认prompt，优先从配置文件读取"""
        try:
            if os.path.exists(self.default_prompt_file):
                with open(self.default_prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # 跳过注释行
                    lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
                    prompt = '\n'.join(lines).strip()
                    if prompt:
                        return prompt
        except Exception as e:
            print_warning(f"读取默认prompt配置失败: {e}")
        
        # 如果配置文件不存在或读取失败，返回内置默认prompt
        return """请作为一个专业、友好的AI助手回答以下问题。要求：
1. 回答准确、详细但简洁，不要有太多的解释文字
2. 如果是技术问题，提供实用的建议
3. 使用中文回答
4. 保持专业但友好的语调"""

    def _show_spinner(self, message: str = "思考中") -> None:
        """显示加载动画"""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        i = 0
        try:
            while True:
                colored_print(f"\r{message} {chars[i % len(chars)]}", MessageType.PROGRESS, prefix="", end="", flush=True)
                time.sleep(0.1)
                i += 1
        except KeyboardInterrupt:
            colored_print(f"\r{' ' * (len(message) + 2)}\r", MessageType.NORMAL, prefix="", end="")

    def _typewriter_output(self, text: str, delay: float = 0.02) -> None:
        """打字机效果输出"""
        try:
            for char in text:
                colored_print(char, MessageType.NORMAL, prefix="", end="", flush=True)
                if char in "。？！.?!":
                    time.sleep(delay * 3)
                elif char in "，；,;":
                    time.sleep(delay * 2)
                else:
                    time.sleep(delay)
        except KeyboardInterrupt:
            print_warning("\n输出被中断")
            
    def call_ai(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> Optional[str]:
        """调用AI API"""
        try:
            return self.client.chat(prompt, max_tokens=max_tokens, temperature=temperature)
        except AIClientError as e:
            print_error(f"AI调用失败: {e}")
            return None
        except Exception as e:
            print_error(f"未知错误: {e}")
            return None
    
    def chat(self, question: str, use_stream: bool = False, custom_prompt: str = None) -> None:
        """通用AI对话"""
        if not question:
            print_info("Usage: python ai_helper.py chat \"your question\"")
            return

        print_info(f"Question: {question}\n")

        # 使用自定义prompt或默认prompt
        if custom_prompt:
            print_info(f"使用自定义 Prompt: {custom_prompt[:50]}{'...' if len(custom_prompt) > 50 else ''}")
            general_prompt = f"{custom_prompt}\n\n问题：{question}"
        else:
            default_prompt = self.get_default_prompt()
            general_prompt = f"{default_prompt}\n\n问题：{question}"

        # 修改逻辑：如果明确指定use_stream，则强制使用流式输出
        # 否则根据配置决定
        should_use_stream = use_stream if use_stream else (
            self.config.is_streaming_enabled() and 
            self.config.get_scenario_config("chat").get("stream", False)
        )
        
        if should_use_stream:
            self._chat_with_stream(general_prompt)
        else:
            self._chat_without_stream(general_prompt)

    def _chat_without_stream(self, prompt: str) -> None:
        """批量模式对话 - Rich增强版"""
        print_info("GLM-4 正在思考...")
        start_time = time.time()
        
        result = self.call_ai(prompt, 1500, 0.7)
        
        end_time = time.time()
        duration = end_time - start_time

        if result:
            # 使用Rich显示AI回复
            display_ai_response(result, "AI 回复")
            
            # 统计信息
            total_chars = len(result)
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', result))
            english_chars = total_chars - chinese_chars
            total_tokens_estimate = chinese_chars // 2 + english_chars // 4
            
            stats = {
                "chars": total_chars,
                "tokens": total_tokens_estimate,
                "duration": duration
            }
            display_statistics(stats)
        else:
            print_error("获取AI回答失败")

    def _chat_with_stream(self, prompt: str) -> None:
        """流式模式对话 - Rich增强版，并行优化"""
        
        # 统计变量
        api_start_time = None
        first_token_time = None
        total_chars = 0
        total_tokens_estimate = 0
        full_response = ""
        streaming_callback = None
        
        # 共享变量，用于线程间通信
        rich_ready = threading.Event()
        api_ready = threading.Event()
        
        try:
            def init_rich():
                """Rich初始化线程"""
                nonlocal streaming_callback
                streaming_callback = create_streaming_callback("AI 回复")
                rich_ready.set()  # 通知Rich初始化完成
            
            def on_chunk(chunk: str):
                nonlocal total_chars, total_tokens_estimate, full_response, first_token_time
                
                # 记录首个词的响应时间 (TTFT - Time To First Token)
                if first_token_time is None and chunk.strip():
                    first_token_time = time.time()
                
                # 累积完整响应
                full_response += chunk
                
                # 清理chunk，移除ANSI颜色代码进行统计
                clean_chunk = re.sub(r'\x1b\[[0-9;]*m', '', chunk)
                total_chars += len(clean_chunk)
                # 粗略估算token数（中文约2字符=1token，英文约4字符=1token）
                chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_chunk))
                english_chars = len(clean_chunk) - chinese_chars
                total_tokens_estimate += chinese_chars // 2 + english_chars // 4
                
                # 等待Rich初始化完成再显示
                rich_ready.wait()
                streaming_callback(chunk)
                time.sleep(self.config.stream_delay)

            # 并行启动：Rich初始化
            rich_thread = threading.Thread(target=init_rich)
            rich_thread.start()
            
            # 立即发送API请求（不等Rich初始化）
            api_start_time = time.time()
            result = self.client.chat_with_scenario(prompt, "chat", on_chunk)
            
            # 等待Rich线程完成
            rich_thread.join()
            
            # 完成流式输出
            if streaming_callback:
                streaming_callback.finish()
            
            # 计算统计信息
            end_time = time.time()
            duration = end_time - api_start_time if api_start_time else 0
            chars_per_sec = total_chars / duration if duration > 0 else 0
            tokens_per_sec = total_tokens_estimate / duration if duration > 0 else 0
            
            # 计算首词响应时间 (TTFT)
            ttft = (first_token_time - api_start_time) if (first_token_time and api_start_time) else 0
            
            if result:
                # 显示统计信息，包含首词响应时间
                stats = {
                    "chars": total_chars,
                    "tokens": total_tokens_estimate,
                    "speed": chars_per_sec,
                    "token_speed": tokens_per_sec,
                    "ttft": ttft,  # Time To First Token
                    "duration": duration
                }
                display_statistics(stats)
            else:
                print_error("获取AI回答失败")

        except AIClientError as e:
            print_error(f"AI对话失败: {e}")
        except Exception as e:
            print_error(f"未知错误: {e}")
    
    def generate_commit_message(self, changes_summary: str) -> Optional[str]:
        """根据文件更改内容生成commit信息"""
        if not changes_summary:
            return None

        try:
            result = self.client.generate_commit_message(changes_summary)
            if result:
                # 清理返回的内容
                commit_msg = result.strip().replace('\n', ' ').replace('\r', '')
                # 移除可能的引号
                commit_msg = commit_msg.strip('"\'')
                return commit_msg
        except AIClientError as e:
            print_error(f"生成commit信息失败: {e}")
        except Exception as e:
            print_error(f"未知错误: {e}")

        return None

    def generate_blog_article(self, title: str) -> Optional[str]:
        """生成博客文章结构"""
        if not title:
            print_error("错误：缺少文章标题")
            return None

        # 读取Claude配置
        claude_config = "你是一个专业的技术博客写作助手。"
        try:
            with open("/Users/leion/.claude/CLAUDE.md", "r", encoding="utf-8") as f:
                claude_config = f.read()
                print_info("已读取Claude配置文件")
        except FileNotFoundError:
            print_warning("未找到~/.claude/CLAUDE.md配置文件，使用默认配置")
            
        print_progress("正在生成博客文章结构...")
        print_info(f"标题: {title}")
        print_progress("请稍等，GLM-4正在为您创作...")

        try:
            result = self.client.generate_blog_article(title, claude_config)
            if result:
                print_success("AI文章结构生成成功！")
                return result
        except AIClientError as e:
            print_error(f"AI生成失败: {e}")
        except Exception as e:
            print_error(f"未知错误: {e}")

        print_warning("AI生成失败，使用默认模板...")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""---
title: "{title}"
date: {current_time}
tags: [技术分享]
categories: [个人经历]
description: "关于{title}的技术分享"
---

## 简介

## 主要内容

## 实践应用

## 总结
"""

    def get_interactive_input(self) -> str:
        """交互模式获取用户输入"""
        print_info("=== 交互模式 ===")
        print_info("请输入您的问题（支持多行，输入 'END' 结束）:")
        print_info("提示：此模式支持任何特殊字符，包括引号、括号等")
        rich_output.console.print("[dim]" + "-" * 50 + "[/]")

        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
            except KeyboardInterrupt:
                print_warning("\n输入被取消")
                return ""
            except EOFError:
                break

        question = '\n'.join(lines).strip()
        if question:
            rich_output.console.print("[dim]" + "-" * 50 + "[/]")
            print_info(f"您的问题已接收，共 {len(question)} 个字符")

        return question

    def read_prompt_from_file(self, filepath: str) -> str:
        """从文件读取自定义prompt"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if content:
                print_info(f"已从文件 {filepath} 读取 Prompt，共 {len(content)} 个字符")
                return content
            else:
                print_warning(f"Prompt文件 {filepath} 为空")
                return ""

        except FileNotFoundError:
            print_error(f"Prompt文件不存在: {filepath}")
            return ""
        except Exception as e:
            print_error(f"读取Prompt文件失败: {e}")
            return ""

    def read_question_from_file(self, filepath: str) -> str:
        """从文件读取问题"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if content:
                print_info(f"已从文件 {filepath} 读取问题，共 {len(content)} 个字符")
                return content
            else:
                print_warning(f"文件 {filepath} 为空")
                return ""

        except FileNotFoundError:
            print_error(f"文件不存在: {filepath}")
            return ""
        except Exception as e:
            print_error(f"读取文件失败: {e}")
            return ""

    def get_clipboard_image(self) -> Optional[str]:
        """从剪贴板获取图片并转换为base64"""
        try:
            # 尝试从剪贴板获取图片
            clipboard_image = ImageGrab.grabclipboard()
            
            if clipboard_image is None:
                return None
            
            if not isinstance(clipboard_image, Image.Image):
                return None
            
            # 保存到临时文件并转换为base64
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                clipboard_image.save(temp_file.name, 'PNG')
                temp_path = temp_file.name
            
            # 读取并编码为base64
            with open(temp_path, 'rb') as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # 删除临时文件
            os.unlink(temp_path)
            
            return base64_image
            
        except Exception as e:
            print_error(f"获取剪贴板图片失败: {e}")
            return None

    def chat_with_image(self, question: str, custom_prompt: str = None) -> None:
        """带图片的AI对话"""
        if not question:
            print_info("Usage: python ai_helper.py chat --image \"describe this image\"")
            return

        print_info("🖼️ 正在检测剪贴板图片...")
        
        # 获取剪贴板图片
        base64_image = self.get_clipboard_image()
        if not base64_image:
            print_error("剪贴板中没有找到图片！请先截图或复制图片。")
            return
        
        print_success("✅ 已获取剪贴板图片")
        print_info(f"Question: {question}\n")

        # 使用自定义prompt或默认prompt
        if custom_prompt:
            print_info(f"使用自定义 Prompt: {custom_prompt[:50]}{'...' if len(custom_prompt) > 50 else ''}")
            general_prompt = f"{custom_prompt}\n\n问题：{question}"
        else:
            default_prompt = self.get_default_prompt()
            general_prompt = f"{default_prompt}\n\n问题：{question}"

        # 视觉分析使用流式输出
        should_use_stream = (
            self.config.is_streaming_enabled() and 
            self.config.get_scenario_config("vision").get("stream", True)
        )
        
        if should_use_stream:
            self._chat_with_vision_stream(general_prompt, base64_image)
        else:
            self._chat_with_vision_batch(general_prompt, base64_image)
    
    def _chat_with_vision_stream(self, prompt: str, image_base64: str) -> None:
        """流式模式视觉对话 - Rich增强版"""
        
        # 统计变量
        api_start_time = None
        first_token_time = None
        total_chars = 0
        total_tokens_estimate = 0
        full_response = ""
        streaming_callback = None
        
        # 共享变量，用于线程间通信
        rich_ready = threading.Event()
        
        try:
            def init_rich():
                """Rich初始化线程"""
                nonlocal streaming_callback
                streaming_callback = create_streaming_callback("🖼️ 视觉分析")
                rich_ready.set()  # 通知Rich初始化完成
            
            def on_chunk(chunk: str):
                nonlocal total_chars, total_tokens_estimate, full_response, first_token_time
                
                # 记录首个词的响应时间 (TTFT - Time To First Token)
                if first_token_time is None and chunk.strip():
                    first_token_time = time.time()
                
                # 累积完整响应
                full_response += chunk
                
                # 清理chunk，移除ANSI颜色代码进行统计
                clean_chunk = re.sub(r'\x1b\[[0-9;]*m', '', chunk)
                total_chars += len(clean_chunk)
                # 粗略估算token数（中文约2字符=1token，英文约4字符=1token）
                chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_chunk))
                english_chars = len(clean_chunk) - chinese_chars
                total_tokens_estimate += chinese_chars // 2 + english_chars // 4
                
                # 等待Rich初始化完成再显示
                rich_ready.wait()
                streaming_callback(chunk)
                time.sleep(self.config.stream_delay)

            # 并行启动：Rich初始化
            rich_thread = threading.Thread(target=init_rich)
            rich_thread.start()
            
            # 立即发送API请求（不等Rich初始化）
            api_start_time = time.time()
            result = self.client.chat_with_scenario(prompt, "vision", on_chunk, image_base64=image_base64)
            
            # 等待Rich线程完成
            rich_thread.join()
            
            # 完成流式输出
            if streaming_callback:
                streaming_callback.finish()
            
            # 计算统计信息
            end_time = time.time()
            duration = end_time - api_start_time if api_start_time else 0
            chars_per_sec = total_chars / duration if duration > 0 else 0
            tokens_per_sec = total_tokens_estimate / duration if duration > 0 else 0
            
            # 计算首词响应时间 (TTFT)
            ttft = (first_token_time - api_start_time) if (first_token_time and api_start_time) else 0
            
            if result:
                # 显示统计信息，包含首词响应时间
                stats = {
                    "chars": total_chars,
                    "tokens": total_tokens_estimate,
                    "speed": chars_per_sec,
                    "token_speed": tokens_per_sec,
                    "ttft": ttft,  # Time To First Token
                    "duration": duration
                }
                display_statistics(stats)
            else:
                print_error("获取视觉分析失败")

        except AIClientError as e:
            print_error(f"视觉对话失败: {e}")
        except Exception as e:
            print_error(f"未知错误: {e}")
    
    def _chat_with_vision_batch(self, prompt: str, image_base64: str) -> None:
        """批量模式视觉对话 - Rich增强版"""
        print_info("🖼️ Qwen-VL 正在分析图片...")
        start_time = time.time()
        
        try:
            result = self.client.chat_with_scenario(prompt, "vision", image_base64=image_base64)
        except Exception as e:
            print_error(f"视觉分析失败: {e}")
            return
        
        end_time = time.time()
        duration = end_time - start_time

        if result:
            # 使用Rich显示AI回复
            display_ai_response(result, "🖼️ 视觉分析")
            
            # 统计信息
            total_chars = len(result)
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', result))
            english_chars = total_chars - chinese_chars
            total_tokens_estimate = chinese_chars // 2 + english_chars // 4
            
            stats = {
                "chars": total_chars,
                "tokens": total_tokens_estimate,
                "duration": duration
            }
            display_statistics(stats)
        else:
            print_error("获取视觉分析失败")


def main():
    parser = argparse.ArgumentParser(
        description="AI助手工具 - 支持多种输入方式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  %(prog)s chat "你的问题"                    # 基础用法
  %(prog)s chat --interactive               # 交互模式，避免特殊字符问题
  %(prog)s chat --file question.txt        # 从文件读取问题
  %(prog)s generate "文章标题"
  %(prog)s commit "更改摘要"

注意：如果问题包含特殊字符，建议使用交互模式或文件模式
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # chat命令
    chat_parser = subparsers.add_parser('chat', help='AI对话')
    chat_group = chat_parser.add_mutually_exclusive_group(required=True)
    chat_group.add_argument('question', nargs='?', help='要问的问题（可选）')
    chat_group.add_argument('-i', '--interactive', action='store_true', help='交互模式输入')
    chat_group.add_argument('-f', '--file', help='从文件读取问题')
    chat_parser.add_argument('-s', '--stream', action='store_true', help='启用流式输出')
    chat_parser.add_argument('-p', '--prompt', help='自定义 Prompt')
    chat_parser.add_argument('--prompt-file', help='从文件读取自定义 Prompt')
    chat_parser.add_argument('--image', action='store_true', help='启用图片分析模式（从剪贴板获取图片）')

    # generate命令
    gen_parser = subparsers.add_parser('generate', help='生成博客文章')
    gen_parser.add_argument('title', help='文章标题')

    # commit命令
    commit_parser = subparsers.add_parser('commit', help='生成commit信息')
    commit_parser.add_argument('changes', help='文件更改摘要')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ai = AIHelper()

    if args.command == 'chat':
        question = None
        custom_prompt = None

        # 处理问题输入
        if args.question:
            question = args.question
        elif args.interactive:
            question = ai.get_interactive_input()
        elif args.file:
            question = ai.read_question_from_file(args.file)

        # 处理自定义prompt
        if args.prompt:
            custom_prompt = args.prompt
        elif args.prompt_file:
            custom_prompt = ai.read_prompt_from_file(args.prompt_file)

        if question:
            if args.image:
                ai.chat_with_image(question, custom_prompt=custom_prompt)
            else:
                ai.chat(question, use_stream=args.stream, custom_prompt=custom_prompt)
        else:
            print_error("未提供有效的问题内容")

    elif args.command == 'generate':
        result = ai.generate_blog_article(args.title)
        if result:
            rich_output.console.print(result)
    elif args.command == 'commit':
        result = ai.generate_commit_message(args.changes)
        if result:
            print(result)  # 直接输出纯文本，供其他脚本调用
        else:
            print_error("生成commit信息失败")


if __name__ == "__main__":
    main()