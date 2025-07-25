#!/usr/bin/env python3
"""
Rich输出工具模块 - by 阮阮
使用Rich库提供专业级的终端输出效果，完美支持Markdown、代码高亮等
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.align import Align
from rich.padding import Padding
from rich.rule import Rule
import time
import re


class RichOutput:
    """Rich输出管理器"""
    
    def __init__(self):
        # 创建控制台实例，支持强制颜色和emoji
        self.console = Console(
            force_terminal=True,
            color_system="256",  # 使用256色
            width=None,  # 自动检测终端宽度
            emoji=True,
            markup=True,
            highlight=False  # 禁用自动高亮以避免冲突
        )
        
        # AI回复的面板样式
        self.ai_panel_style = "bold white on blue"
        self.ai_border_style = "bright_blue"
        
    def print_info(self, message: str):
        """输出信息提示"""
        self.console.print(f"[bold blue]:information: {message}[/]")
    
    def print_success(self, message: str):
        """输出成功信息"""
        self.console.print(f"[bold green]:white_check_mark: {message}[/]")
    
    def print_warning(self, message: str):
        """输出警告信息"""
        self.console.print(f"[bold yellow]:warning: {message}[/]")
    
    def print_error(self, message: str):
        """输出错误信息"""
        self.console.print(f"[bold red]:x: {message}[/]")
    
    def print_progress(self, message: str):
        """输出进度状态"""
        self.console.print(f"[bold orange1]:gear: {message}[/]")
    
    def print_ai_response_start(self, message: str = "GLM-4 正在回答中..."):
        """显示AI回复开始"""
        self.console.print()
        self.console.print(f"[bold cyan]:robot: {message}[/]")
        self.console.print()
    
    def create_ai_panel(self, content: str, title: str = "AI 回复") -> Panel:
        """创建AI回复面板"""
        # 检测内容中是否包含Markdown
        if self._contains_markdown(content):
            # 使用Markdown渲染
            markdown_content = Markdown(content, code_theme="monokai")
            panel_content = markdown_content
        else:
            # 普通文本，添加高亮样式
            panel_content = Text(content, style="white")
        
        return Panel(
            panel_content,
            title=f"[bold bright_blue]{title}[/]",
            title_align="left",
            border_style=self.ai_border_style,
            padding=(1, 2),
            expand=False
        )
    
    def display_ai_response(self, content: str, title: str = "AI 回复"):
        """显示AI回复内容"""
        panel = self.create_ai_panel(content, title)
        self.console.print(panel)
    
    def stream_ai_response(self, content_chunks, title: str = "AI 回复"):
        """流式显示AI回复"""
        # 创建实时更新的面板
        full_content = ""
        
        with Live(console=self.console, refresh_per_second=10) as live:
            for chunk in content_chunks:
                full_content += chunk
                panel = self.create_ai_panel(full_content + "[dim]▊[/]", title)  # 添加光标效果
                live.update(panel)
                time.sleep(0.02)  # 模拟流式效果
            
            # 最终版本，移除光标
            final_panel = self.create_ai_panel(full_content, title)
            live.update(final_panel)
    
    def display_code_block(self, code: str, language: str = "python", title: str = None):
        """显示代码块"""
        syntax = Syntax(
            code, 
            language, 
            theme="monokai",  # 使用专业的代码主题
            line_numbers=True,
            background_color="default"
        )
        
        if title:
            panel = Panel(
                syntax,
                title=f"[bold bright_green]{title}[/]",
                title_align="left", 
                border_style="bright_green",
                padding=(1, 1)
            )
            self.console.print(panel)
        else:
            self.console.print(syntax)
    
    def display_markdown(self, markdown_text: str):
        """显示Markdown内容"""
        md = Markdown(markdown_text, code_theme="monokai")
        self.console.print(md)
    
    def display_statistics(self, stats: dict):
        """显示统计信息"""
        # 构建单行统计信息（英文简称）
        stat_parts = []
        
        if "chars" in stats:
            stat_parts.append(f"{stats['chars']} chars")
        if "speed" in stats:
            stat_parts.append(f"{stats['speed']:.1f} chars/s")
        if "duration" in stats:
            stat_parts.append(f"{stats['duration']:.1f}s")
        
        # 使用分隔符连接
        stats_line = " | ".join(stat_parts)
        
        # 获取终端宽度并右对齐
        console_width = self.console.size.width
        self.console.print()
        self.console.print(f"[dim]{stats_line}[/]", justify="right")
    
    def display_separator(self, title: str = None):
        """显示分隔符"""
        if title:
            rule = Rule(title, style="bright_blue")
        else:
            rule = Rule(style="dim")
        self.console.print(rule)
    
    def _contains_markdown(self, text: str) -> bool:
        """检测文本是否包含Markdown语法"""
        markdown_patterns = [
            r'```\w*\n.*?\n```',  # 代码块
            r'`[^`]+`',           # 行内代码
            r'^\s*#{1,6}\s+',     # 标题
            r'^\s*[-*+]\s+',      # 列表
            r'\*\*[^*]+\*\*',     # 粗体
            r'\*[^*]+\*',         # 斜体
            r'^\s*\d+\.\s+',      # 有序列表
        ]
        
        for pattern in markdown_patterns:
            if re.search(pattern, text, re.MULTILINE | re.DOTALL):
                return True
        return False
    
    def create_streaming_callback(self, title: str = "AI 回复"):
        """创建流式输出回调函数"""
        content = ""
        live = Live(console=self.console, refresh_per_second=8)
        live.start()
        
        def callback(chunk: str):
            nonlocal content
            content += chunk
            panel = self.create_ai_panel(content + "[dim]▊[/]", title)
            live.update(panel)
        
        def finish():
            nonlocal content
            final_panel = self.create_ai_panel(content, title)
            live.update(final_panel)
            live.stop()
        
        callback.finish = finish
        return callback
    
    def display_help_info(self):
        """显示帮助信息"""
        help_content = """
