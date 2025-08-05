#!/usr/bin/env python3
"""
🚀 LEION BLOG AUTOMATION ⚡
Professional Blog Generation with AI Enhancement
Powered by GLM-4-32B-0414 Model
"""

import json
import sys
from datetime import datetime
from typing import Optional
import argparse
import os
from pathlib import Path
from color_utils import print_error, print_success, print_warning, print_info, print_progress, print_debug
from ai_client import get_client, AIClientError
from ai_config import get_config
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.tree import Tree
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.rule import Rule
from rich.status import Status
from rich.layout import Layout
from rich import box
import psutil
import platform


def get_system_info():
    """获取系统信息"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        return {
            'platform': platform.system(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'python_version': platform.python_version(),
            'architecture': platform.machine()
        }
    except:
        return None


def create_leion_header(console: Console, title: str, subtitle: str):
    """创建 Leion 专业品牌标题"""
    start_time = datetime.now()
    
    # Leion 品牌标题
    header_text = Text()
    header_text.append("🚀 ", style="bold red")
    header_text.append("LEION", style="bold white on blue")
    header_text.append(" ", style="")
    header_text.append("BLOG", style="bold white on green")
    header_text.append(" ", style="")
    header_text.append("AUTOMATION", style="bold white on magenta")
    header_text.append(" ⚡", style="bold yellow")
    
    # 版本和时间信息
    version_text = Text()
    version_text.append("v2.0.0", style="dim cyan")
    version_text.append(" • ", style="dim white")
    version_text.append(f"Started at {start_time.strftime('%H:%M:%S')}", style="dim cyan")
    version_text.append(" • ", style="dim white")
    version_text.append(f"{platform.system()} {platform.machine()}", style="dim cyan")
    
    # 版权信息
    copyright_text = Text()
    copyright_text.append("© 2025 Leion Charles - All Rights Reserved", style="dim yellow")
    copyright_text.append(" • ", style="dim white")
    copyright_text.append("Professional Blog Generation Suite", style="dim green")
    
    title_content = Text()
    title_content.append(header_text)
    title_content.append("\n")
    title_content.append(version_text)
    title_content.append("\n")
    title_content.append(copyright_text)
    
    title_panel = Panel(
        Align.center(title_content),
        box=box.DOUBLE_EDGE,
        style="bright_blue",
        padding=(1, 3),
        title=f"[bold white]🎯 {title}[/bold white]",
        subtitle=f"[dim cyan]{subtitle}[/dim cyan]",
        title_align="center"
    )
    
    console.clear()
    console.print(title_panel)
    console.print()
    return start_time


class BlogAIHelper:
    def __init__(self):
        self.client = get_client()
        self.config = get_config()
        self.console = Console()

        # 博客配置
        self.blog_dir = "/Users/leion/Charles/LeionWeb/blog"
        self.posts_dir = f"{self.blog_dir}/source/_posts"
        
    def _check_network(self) -> bool:
        """检查网络连接"""
        try:
            return self.client.check_connection()
        except:
            return False
    
    def _call_glm4_api(self, prompt: str, max_tokens: int = 3000, temperature: float = 0.7) -> Optional[str]:
        """调用GLM-4-32B-0414 API，包含重试机制"""
        try:
            print_progress("正在调用 GLM-4-32B-0414 生成内容...")
            content = self.client.generate(prompt, max_tokens=max_tokens, temperature=temperature)
            print_success("AI内容生成成功！")
            return content
        except AIClientError as e:
            print_error(f"AI调用失败: {e}")
            print_error("将使用默认模板")
            return None
        except Exception as e:
            print_error(f"未知错误: {e}")
            print_error("将使用默认模板")
            return None
    
    def _generate_safe_filename(self, title: str) -> str:
        """生成安全的文件名"""
        import re
        safe_name = re.sub(r'[^\w\u4e00-\u9fa5-]', '-', title)
        safe_name = re.sub(r'-+', '-', safe_name)
        return safe_name.strip('-')
    
    def _generate_slug_from_title(self, title: str) -> str:
        """根据标题生成英文slug"""
        import re
        # 简单的中英文标题对应
        slug_mappings = {
            '教程': 'tutorial',
            '指南': 'guide', 
            '详解': 'explained',
            '入门': 'getting-started',
            '实战': 'practice',
            '技巧': 'tips',
            '总结': 'summary',
            '经验': 'experience',
            '最佳实践': 'best-practices',
            '深入': 'deep-dive',
            '原理': 'principles',
            '优化': 'optimization'
        }
        
        # 转换为小写并处理常见词汇
        slug = title.lower()
        for cn, en in slug_mappings.items():
            slug = slug.replace(cn, en)
        
        # 移除特殊字符，只保留字母、数字和连字符
        slug = re.sub(r'[^\w\s-]', '', slug)
        # 将空格和多个连字符替换为单个连字符
        slug = re.sub(r'[\s_-]+', '-', slug)
        # 移除首尾连字符
        slug = slug.strip('-')
        
        # 如果生成的slug为空或过短，使用默认格式
        if not slug or len(slug) < 3:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d")
            slug = f"article-{timestamp}"
        
        # 确保slug长度不超过50个字符
        if len(slug) > 50:
            slug = slug[:50].rstrip('-')
            
        return slug
    
    def _validate_slug(self, slug: str) -> bool:
        """验证slug格式是否正确"""
        import re
        # slug应该只包含字母、数字和连字符
        return bool(re.match(r'^[a-z0-9-]+$', slug))
    
    def _ensure_unique_filename(self, base_path: str) -> str:
        """确保文件名唯一"""
        counter = 1
        path = Path(base_path)
        original_path = path
        
        while path.exists():
            path = Path(f"{original_path.stem}-{counter}{original_path.suffix}")
            path = original_path.parent / path.name
            counter += 1
            
        return str(path)
    
    def _get_default_template(self, title: str) -> str:
        """获取默认博客模板"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""---
title: "{title}"
slug: {self._generate_slug_from_title(title)}
date: {current_time}
author: Leion Charrrrls
tags: [技术分享]
categories: [个人经历]
description: "关于{title}的技术分享和思考"
cover: ""
---

## 📝 前言

在这篇文章中，我将分享关于{title}的相关内容。

## 🎯 主要内容

### 核心概念

### 实际应用

### 最佳实践

## 🤔 深入思考

### 优势分析

### 注意事项

## 📚 参考资料

## 🎉 总结

通过本文的分享，希望能帮助大家更好地理解{title}。

---

> 💡 如果您觉得这篇文章有帮助，欢迎点赞收藏～
"""

    def generate_ai_article(self, title: str) -> str:
        """使用AI生成博客文章"""
        # 读取用户配置
        claude_config = "你是一个专业的技术博客写作助手。"
        # try:
        #     with open("/Users/leion/.claude/CLAUDE.md", "r", encoding="utf-8") as f:
        #         claude_config = f.read()
        #         print("📖 已读取用户配置文件")
        # except FileNotFoundError:
        #     print("⚠️ 未找到配置文件，使用默认配置")
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 构建专业的提示词
        ai_prompt = f"""{claude_config}

请根据文章标题「{title}」生成技术博客大纲，要求简洁明了，控制在150字以内。

## 输出格式：

**第一部分：Front-matter配置**
```yaml
---
title: "优化总结后的标题"「注这部分需要你自己优化后总结」
slug: [根据标题生成的英文slug]
date: {current_time}
author: Leion Charrrrls
cover: ""
tags: 
  - [相关技术标签1]
  - [相关技术标签2]
categories: 
  - [主分类]
description: "[简洁描述，30字以内]"
---
```

**第二部分：文章大纲**

#在这篇文章中，我将分享关于{title}的相关内容「这是前言部分，也由你优化总结」

##1. [根据标题生成的核心概念介绍]
### [子要点1]
### [子要点2]
##2. [实践操作或技术实现]
### [子要点1]
### [子要点2]
### [子要点3]
##3. [最佳实践或注意事项]
### [子要点1]
### [子要点2]
### [子要点3]
##4. [总结与扩展]
### [子要点1]
## 输出示例：
```yaml
---
title: "React Hooks详解"
slug: react-hooks-explained
date: 2025-07-23 18:30:00
author: Leion Charrrrls
cover: ""
tags: 
  - React
  - Hooks
  - 前端开发
categories: 
  - 前端技术
description: "深入解析React Hooks原理与实践应用"
---
```
#React Hooks详解，本文详细讲一下React Hooks

## 1. Hooks基础概念与核心原理解析
### [子要点1]
### [子要点2]
## 2. 常用Hooks实战应用与代码示例
### [子要点1]
### [子要点2]
### [子要点3]
## 3. 性能优化技巧与最佳实践
### [子要点1]
### [子要点2]
## 4. 进阶用法总结与学习资源推荐
### [子要点1]
### [子要点2]