# 🤖 GLM-4 AI助手 - Rich增强版

## 用法
- `kimi "你的问题"` - 基础用法（流式输出）
- `kimi -i` - 交互模式（推荐）
- `kimi -f question.txt` - 从文件读取
- `kimi --batch "问题"` - 批量模式
- `kimi --help` - 显示帮助

## ✨ Rich增强特点
- 🎨 **专业级Markdown渲染**：完美支持标题、列表、代码块
- 🔥 **语法高亮**：Python、JavaScript、SQL等多语言支持
- 📦 **美观面板**：AI回复带边框和标题
- ⚡ **流式更新**：实时光标效果，类似打字机
- 📊 **统计面板**：性能数据清晰展示

## 🚀 流式输出特点
- 实时显示AI回复，类似ChatGPT效果
- 光标闪烁效果，更好的视觉反馈
- 自适应终端宽度

## 交互模式特点
- 支持任何特殊字符：`()""''``
- 支持多行输入
- 输入'END'结束

## 示例
```bash
kimi "写一个Python快速排序函数"
kimi -i
echo "解释机器学习" > question.txt && kimi -f question.txt
```
        """
        
        self.display_markdown(help_content.strip())


# 创建全局实例
rich_output = RichOutput()

# 兼容性函数，保持原有接口
def print_info(message: str):
    rich_output.print_info(message)

def print_success(message: str):
    rich_output.print_success(message)

def print_warning(message: str):
    rich_output.print_warning(message)

def print_error(message: str):
    rich_output.print_error(message)

def print_progress(message: str):
    rich_output.print_progress(message)

def display_ai_response(content: str, title: str = "AI 回复"):
    rich_output.display_ai_response(content, title)

def display_code_block(code: str, language: str = "python", title: str = None):
    rich_output.display_code_block(code, language, title)

def display_markdown(markdown_text: str):
    rich_output.display_markdown(markdown_text)

def display_statistics(stats: dict):
    rich_output.display_statistics(stats)

def create_streaming_callback(title: str = "AI 回复"):
    return rich_output.create_streaming_callback(title)

# 向后兼容的空函数
def colored_print(message: str, msg_type=None, **kwargs):
    """向后兼容函数"""
    if msg_type and hasattr(msg_type, 'value'):
        msg_type = msg_type.value.lower()
    
    if msg_type == 'error':
        print_error(message)
    elif msg_type == 'success':
        print_success(message)
    elif msg_type == 'warning':
        print_warning(message)
    elif msg_type == 'info':
        print_info(message)
    elif msg_type == 'progress':
        print_progress(message)
    else:
        rich_output.console.print(message)

class MessageType:
    """兼容性消息类型"""
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    INFO = "INFO"
    NORMAL = "NORMAL"
    DEBUG = "DEBUG"
    PROGRESS = "PROGRESS"


if __name__ == "__main__":
    # 演示Rich输出效果
    rich_output.print_info("Rich输出工具演示")
    rich_output.display_separator("演示开始")
    
    # 演示代码块
    code = '''def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr'''
    
    rich_output.display_code_block(code, "python", "冒泡排序算法")
    
    # 演示Markdown
    markdown_content = """
## 冒泡排序算法

冒泡排序是一种简单的排序算法，具有以下特点：

- **时间复杂度**: O(n²)
- **空间复杂度**: O(1)
- **稳定性**: 稳定排序

### 优化建议
可以添加标志位提前终止已排序的数组处理。
    """
    
    rich_output.display_markdown(markdown_content)
    
    # 演示统计信息
    stats = {
        "chars": 150,
        "tokens": 75,
        "speed": 45.2,
        "token_speed": 22.6,
        "duration": 3.32
    }
    rich_output.display_statistics(stats)