## 要求：
- 标签2-3个，与技术内容相关
- 分类1个，技术领域分类
- slug字段：根据标题生成英文slug，使用连字符分隔，全小写
- 大纲不超过5点，每点15字以内，请注意格式必须为h2格式
- 可以在每个大纲下生成必要的子要点每个大纲下不超过三个h3格式
- 描述简洁，突出核心价值，可以适当加一些emoji，但是不要太多"""

        # 检查网络连接
        if not self._check_network():
            print_warning("网络连接检查失败，使用默认模板")
            return self._get_default_template(title)

        # 调用AI生成
        ai_content = self._call_glm4_api(ai_prompt, 3000, 0.7)

        if ai_content and ai_content.strip():
            return ai_content
        else:
            print_warning("AI生成失败，使用默认模板")
            return self._get_default_template(title)
    
    def create_blog_article(self, title: str, use_ai: bool = False) -> bool:
        import re
        """创建博客文章"""
        # 创建专业标题和系统信息显示
        start_time = create_leion_header(
            self.console, 
            "Leion's Professional Blog Generator",
            "AI-Powered Content Creation Platform"
        )
        
        if not title:
            self.console.print("[red]❌ 请提供文章标题[/red]")
            return False

        # 检查博客目录
        if not os.path.exists(self.blog_dir):
            self.console.print(f"[red]❌ 博客目录不存在: {self.blog_dir}[/red]")
            return False

        # 获取系统信息并显示配置
        sys_info = get_system_info()
        
        # 配置信息树
        config_tree = Tree("📊 [bold blue]Generation Configuration[/bold blue]")
        config_tree.add(f"[cyan]Article Title:[/cyan] [bright_yellow]{title}[/bright_yellow]")
        config_tree.add(f"[cyan]Mode:[/cyan] [bright_magenta]{'AI Enhanced' if use_ai else 'Standard Template'}[/bright_magenta]")
        config_tree.add(f"[cyan]Blog Directory:[/cyan] [green]{self.blog_dir}[/green]")
        config_tree.add(f"[cyan]Posts Directory:[/cyan] [green]{self.posts_dir}[/green]")
        config_tree.add(f"[cyan]Session ID:[/cyan] [dim]{start_time.strftime('%Y%m%d%H%M%S')}[/dim]")
        
        if sys_info:
            system_tree = Tree("🖥️ [bold green]System Status[/bold green]")
            system_tree.add(f"[cyan]Platform:[/cyan] [white]{sys_info['platform']} {sys_info['architecture']}[/white]")
            system_tree.add(f"[cyan]CPU Usage:[/cyan] [yellow]{sys_info['cpu_percent']:.1f}%[/yellow]")
            system_tree.add(f"[cyan]Memory:[/cyan] [yellow]{sys_info['memory_percent']:.1f}%[/yellow]") 
            system_tree.add(f"[cyan]Python:[/cyan] [green]v{sys_info['python_version']}[/green]")
            
            trees = Columns([config_tree, system_tree], equal=True, expand=True)
        else:
            trees = config_tree
        
        self.console.print(trees)
        self.console.print()
        
        # 专业分割线
        self.console.print(Rule("[bold blue]🚀 CONTENT GENERATION PIPELINE[/bold blue]", style="blue"))
        self.console.print()

        # 生成文章内容
        content = None
        filename = title
        
        if use_ai:
            with Progress(
                SpinnerColumn(style="cyan"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=None),
                TimeElapsedColumn(),
                console=self.console,
                transient=True,
            ) as progress:
                task = progress.add_task("[cyan]🤖 AI Content Generation...[/cyan]", total=None)
                content = self.generate_ai_article(title)
                
                # 提取AI生成的标题
                try:
                    filename_match = re.search(r'title:\s*"([^"]*)"', content)
                    if filename_match:
                        filename = filename_match.group(1)
                except:
                    filename = title
                    
            self.console.print("[green]✅[/green] [bold green]AI content generated successfully[/bold green]")
        else:
            with Progress(
                SpinnerColumn(style="blue"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=None),
                TimeElapsedColumn(),
                console=self.console,
                transient=True,
            ) as progress:
                task = progress.add_task("[blue]📝 Template Generation...[/blue]", total=None)
                content = self._get_default_template(title)
                
            self.console.print("[green]✅[/green] [bold green]Standard template generated[/bold green]")

        # 生成文件名和路径 - 添加中文标识后缀
        safe_filename = self._generate_safe_filename(filename)
        article_file = f"{self.posts_dir}/{safe_filename}-zh.md"
        article_file = self._ensure_unique_filename(article_file)
        
        try:
            with Progress(
                SpinnerColumn(style="magenta"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=None),
                TimeElapsedColumn(),
                console=self.console,
                transient=True,
            ) as progress:
                task = progress.add_task("[magenta]💾 Saving article...[/magenta]", total=None)
                
                # 写入文件
                with open(article_file, 'w', encoding='utf-8') as f:
                    f.write(content)

            # 成功信息展示
            elapsed = datetime.now() - start_time
            elapsed_seconds = elapsed.total_seconds()
            
            self.console.print()
            self.console.print(Rule("[bold green]🎉 ARTICLE CREATION SUCCESSFUL[/bold green]", style="green"))
            self.console.print()
            
            # 文章信息仪表板
            article_table = Table(
                show_header=True,
                header_style="bold white on blue",
                box=box.DOUBLE_EDGE,
                title="[bold white]📄 ARTICLE INFORMATION[/bold white]",
                title_style="bold green on black",
                border_style="bright_green",
                padding=(1, 2),
                expand=True
            )
            article_table.add_column("Property", style="bold cyan", width=20)
            article_table.add_column("Value", style="bold white")
            article_table.add_column("Status", style="bold green", width=15)
            
            article_table.add_row("📝 Article Title", filename, "🟢 READY")
            article_table.add_row("📁 File Path", article_file, "🟢 SAVED")
            article_table.add_row("📊 Generation Mode", "AI Enhanced" if use_ai else "Standard", "🟢 APPLIED")
            article_table.add_row("⚡ Process Time", f"{elapsed_seconds:.2f}s", "🟢 FAST")
            article_table.add_row("🔗 Slug Generated", self._generate_slug_from_title(filename), "🟢 OPTIMIZED")
            
            self.console.print(article_table)
            self.console.print()

            # 尝试用Typora打开
            typora_status = False
            try:
                import subprocess
                subprocess.run(['open', '-a', 'Typora', article_file], check=True)
                typora_status = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                typora_status = False
            
            # 最终操作面板
            if typora_status:
                operation_panel = Panel(
                    "[bold white]🎯 ARTICLE READY FOR EDITING[/bold white]\n\n"
                    f"[bright_green]✅ Article created: {os.path.basename(article_file)}[/bright_green]\n"
                    f"[bright_blue]📂 Location: {article_file}[/bright_blue]\n"
                    f"[bright_magenta]✨ Typora opened automatically for editing[/bright_magenta]\n\n"
                    "[dim white]Your professional blog article is ready for customization[/dim white]\n"
                    "[dim cyan]Crafted with ❤️ by Leion • Professional Blog Solutions[/dim cyan]",
                    title="[bold yellow]🚀 LEION BLOG CONTROL CENTER[/bold yellow]",
                    border_style="yellow",
                    box=box.DOUBLE_EDGE,
                    padding=(1, 2)
                )
            else:
                operation_panel = Panel(
                    "[bold white]🎯 ARTICLE CREATION COMPLETED[/bold white]\n\n"
                    f"[bright_green]✅ Article created: {os.path.basename(article_file)}[/bright_green]\n"
                    f"[bright_blue]📂 Location: {article_file}[/bright_blue]\n"
                    f"[bright_yellow]📝 Please manually open in your preferred editor[/bright_yellow]\n\n"
                    "[dim white]Your professional blog article is ready for editing[/dim white]\n"
                    "[dim cyan]Crafted with ❤️ by Leion • Professional Blog Solutions[/dim cyan]",
                    title="[bold yellow]🚀 LEION BLOG CONTROL CENTER[/bold yellow]",
                    border_style="yellow",
                    box=box.DOUBLE_EDGE,
                    padding=(1, 2)
                )
            
            self.console.print(operation_panel)
            self.console.print()

            return True

        except Exception as e:
            self.console.print(f"[red]❌ 创建文章失败: {e}[/red]")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="🚀 LEION BLOG AUTOMATION ⚡ - Professional Blog Generation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 Usage Examples:
  %(prog)s "Python装饰器详解"           # Standard mode - Quick creation
  %(prog)s "Python装饰器详解" --ai      # AI mode - Intelligent content generation  
  %(prog)s "机器学习入门" -ai           # AI mode (short form)
  
✨ Features:
  • Professional Rich Terminal UI
  • AI-powered content generation with GLM-4-32B-0414
  • Automatic slug generation for SEO optimization
  • Real-time system monitoring and progress tracking
  • Auto-launch Typora for seamless editing experience
  
© 2025 Leion Charles - Professional Blog Solutions
        """
    )
    
    parser.add_argument('title', help='Article title for blog post generation')
    parser.add_argument('--ai', '-ai', action='store_true', 
                       help='Enable AI Enhanced Mode using GLM-4-32B-0414 for intelligent content generation')
    
    args = parser.parse_args()
    
    try:
        # 创建AI助手实例并生成文章
        helper = BlogAIHelper()
        success = helper.create_blog_article(args.title, args.ai)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        console = Console()
        console.print()
        console.print(Rule("[bold yellow]🛑 Process Interrupted[/bold yellow]", style="yellow"))
        console.print()
        
        shutdown_panel = Panel(
            "[bold white]✨ Blog generation process stopped gracefully[/bold white]\n"
            "[dim white]No files were created during this session[/dim white]\n\n"
            "[dim cyan]Thank you for using Leion's Professional Blog Generator[/dim cyan]",
            title="[bold yellow]👋 Goodbye from Leion[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED
        )
        console.print(Align.center(shutdown_panel))
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]❌ Unexpected error occurred: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()