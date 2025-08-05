#!/usr/bin/env python
"""
🚀 LEION BLOG MANAGEMENT SUITE ⚡
Professional Blog Operations & Services Platform
Enhanced with Rich Terminal UI & AI Integration
"""

import os
import sys
import subprocess
import re
import argparse
from datetime import datetime
from pathlib import Path
from color_utils import print_error, print_success, print_warning, print_info, print_progress, colored_print, MessageType
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


def create_leion_server_header(console: Console):
    """创建 Leion 博客服务器专业标题"""
    start_time = datetime.now()
    
    # Leion 服务器品牌标题
    header_text = Text()
    header_text.append("🌐 ", style="bold blue")
    header_text.append("LEION", style="bold white on blue")
    header_text.append(" ", style="")
    header_text.append("BLOG", style="bold white on green")
    header_text.append(" ", style="")
    header_text.append("SERVER", style="bold white on magenta")
    header_text.append(" 🚀", style="bold yellow")
    
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
    copyright_text.append("Professional Blog Development Server", style="dim green")
    
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
        title="[bold white]🎯 Leion's Professional Blog Development Environment[/bold white]",
        subtitle="[dim cyan]Local Development Server with Hot Reload[/dim cyan]",
        title_align="center"
    )
    
    console.clear()
    console.print(title_panel)
    console.print()
    return start_time


def create_leion_git_header(console: Console):
    """创建 Leion Git 推送专业标题"""
    start_time = datetime.now()
    
    # Leion Git 品牌标题
    header_text = Text()
    header_text.append("📡 ", style="bold green")
    header_text.append("LEION", style="bold white on blue")
    header_text.append(" ", style="")
    header_text.append("GIT", style="bold white on green")
    header_text.append(" ", style="")
    header_text.append("DEPLOYMENT", style="bold white on magenta")
    header_text.append(" 🚀", style="bold yellow")
    
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
    copyright_text.append("Professional Git Deployment System", style="dim green")
    
    title_content = Text()
    title_content.append(header_text)
    title_content.append("\n")
    title_content.append(version_text)
    title_content.append("\n")
    title_content.append(copyright_text)
    
    title_panel = Panel(
        Align.center(title_content),
        box=box.DOUBLE_EDGE,
        style="bright_green",
        padding=(1, 3),
        title="[bold white]🎯 Leion's Professional Git Deployment Suite[/bold white]",
        subtitle="[dim cyan]Intelligent Commit Analysis & GitHub Integration[/dim cyan]",
        title_align="center"
    )
    
    console.clear()
    console.print(title_panel)
    console.print()
    return start_time


class BlogManager:
    def __init__(self):
        self.blog_dir = "/Users/leion/Charles/LeionWeb/blog"
        self.posts_dir = f"{self.blog_dir}/source/_posts"
        self.main_blog_dir = "/Users/leion/Charles/LeionWeb"
        self.ai_helper_script = "/Users/leion/scripts/ai_helper.py"
        self.console = Console()
        
        # 配置文件路径
        self.config_dir = os.path.join(os.path.dirname(__file__), 'config')
        self.optimizer_config = os.path.join(self.config_dir, 'blog_optimizer.txt')
        self.translator_config = os.path.join(self.config_dir, 'blog_translator.txt')
        
        # 导入AI客户端
        try:
            from ai_client import get_client, AIClientError
            self.client = get_client()
        except ImportError:
            self.client = None
    
    def _load_prompt_template(self, config_file: str) -> str:
        """加载提示词模板文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            self.console.print(f"[yellow]⚠️ 配置文件未找到: {config_file}[/yellow]")
            return None
        except Exception as e:
            self.console.print(f"[red]❌ 读取配置文件失败: {e}[/red]")
            return None
        
    def _run_command(self, cmd: str, cwd: str = None) -> tuple[bool, str]:
        """执行shell命令"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                cwd=cwd or os.getcwd(),
                capture_output=True, 
                text=True
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
            
    def _generate_safe_filename(self, title: str) -> str:
        """生成安全的文件名"""
        # 移除特殊字符，保留中文、英文、数字和连字符
        safe_name = re.sub(r'[^\w\u4e00-\u9fa5-]', '-', title)
        safe_name = re.sub(r'-+', '-', safe_name)  # 合并多个连字符
        return safe_name.strip('-')
        
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
        
    def new_article(self, title: str) -> bool:
        """创建新博客文章"""
        if not title:
            print_error("请提供文章标题")
            print_info("使用方法: python blog_manager.py new \"文章标题\"")
            return False

        # 检查博客目录
        if not os.path.exists(self.blog_dir):
            print_error(f"博客目录不存在: {self.blog_dir}")
            return False

        print_info("切换到博客目录...")
        original_dir = os.getcwd()

        try:
            os.chdir(self.blog_dir)

            # 调用AI生成文章结构
            print_progress("正在调用AI生成文章结构...")
            success, ai_content = self._run_command(
                f'python3 "{self.ai_helper_script}" generate "{title}"'
            )
            
            if success and ai_content.strip():
                # 生成安全的文件名
                safe_filename = self._generate_safe_filename(title)
                article_file = f"{self.posts_dir}/{safe_filename}.md"
                article_file = self._ensure_unique_filename(article_file)
                
                # 写入AI生成的内容
                try:
                    with open(article_file, 'w', encoding='utf-8') as f:
                        f.write(ai_content)

                    print_success(f"文章创建成功: {os.path.basename(article_file)}")
                    print_info(f"文件路径: {article_file}")

                    # 用Typora打开文件
                    print_progress("正在用 Typora 打开文章...")
                    success, _ = self._run_command(f'open -a "Typora" "{article_file}"')

                    if success:
                        print_success("Typora 已打开，开始您的创作之旅！")
                        print_info("文章已包含完整结构和AI建议的大纲")
                    else:
                        print_warning("Typora 打开失败，请手动打开文件")

                    return True

                except Exception as e:
                    print_error(f"写入文件失败: {e}")
                    return False
                    
            else:
                print_warning("AI生成失败，使用传统方式创建文章")
                success, output = self._run_command(f'hexo new "{title}"')

                if success:
                    print_success("文章创建成功（使用默认模板）")

                    # 查找刚创建的文件
                    success, output = self._run_command(f'find "{self.posts_dir}" -name "*{title}*.md" -type f -newermt "1 minute ago"')
                    if success and output.strip():
                        article_file = output.strip().split('\n')[0]
                        self._run_command(f'open -a "Typora" "{article_file}"')

                    return True
                else:
                    print_error(f"创建文章失败: {output}")
                    return False

        finally:
            os.chdir(original_dir)
            print_info("已返回原目录")
            
    def _generate_commit_message(self, changes_summary: str) -> str:
        """使用AI生成有意义的commit信息"""
        try:
            # 清理摘要内容，避免命令行解析问题
            cleaned_summary = self._clean_summary_for_command(changes_summary)

            # 调用AI助手生成commit信息
            success, ai_commit = self._run_command(
                f'python3 "{self.ai_helper_script}" commit "{cleaned_summary}"'
            )

            if success and ai_commit.strip():
                # 清理AI返回的内容，只保留commit信息
                commit_msg = ai_commit.strip().split('\n')[0]  # 取第一行
                # 移除可能的引号和多余字符
                commit_msg = commit_msg.strip('"\'').strip()
                
                # 调试信息 - 显示AI生成的原始内容
                if self.console:
                    self.console.print(f"[dim]🔍 AI生成原始信息: {ai_commit.strip()[:100]}...[/dim]")
                    self.console.print(f"[dim]🔍 处理后的信息: {commit_msg}[/dim]")
                    self.console.print(f"[dim]🔍 信息长度: {len(commit_msg)}[/dim]")

                # 放宽长度限制，确保AI生成的信息能被使用
                if len(commit_msg) > 5 and len(commit_msg) < 200:
                    return commit_msg
                elif commit_msg:  # 如果有内容但长度不符合，截取或补充
                    if len(commit_msg) > 200:
                        return commit_msg[:197] + "..."
                    elif len(commit_msg) <= 5:
                        return f"更新内容: {commit_msg}"

        except Exception as e:
            if self.console:
                self.console.print(f"[dim red]🔍 AI生成commit信息失败: {e}[/dim red]")

        # 备用方案：基于时间的默认信息
        return f"更新博客内容: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    def _clean_summary_for_command(self, summary: str) -> str:
        """清理摘要内容，避免命令行解析问题"""
        # 替换可能导致问题的字符
        cleaned = summary.replace('"', "'")  # 双引号替换为单引号
        cleaned = cleaned.replace('`', "'")  # 反引号替换为单引号
        cleaned = cleaned.replace('\\', '/')  # 反斜杠替换为正斜杠

        # 移除过长的URL或路径
        import re
        cleaned = re.sub(r'https?://[^\s;]+', '[链接]', cleaned)
        cleaned = re.sub(r'<[^>]+>', '[标签]', cleaned)  # 移除HTML标签

        # 限制长度
        if len(cleaned) > 200:
            cleaned = cleaned[:200] + "..."

        return cleaned
        
    def _get_changes_summary(self) -> str:
        """获取详细的文件更改摘要用于生成commit信息"""
        return self._get_detailed_changes_summary()

    def _get_detailed_changes_summary(self) -> str:
        """获取详细的更改分析"""
        changes_info = []

        # 获取文件状态信息
        success, status_output = self._run_command("git status --porcelain")
        if not success:
            return self._get_simple_changes_summary()

        # 获取详细diff内容
        success, diff_output = self._run_command("git diff --cached")
        if not success:
            return self._get_simple_changes_summary()

        # 获取文件统计信息
        success, stat_output = self._run_command("git diff --cached --stat")
        if not success:
            stat_output = ""

        # 分析每个文件的详细变更
        file_changes = self._analyze_detailed_changes(status_output, diff_output, stat_output)

        # 生成结构化的变更摘要
        return self._format_changes_summary(file_changes)
    
    def _analyze_detailed_changes(self, status_output: str, diff_output: str, stat_output: str) -> list:
        """详细分析所有文件的变更内容"""
        changes = []
        
        # 解析文件状态
        file_statuses = {}
        for line in status_output.strip().split('\n'):
            if len(line) > 3:
                status = line[:2].strip()
                filepath = line[3:].strip().strip('"')
                file_statuses[filepath] = status
        
        # 解析统计信息
        file_stats = {}
        for line in stat_output.strip().split('\n'):
            if '|' in line and ('+' in line or '-' in line):
                parts = line.split('|')
                if len(parts) >= 2:
                    filename = parts[0].strip()
                    stats_part = parts[1].strip()
                    # 提取数字统计
                    import re
                    numbers = re.findall(r'\d+', stats_part)
                    additions = stats_part.count('+')
                    deletions = stats_part.count('-')
                    file_stats[filename] = {
                        'additions': additions,
                        'deletions': deletions,
                        'changes': int(numbers[0]) if numbers else additions + deletions
                    }
        
        # 分析每个文件的diff内容
        current_file = None
        file_diffs = {}
        
        for line in diff_output.split('\n'):
            if line.startswith('diff --git'):
                # 提取文件路径
                parts = line.split(' ')
                if len(parts) >= 4:
                    current_file = parts[3].replace('b/', '').strip()
                    file_diffs[current_file] = {
                        'added_lines': [],
                        'deleted_lines': [],
                        'context_lines': []
                    }
            elif current_file and line.startswith('+') and not line.startswith('+++'):
                file_diffs[current_file]['added_lines'].append(line[1:].strip())
            elif current_file and line.startswith('-') and not line.startswith('---'):
                file_diffs[current_file]['deleted_lines'].append(line[1:].strip())
            elif current_file and not line.startswith(('@', '\\', 'index ', 'new file', 'deleted file')):
                file_diffs[current_file]['context_lines'].append(line.strip())
        
        # 为每个文件生成详细分析
        for filepath in file_statuses.keys():
            change_info = {
                'filepath': filepath,
                'filename': filepath.split('/')[-1],
                'status': file_statuses.get(filepath, ''),
                'stats': file_stats.get(filepath, {'additions': 0, 'deletions': 0, 'changes': 0}),
                'diff': file_diffs.get(filepath, {'added_lines': [], 'deleted_lines': [], 'context_lines': []}),
                'analysis': self._analyze_file_changes(filepath, file_diffs.get(filepath, {}))
            }
            changes.append(change_info)
        
        return changes
    
    def _analyze_file_changes(self, filepath: str, diff_data: dict) -> str:
        """深度分析单个文件的变更内容"""
        added_lines = diff_data.get('added_lines', [])
        deleted_lines = diff_data.get('deleted_lines', [])
        
        # 根据文件类型进行专门分析
        if filepath.endswith('.md'):
            return self._analyze_markdown_changes(filepath, added_lines, deleted_lines)
        elif filepath.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs')):
            return self._analyze_code_changes(filepath, added_lines, deleted_lines)
        elif filepath.endswith(('.yml', '.yaml', '.json', '.toml', '.ini')):
            return self._analyze_config_changes(filepath, added_lines, deleted_lines)
        elif filepath.endswith(('.css', '.scss', '.less')):
            return self._analyze_style_changes(filepath, added_lines, deleted_lines)
        elif filepath.endswith(('.html', '.jsx', '.tsx', '.vue')):
            return self._analyze_template_changes(filepath, added_lines, deleted_lines)
        elif filepath.endswith(('.sql', '.db')):
            return self._analyze_database_changes(filepath, added_lines, deleted_lines)
        else:
            return self._analyze_general_changes(filepath, added_lines, deleted_lines)
    
    def _analyze_markdown_changes(self, filepath: str, added_lines: list, deleted_lines: list) -> str:
        """分析Markdown文件变更"""
        analysis = []
        
        # 检查是否是博客文章
        is_blog_post = 'source/_posts/' in filepath
        
        # 分析front-matter变更
        fm_changes = []
        for line in added_lines + deleted_lines:
            if line.startswith(('title:', 'slug:', 'tags:', 'categories:', 'date:', 'cover:')):
                key = line.split(':')[0].strip()
                if key not in [c.split(':')[0] for c in fm_changes]:
                    fm_changes.append(f"{key}配置")
        
        if fm_changes:
            analysis.append(f"更新{'/'.join(fm_changes[:3])}")
        
        # 分析内容变更
        added_headers = [line for line in added_lines if line.startswith('#')]
        deleted_headers = [line for line in deleted_lines if line.startswith('#')]
        added_links = [line for line in added_lines if '[' in line and '](' in line]
        added_code = [line for line in added_lines if line.startswith('```') or line.startswith('    ')]
        added_images = [line for line in added_lines if '![' in line]
        
        if added_headers:
            headers = [h.strip('#').strip()[:20] for h in added_headers[:2]]
            analysis.append(f"新增章节「{'/'.join(headers)}」")
        
        if deleted_headers:
            headers = [h.strip('#').strip()[:20] for h in deleted_headers[:2]]
            analysis.append(f"删除章节「{'/'.join(headers)}」")
        
        if added_images:
            analysis.append(f"添加{len(added_images)}张图片")
        
        if added_links:
            analysis.append(f"添加{len(added_links)}个链接")
        
        if added_code:
            analysis.append("添加代码示例")
        
        # 内容长度分析
        if len(added_lines) > len(deleted_lines) + 10:
            analysis.append("大幅补充内容")
        elif len(deleted_lines) > len(added_lines) + 10:
            analysis.append("大幅删减内容")
        elif len(added_lines) > 5 or len(deleted_lines) > 5:
            analysis.append("修改内容")
        
        return f"{'博客文章' if is_blog_post else 'Markdown文档'}: {' + '.join(analysis) if analysis else '微调内容'}"
    
    def _analyze_code_changes(self, filepath: str, added_lines: list, deleted_lines: list) -> str:
        """分析代码文件变更"""
        analysis = []
        
        # 检测语言
        lang = filepath.split('.')[-1]
        lang_names = {
            'py': 'Python', 'js': 'JavaScript', 'ts': 'TypeScript', 
            'java': 'Java', 'cpp': 'C++', 'c': 'C', 'go': 'Go', 'rs': 'Rust'
        }
        
        # 分析函数/方法变更
        func_patterns = {
            'py': r'def\s+(\w+)',
            'js': r'function\s+(\w+)|(\w+)\s*[:=]\s*\(',
            'ts': r'function\s+(\w+)|(\w+)\s*[:=]\s*\(',
            'java': r'(public|private|protected).*\s+(\w+)\s*\(',
            'cpp': r'\w+\s+(\w+)\s*\(',
            'c': r'\w+\s+(\w+)\s*\(',
            'go': r'func\s+(\w+)',
            'rs': r'fn\s+(\w+)'
        }
        
        import re
        pattern = func_patterns.get(lang, r'function\s+(\w+)')
        
        added_functions = []
        deleted_functions = []
        
        for line in added_lines:
            matches = re.findall(pattern, line)
            if matches:
                for match in matches:
                    func_name = match[0] if isinstance(match, tuple) else match
                    if func_name and func_name not in ['', 'if', 'for', 'while']:
                        added_functions.append(func_name)
        
        for line in deleted_lines:
            matches = re.findall(pattern, line)
            if matches:
                for match in matches:
                    func_name = match[0] if isinstance(match, tuple) else match
                    if func_name and func_name not in ['', 'if', 'for', 'while']:
                        deleted_functions.append(func_name)
        
        # 分析导入/包含变更
        import_patterns = {
            'py': r'(import\s+\w+|from\s+\w+\s+import)',
            'js': r'(import\s+.*from|require\s*\()',
            'ts': r'(import\s+.*from|require\s*\()',
            'java': r'import\s+[\w.]+',
            'cpp': r'#include\s*[<"][\w./]+[>"]',
            'c': r'#include\s*[<"][\w./]+[>"]',
            'go': r'import\s+',
            'rs': r'use\s+[\w::]+',
        }
        
        import_pattern = import_patterns.get(lang, r'import')
        added_imports = [line for line in added_lines if re.search(import_pattern, line)]
        deleted_imports = [line for line in deleted_lines if re.search(import_pattern, line)]
        
        # 分析类定义
        class_patterns = {
            'py': r'class\s+(\w+)',
            'java': r'class\s+(\w+)',
            'cpp': r'class\s+(\w+)',
            'ts': r'class\s+(\w+)',
            'js': r'class\s+(\w+)',
            'rs': r'struct\s+(\w+)|enum\s+(\w+)',
        }
        
        class_pattern = class_patterns.get(lang, r'class\s+(\w+)')
        added_classes = [re.findall(class_pattern, line) for line in added_lines if re.search(class_pattern, line)]
        deleted_classes = [re.findall(class_pattern, line) for line in deleted_lines if re.search(class_pattern, line)]
        
        # 生成分析结果
        if added_functions:
            analysis.append(f"新增函数: {'/'.join(added_functions[:3])}")
        if deleted_functions:
            analysis.append(f"删除函数: {'/'.join(deleted_functions[:3])}")
        if added_imports:
            analysis.append(f"新增{len(added_imports)}个导入")
        if deleted_imports:
            analysis.append(f"删除{len(deleted_imports)}个导入")
        if added_classes:
            analysis.append(f"新增类定义")
        if deleted_classes:
            analysis.append(f"删除类定义")
        
        # 代码量分析
        if len(added_lines) > len(deleted_lines) + 20:
            analysis.append("大量新增代码")
        elif len(deleted_lines) > len(added_lines) + 20:
            analysis.append("大量删除代码")
        elif len(added_lines) > 10 or len(deleted_lines) > 10:
            analysis.append("重构代码")
        else:
            analysis.append("微调代码")
        
        lang_name = lang_names.get(lang, lang.upper())
        return f"{lang_name}代码: {' + '.join(analysis) if analysis else '微调'}"
    
    def _analyze_config_changes(self, filepath: str, added_lines: list, deleted_lines: list) -> str:
        """分析配置文件变更"""
        analysis = []
        
        # 检测配置类型
        config_type = "配置文件"
        if filepath.endswith('.json'):
            config_type = "JSON配置"
        elif filepath.endswith(('.yml', '.yaml')):
            config_type = "YAML配置"
        elif filepath.endswith('.toml'):
            config_type = "TOML配置"
        elif filepath.endswith('.ini'):
            config_type = "INI配置"
        
        # 分析配置项变更
        added_configs = []
        deleted_configs = []
        
        for line in added_lines:
            if ':' in line and not line.strip().startswith('#'):
                key = line.split(':')[0].strip().strip('"\'')
                if key and len(key) < 30:
                    added_configs.append(key)
            elif '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip().strip('"\'')
                if key and len(key) < 30:
                    added_configs.append(key)
        
        for line in deleted_lines:
            if ':' in line and not line.strip().startswith('#'):
                key = line.split(':')[0].strip().strip('"\'')
                if key and len(key) < 30:
                    deleted_configs.append(key)
            elif '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip().strip('"\'')
                if key and len(key) < 30:
                    deleted_configs.append(key)
        
        if added_configs:
            analysis.append(f"新增{'/'.join(added_configs[:3])}配置")
        if deleted_configs:
            analysis.append(f"删除{'/'.join(deleted_configs[:3])}配置")
        
        # 特殊配置文件分析
        if 'package.json' in filepath:
            deps_changes = []
            for line in added_lines + deleted_lines:
                if '"dependencies"' in line or '"devDependencies"' in line:
                    deps_changes.append("依赖包")
                elif '"scripts"' in line:
                    deps_changes.append("脚本命令")
            if deps_changes:
                analysis.extend(deps_changes)
        
        elif '_config' in filepath:
            for line in added_lines:
                if any(key in line for key in ['url:', 'title:', 'theme:', 'deploy:']):
                    analysis.append("核心配置更新")
                    break
        
        return f"{config_type}: {' + '.join(analysis) if analysis else '配置调整'}"
    
    def _analyze_style_changes(self, filepath: str, added_lines: list, deleted_lines: list) -> str:
        """分析样式文件变更"""
        analysis = []
        
        # 检测选择器变更
        added_selectors = [line for line in added_lines if '{' in line and not line.strip().startswith('//')]
        deleted_selectors = [line for line in deleted_lines if '{' in line and not line.strip().startswith('//')]
        
        # 检测属性变更
        added_properties = [line for line in added_lines if ':' in line and ';' in line]
        
        if added_selectors:
            analysis.append(f"新增{len(added_selectors)}个样式规则")
        if deleted_selectors:
            analysis.append(f"删除{len(deleted_selectors)}个样式规则")
        if len(added_properties) > 10:
            analysis.append("大量样式属性调整")
        elif added_properties:
            analysis.append("样式属性调整")
        
        style_type = "CSS样式"
        if filepath.endswith('.scss'):
            style_type = "SCSS样式"
        elif filepath.endswith('.less'):
            style_type = "LESS样式"
        
        return f"{style_type}: {' + '.join(analysis) if analysis else '样式微调'}"
    
    def _analyze_template_changes(self, filepath: str, added_lines: list, deleted_lines: list) -> str:
        """分析模板文件变更"""
        analysis = []
        
        # 检测HTML标签变更
        import re
        added_tags = []
        for line in added_lines:
            tags = re.findall(r'<(\w+)', line)
            added_tags.extend(tags)
        
        deleted_tags = []
        for line in deleted_lines:
            tags = re.findall(r'<(\w+)', line)
            deleted_tags.extend(tags)
        
        # 检测组件变更
        added_components = [line for line in added_lines if '<' in line and '>' in line and line.strip().startswith('<')]
        
        if added_components:
            analysis.append(f"新增{len(added_components)}个UI组件")
        if added_tags:
            unique_tags = list(set(added_tags))[:3]
            analysis.append(f"添加{'/'.join(unique_tags)}元素")
        if deleted_tags:
            unique_tags = list(set(deleted_tags))[:3]
            analysis.append(f"删除{'/'.join(unique_tags)}元素")
        
        template_type = "HTML模板"
        if filepath.endswith('.jsx'):
            template_type = "React组件"
        elif filepath.endswith('.tsx'):
            template_type = "React组件(TS)"
        elif filepath.endswith('.vue'):
            template_type = "Vue组件"
        
        return f"{template_type}: {' + '.join(analysis) if analysis else '模板调整'}"
    
    def _analyze_database_changes(self, filepath: str, added_lines: list, deleted_lines: list) -> str:
        """分析数据库文件变更"""
        analysis = []
        
        # 检测SQL语句
        sql_keywords = ['CREATE', 'ALTER', 'DROP', 'INSERT', 'UPDATE', 'DELETE', 'SELECT']
        
        for keyword in sql_keywords:
            added_count = sum(1 for line in added_lines if keyword.upper() in line.upper())
            if added_count > 0:
                analysis.append(f"{keyword}操作")
        
        return f"数据库文件: {' + '.join(analysis) if analysis else '数据变更'}"
    
    def _analyze_general_changes(self, filepath: str, added_lines: list, deleted_lines: list) -> str:
        """分析通用文件变更"""
        if len(added_lines) > len(deleted_lines) * 2:
            return f"文件: 大量新增内容"
        elif len(deleted_lines) > len(added_lines) * 2:
            return f"文件: 大量删除内容"
        elif len(added_lines) > 0 and len(deleted_lines) > 0:
            return f"文件: 内容修改"
        elif len(added_lines) > 0:
            return f"文件: 新增内容"
        else:
            return f"文件: 内容变更"
    
    def _format_changes_summary(self, file_changes: list) -> str:
        """格式化变更摘要为commit消息"""
        if not file_changes:
            return "文件更新"
        
        # 按文件类型分组
        blog_changes = []
        code_changes = []
        config_changes = []
        style_changes = []
        other_changes = []
        
        for change in file_changes:
            analysis = change['analysis']
            filepath = change['filepath']
            
            if 'source/_posts/' in filepath:
                blog_changes.append(analysis)
            elif any(ext in filepath for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']):
                code_changes.append(analysis)
            elif any(ext in filepath for ext in ['.yml', '.yaml', '.json', '.toml', '.ini']):
                config_changes.append(analysis)
            elif any(ext in filepath for ext in ['.css', '.scss', '.less', '.html', '.jsx', '.tsx', '.vue']):
                style_changes.append(analysis)
            else:
                other_changes.append(analysis)
        
        # 构建摘要
        summary_parts = []
        
        if blog_changes:
            summary_parts.append('; '.join(blog_changes[:2]))
        if code_changes:
            summary_parts.append('; '.join(code_changes[:2]))
        if config_changes:
            summary_parts.append('; '.join(config_changes[:2]))
        if style_changes:
            summary_parts.append('; '.join(style_changes[:2]))
        if other_changes:
            summary_parts.append('; '.join(other_changes[:2]))
        
        # 限制总长度
        result = ' | '.join(summary_parts)
        if len(result) > 200:
            result = result[:197] + "..."
        
        return result or "文件更新"

    def _get_simple_changes_summary(self) -> str:
        """简单的文件更改摘要（备用方案）"""
        changes_info = []

        # 获取修改的文件列表
        success, status_output = self._run_command("git status --porcelain")
        if success and status_output.strip():
            lines = status_output.strip().split('\n')

            for line in lines:
                if len(line) > 3:
                    status = line[:2].strip()
                    filepath = line[3:].strip()

                    # 清理文件路径：移除引号
                    if filepath.startswith('"') and filepath.endswith('"'):
                        filepath = filepath[1:-1]  # 移除首尾引号

                    # 分类文件类型
                    if filepath.endswith('.md'):
                        if 'source/_posts/' in filepath:
                            changes_info.append(f"博客文章: {os.path.basename(filepath)}")
                        else:
                            changes_info.append(f"Markdown文件: {os.path.basename(filepath)}")
                    elif filepath.endswith(('.yml', '.yaml')):
                        changes_info.append(f"配置文件: {os.path.basename(filepath)}")
                    elif filepath.endswith(('.js', '.css', '.html')):
                        changes_info.append(f"主题文件: {os.path.basename(filepath)}")
                    else:
                        changes_info.append(f"文件: {os.path.basename(filepath)}")

        return "; ".join(changes_info[:5])  # 最多显示5个文件



    def push_blog(self) -> bool:
        """推送博客到GitHub"""
        if not os.path.exists(self.main_blog_dir):
            self.console.print(f"[red]❌ 博客目录不存在: {self.main_blog_dir}[/red]")
            return False

        original_dir = os.getcwd()

        try:
            os.chdir(self.main_blog_dir)

            # 检查是否是Git仓库
            if not os.path.exists(".git"):
                self.console.print("[red]❌ 当前目录不是Git仓库[/red]")
                return False

            # 检查Git状态
            success, status_output = self._run_command("git status --porcelain")
            if not success:
                self.console.print("[red]❌ 无法获取Git状态[/red]")
                return False

            if not status_output.strip():
                # 无更改状态面板
                no_changes_panel = Panel(
                    "[bold white]📊 仓库状态检查[/bold white]\n\n"
                    "[green]✅ 状态:[/green] [bold green]仓库已是最新状态[/bold green]\n"
                    "[blue]🌐 远程:[/blue] [dim]已与 GitHub 同步[/dim]\n"
                    "[yellow]📋 变更:[/yellow] [dim]未检测到待处理的修改[/dim]",
                    title="[bold cyan]✨ 无需提交更改[/bold cyan]",
                    title_align="left",
                    border_style="cyan",
                    box=box.ROUNDED,
                    padding=(1, 2),
                    expand=True
                )
                self.console.print(no_changes_panel)
                return True

            # 显示将要提交的文件 - 专业表格格式
            success, short_status = self._run_command("git status --short")
            if success and short_status.strip():
                files_table = Table(
                    show_header=True,
                    header_style="bold white on blue",
                    box=box.ROUNDED,
                    title="[bold white]📋 待提交文件分析[/bold white]",
                    title_style="bold cyan",
                    border_style="bright_cyan",
                    padding=(0, 1),
                    expand=True
                )
                files_table.add_column("状态", style="bold yellow", width=10, justify="center")
                files_table.add_column("文件路径", style="bold white", min_width=40)
                files_table.add_column("类型", style="bold green", width=15, justify="center")
                files_table.add_column("操作", style="bold magenta", width=12, justify="center")
                
                status_lines = short_status.strip().split('\n')
                for line in status_lines:
                    if len(line) > 3:
                        status = line[:2].strip()
                        filepath = line[3:].strip()
                        
                        # 确定文件类型
                        if filepath.endswith('.md'):
                            if 'source/_posts/' in filepath:
                                file_type = "📝 Blog Post"
                            else:
                                file_type = "📄 Markdown"
                        elif filepath.endswith(('.yml', '.yaml')):
                            file_type = "⚙️ Config"
                        elif filepath.endswith(('.js', '.css', '.html')):
                            file_type = "🎨 Theme"
                        elif filepath.endswith(('.py', '.ts', '.jsx')):
                            file_type = "💻 Code"
                        elif filepath.endswith(('.jpg', '.png', '.gif', '.webp')):
                            file_type = "🖼️ Image"
                        else:
                            file_type = "📁 File"
                        
                        # 状态标识和操作
                        if 'M' in status:
                            status_icon = "🔄 已修改"
                            action = "更新"
                        elif 'A' in status:
                            status_icon = "➕ 已添加"
                            action = "创建"
                        elif 'D' in status:
                            status_icon = "➖ 已删除"
                            action = "删除"
                        elif 'R' in status:
                            status_icon = "🔀 已重命名"
                            action = "重命名"
                        else:
                            status_icon = f"❓ {status}"
                            action = "未知"
                        
                        files_table.add_row(status_icon, filepath, file_type, action)
                
                self.console.print(files_table)
                self.console.print()

            # 添加所有更改 - 带进度指示
            with Status("[blue]📦 正在暂存所有更改...[/blue]", console=self.console, spinner="dots"):
                success, _ = self._run_command("git add .")
                if not success:
                    self.console.print("[red]❌ 添加文件到暂存区失败[/red]")
                    return False
            
            self.console.print("[green]✓[/green] [bold]所有更改已成功暂存[/bold]")
            self.console.print()

            # 智能生成提交信息 - 专业分析面板
            with Status("[magenta]🤖 正在使用 AI 分析更改...[/magenta]", console=self.console, spinner="bouncingBar"):
                changes_summary = self._get_changes_summary()
                commit_msg = self._generate_commit_message(changes_summary)
            
            # AI 分析结果展示面板
            analysis_panel = Panel(
                f"[bold white]🔍 AI 分析结果[/bold white]\n\n"
                f"[cyan]📊 更改摘要:[/cyan]\n[dim white]{changes_summary}[/dim white]\n\n"
                f"[yellow]💬 生成的提交信息:[/yellow]\n[bold green]{commit_msg}[/bold green]",
                title="[bold magenta]🤖 智能提交分析[/bold magenta]",
                title_align="left",
                border_style="magenta",
                box=box.ROUNDED,
                padding=(1, 2),
                expand=True
            )
            self.console.print(analysis_panel)
            self.console.print()

            # 执行提交 - 带状态指示
            with Status("[yellow]💾 正在创建提交...[/yellow]", console=self.console, spinner="arc"):
                success, commit_output = self._run_command(f'git commit -m "{commit_msg}"')
                if not success:
                    self.console.print("[red]❌ 提交失败[/red]")
                    self.console.print(f"[dim red]错误信息: {commit_output}[/dim red]")
                    return False
            
            self.console.print("[green]✓[/green] [bold]提交创建成功[/bold]")
            self.console.print()

            # 推送到远程仓库 - 专业部署状态
            with Status("[blue]🚀 正在推送到 GitHub 仓库...[/blue]", console=self.console, spinner="bouncingBall"):
                success, push_output = self._run_command("git push origin main")

            if success:
                # 成功部署结果面板
                success_panel = Panel(
                    "[bold white]🎉 部署成功完成[/bold white]\n\n"
                    "[green]✅ 状态:[/green] [bold green]所有更改已推送到远程仓库[/bold green]\n"
                    "[blue]🌐 仓库地址:[/blue] [link=https://github.com/charrrrls/LeionWeb]https://github.com/charrrrls/LeionWeb[/link]\n"
                    "[magenta]🏷️  分支:[/magenta] [bold]main[/bold]\n"
                    f"[cyan]💬 提交信息:[/cyan] [dim]{commit_msg}[/dim]",
                    title="[bold green]🚀 部署成功[/bold green]",
                    title_align="left",
                    border_style="green",
                    box=box.DOUBLE,
                    padding=(1, 2),
                    expand=True
                )
                self.console.print(success_panel)
                return True
            else:
                # 失败部署结果面板
                error_panel = Panel(
                    "[bold white]❌ 部署失败[/bold white]\n\n"
                    "[red]✗ 状态:[/red] [bold red]推送到远程仓库失败[/bold red]\n"
                    "[yellow]🔧 建议:[/yellow] [dim]请检查网络连接和 Git 配置[/dim]\n\n"
                    f"[dim red]错误详情:[/dim red]\n[dim]{push_output}[/dim]",
                    title="[bold red]❌ 部署错误[/bold red]",
                    title_align="left",
                    border_style="red",
                    box=box.DOUBLE,
                    padding=(1, 2),
                    expand=True
                )
                self.console.print(error_panel)
                return False
                
        finally:
            os.chdir(original_dir)
            
    def serve_blog(self) -> bool:
        """启动博客本地服务器"""
        # 创建专业服务器标题
        start_time = create_leion_server_header(self.console)
        
        if not os.path.exists(self.blog_dir):
            self.console.print(f"[red]❌ 博客目录不存在: {self.blog_dir}[/red]")
            return False

        # 获取系统信息并显示配置
        sys_info = get_system_info()
        
        # 服务器配置信息树
        config_tree = Tree("🛠️ [bold blue]Server Configuration[/bold blue]")
        config_tree.add(f"[cyan]Blog Directory:[/cyan] [green]{self.blog_dir}[/green]")
        config_tree.add(f"[cyan]Posts Directory:[/cyan] [green]{self.posts_dir}[/green]")
        config_tree.add(f"[cyan]Server URL:[/cyan] [bright_blue]http://localhost:4000[/bright_blue]")
        config_tree.add(f"[cyan]Hot Reload:[/cyan] [bright_magenta]Enabled[/bright_magenta]")
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
        self.console.print(Rule("[bold blue]🚀 SERVER INITIALIZATION PIPELINE[/bold blue]", style="blue"))
        self.console.print()

        os.chdir(self.blog_dir)

        # 清理缓存阶段
        with Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task("[cyan]🧹 Cleaning cache...[/cyan]", total=None)
            success, _ = self._run_command("hexo clean")
            
            if success:
                self.console.print("[green]✅[/green] [bold green]Cache cleaned successfully[/bold green]")
            else:
                self.console.print("[yellow]⚠️[/yellow] [bold yellow]Cache cleanup failed, continuing...[/bold yellow]")

        self.console.print()
        
        # 服务器启动信息展示
        elapsed = datetime.now() - start_time
        elapsed_seconds = elapsed.total_seconds()
        
        self.console.print(Rule("[bold green]🌐 SERVER READY TO START[/bold green]", style="green"))
        self.console.print()
        
        # 服务器信息仪表板
        server_table = Table(
            show_header=True,
            header_style="bold white on blue",
            box=box.DOUBLE_EDGE,
            title="[bold white]🌐 BLOG SERVER DASHBOARD[/bold white]",
            title_style="bold green on black",
            border_style="bright_green",
            padding=(1, 2),
            expand=True
        )
        server_table.add_column("Service", style="bold cyan", width=20)
        server_table.add_column("Details", style="bold white")
        server_table.add_column("Status", style="bold green", width=15)
        
        server_table.add_row("🌍 Local Server", "http://localhost:4000", "🟢 READY")
        server_table.add_row("📁 Blog Path", self.blog_dir, "🟢 MOUNTED")
        server_table.add_row("🔄 Hot Reload", "File watcher enabled", "🟢 ACTIVE")
        server_table.add_row("⚡ Initialization", f"{elapsed_seconds:.2f}s", "🟢 FAST")
        server_table.add_row("🚀 Engine", "Hexo Static Generator", "🟢 OPTIMIZED")
        
        self.console.print(server_table)
        self.console.print()
        
        # 操作指南面板
        guide_panel = Panel(
            "[bold white]🎯 DEVELOPMENT SERVER STARTING[/bold white]\n\n"
            "[bright_green]✅ Server will be available at: http://localhost:4000[/bright_green]\n"
            "[bright_blue]🔄 Changes will auto-reload in real-time[/bright_blue]\n"
            "[bright_magenta]📝 Edit posts in source/_posts/ directory[/bright_magenta]\n\n"
            "[dim white]Press [bold]Ctrl+C[/bold] to gracefully stop the development server[/dim white]\n"
            "[dim cyan]Crafted with ❤️ by Leion • Professional Blog Development Suite[/dim cyan]",
            title="[bold yellow]🚀 LEION BLOG SERVER CONTROL CENTER[/bold yellow]",
            border_style="yellow",
            box=box.DOUBLE_EDGE,
            padding=(1, 2)
        )
        self.console.print(guide_panel)
        self.console.print()

        # 启动服务器（阻塞运行）
        try:
            self.console.print(Rule("[bold magenta]🎬 LAUNCHING HEXO SERVER[/bold magenta]", style="magenta"))
            self.console.print()
            subprocess.run("hexo server", shell=True, cwd=self.blog_dir)
            return True
        except KeyboardInterrupt:
            self.console.print()
            self.console.print(Rule("[bold yellow]🛑 Server Shutdown[/bold yellow]", style="yellow"))
            self.console.print()
            
            shutdown_panel = Panel(
                "[bold white]✨ Development server stopped gracefully[/bold white]\n"
                "[dim white]All connections have been terminated[/dim white]\n\n"
                "[bright_green]📊 Session completed successfully[/bright_green]\n"
                "[dim cyan]Thank you for using Leion's Professional Blog Server[/dim cyan]",
                title="[bold yellow]👋 Server Shutdown Complete[/bold yellow]",
                border_style="yellow",
                box=box.ROUNDED
            )
            self.console.print(Align.center(shutdown_panel))
            return True
        except Exception as e:
            self.console.print(f"[red]❌ 启动服务器失败: {e}[/red]")
            return False
            
    def generate_blog(self) -> bool:
        """生成静态博客文件"""
        if not os.path.exists(self.blog_dir):
            print_error(f"博客目录不存在: {self.blog_dir}")
            return False

        print_progress("生成静态博客文件...")
        os.chdir(self.blog_dir)

        # 清理并生成
        success, _ = self._run_command("hexo clean")
        if not success:
            print_warning("清理缓存失败，继续生成...")

        success, output = self._run_command("hexo generate")
        if success:
            print_success("博客生成成功！")
            return True
        else:
            print_error(f"生成失败: {output}")
            return False

    def _find_matching_file(self, partial_name: str) -> str:
        """智能匹配文件名 - 模糊搜索zh.md文件，多个匹配时选择最新的"""
        if not os.path.exists(self.posts_dir):
            return None
            
        # 获取所有-zh.md文件及其修改时间
        zh_files = []
        for file in os.listdir(self.posts_dir):
            if file.endswith('-zh.md'):
                file_path = os.path.join(self.posts_dir, file)
                try:
                    mtime = os.path.getmtime(file_path)
                    zh_files.append((file, mtime))
                except OSError:
                    # 如果无法获取修改时间，使用当前时间
                    import time
                    zh_files.append((file, time.time()))
        
        if not zh_files:
            return None
            
        # 清理搜索词
        clean_name = partial_name.lower().strip()
        
        # 1. 精确匹配（去掉-zh.md后缀）
        exact_matches = []
        for file, mtime in zh_files:
            file_name = file.replace('-zh.md', '').lower()
            if file_name == clean_name:
                exact_matches.append((file, mtime))
        
        if exact_matches:
            # 如果有精确匹配，按时间倒排选择最新的
            exact_matches.sort(key=lambda x: x[1], reverse=True)
            return os.path.join(self.posts_dir, exact_matches[0][0])
        
        # 2. 包含匹配
        partial_matches = []
        for file, mtime in zh_files:
            file_name = file.replace('-zh.md', '').lower()
            if clean_name in file_name or file_name in clean_name:
                similarity = self._calculate_similarity(clean_name, file_name)
                partial_matches.append((file, mtime, similarity))
        
        if partial_matches:
            # 先按相似度分组，相似度相同的按时间排序
            # 找出最高相似度
            max_similarity = max(match[2] for match in partial_matches)
            best_matches = [match for match in partial_matches if match[2] == max_similarity]
            
            # 如果有多个相同最高相似度的文件，选择最新的
            if len(best_matches) > 1:
                best_matches.sort(key=lambda x: x[1], reverse=True)  # 按时间倒排
                selected_file = best_matches[0][0]
                self.console.print(f"[dim cyan]🔍 发现 {len(best_matches)} 个相似匹配，已选择最新的: {selected_file}[/dim cyan]")
            else:
                selected_file = best_matches[0][0]
            
            return os.path.join(self.posts_dir, selected_file)
            
        return None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算字符串相似度"""
        # 简单的相似度计算
        common_chars = set(str1) & set(str2)
        total_chars = set(str1) | set(str2)
        return len(common_chars) / len(total_chars) if total_chars else 0
    
    def _analyze_content_changes(self, original: str, optimized: str) -> dict:
        """分析内容变化详情"""
        original_lines = original.split('\n')
        optimized_lines = optimized.split('\n')
        
        # 基础统计
        original_chars = len(original)
        optimized_chars = len(optimized)
        original_words = len(original.split())
        optimized_words = len(optimized.split())
        
        # 分析变化
        char_diff = optimized_chars - original_chars
        word_diff = optimized_words - original_words
        char_change_percent = (char_diff / original_chars * 100) if original_chars > 0 else 0
        
        # 内容结构分析
        original_headers = len([line for line in original_lines if line.strip().startswith('#')])
        optimized_headers = len([line for line in optimized_lines if line.strip().startswith('#')])
        
        original_code_blocks = original.count('```')
        optimized_code_blocks = optimized.count('```')
        
        original_links = original.count('[') + original.count('](')
        optimized_links = optimized.count('[') + optimized.count('](')
        
        # 段落分析
        original_paragraphs = len([line for line in original_lines if line.strip() and not line.startswith('#')])
        optimized_paragraphs = len([line for line in optimized_lines if line.strip() and not line.startswith('#')])
        
        return {
            'original_chars': original_chars,
            'optimized_chars': optimized_chars,
            'char_diff': char_diff,
            'char_change_percent': char_change_percent,
            'original_words': original_words,
            'optimized_words': optimized_words,
            'word_diff': word_diff,
            'original_headers': original_headers,
            'optimized_headers': optimized_headers,
            'header_diff': optimized_headers - original_headers,
            'original_code_blocks': original_code_blocks // 2,  # 除以2因为```成对出现
            'optimized_code_blocks': optimized_code_blocks // 2,
            'original_links': original_links // 2,
            'optimized_links': optimized_links // 2,
            'original_paragraphs': original_paragraphs,
            'optimized_paragraphs': optimized_paragraphs,
            'paragraph_diff': optimized_paragraphs - original_paragraphs
        }
    
    def _optimize_chinese_article(self, content: str) -> tuple[str, dict]:
        """使用AI优化中文文章，返回优化后的内容和统计信息"""
        start_time = datetime.now()
        
        try:
            # 提取front-matter和正文
            parts = content.split('---', 2)
            if len(parts) < 3:
                return content, {}
                
            front_matter = parts[1]
            article_content = parts[2]
            
            # 加载优化提示词模板
            optimize_template = self._load_prompt_template(self.optimizer_config)
            if not optimize_template:
                # 备用提示词
                optimize_template = """请优化以下中文技术博客文章，要求：
1. 保持原意和技术准确性
2. 优化语言表达，使其更流畅专业
3. 完善文章结构，补充必要的技术细节
4. 保持Markdown格式
5. 不要修改代码块
6. 适当添加技术深度和实用性

文章正文内容：
{article_content}

请直接返回优化后的文章正文内容。"""
            
            # 生成完整的优化提示词
            optimize_prompt = optimize_template.format(article_content=article_content)

            optimized_content = None
            
            if self.client:
                try:
                    optimized_content = self.client.generate(optimize_prompt, max_tokens=4000, temperature=0.7)
                    if not (optimized_content and optimized_content.strip()):
                        optimized_content = None
                except Exception as e:
                    self.console.print(f"[dim red]🔍 AI客户端优化失败: {e}[/dim red]")
                    optimized_content = None
            
            # 备用方案：使用ai_helper脚本
            if not optimized_content:
                success, optimized_content = self._run_command(
                    f'python3 "{self.ai_helper_script}" optimize "{self._clean_summary_for_command(optimize_prompt)}"'
                )
                if not (success and optimized_content and optimized_content.strip()):
                    optimized_content = None
            
            # 计算处理时间
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            if optimized_content:
                final_content = f"---{front_matter}---\n\n{optimized_content.strip()}"
                
                # 分析内容变化
                analysis = self._analyze_content_changes(article_content, optimized_content)
                analysis['processing_time'] = processing_time
                analysis['success'] = True
                
                return final_content, analysis
            else:
                return content, {'processing_time': processing_time, 'success': False}
                
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            self.console.print(f"[dim red]🔍 优化失败: {e}[/dim red]")
            return content, {'processing_time': processing_time, 'success': False, 'error': str(e)}
    
    def _analyze_translation_quality(self, chinese_content: str, english_content: str) -> dict:
        """分析翻译质量统计"""
        # 基础统计
        chinese_chars = len(chinese_content)
        english_chars = len(english_content)
        chinese_words = len(chinese_content.split())
        english_words = len(english_content.split())
        
        # 结构保持度分析
        chinese_headers = len([line for line in chinese_content.split('\n') if line.strip().startswith('#')])
        english_headers = len([line for line in english_content.split('\n') if line.strip().startswith('#')])
        
        chinese_code_blocks = chinese_content.count('```') // 2
        english_code_blocks = english_content.count('```') // 2
        
        chinese_links = chinese_content.count('](')
        english_links = english_content.count('](')
        
        # 段落统计
        chinese_paragraphs = len([line for line in chinese_content.split('\n') if line.strip() and not line.startswith('#')])
        english_paragraphs = len([line for line in english_content.split('\n') if line.strip() and not line.startswith('#')])
        
        # 计算比率
        char_ratio = english_chars / chinese_chars if chinese_chars > 0 else 0
        word_ratio = english_words / chinese_words if chinese_words > 0 else 0
        
        # 结构保持率
        structure_score = 0
        total_checks = 0
        
        if chinese_headers > 0:
            structure_score += min(english_headers / chinese_headers, 1.0)
            total_checks += 1
        if chinese_code_blocks > 0:
            structure_score += min(english_code_blocks / chinese_code_blocks, 1.0)
            total_checks += 1
        if chinese_links > 0:
            structure_score += min(english_links / chinese_links, 1.0)
            total_checks += 1
            
        structure_preservation = (structure_score / total_checks * 100) if total_checks > 0 else 100
        
        return {
            'chinese_chars': chinese_chars,
            'english_chars': english_chars,
            'chinese_words': chinese_words,
            'english_words': english_words,
            'char_ratio': char_ratio,
            'word_ratio': word_ratio,
            'chinese_headers': chinese_headers,
            'english_headers': english_headers,
            'chinese_code_blocks': chinese_code_blocks,
            'english_code_blocks': english_code_blocks,
            'chinese_links': chinese_links,
            'english_links': english_links,
            'chinese_paragraphs': chinese_paragraphs,
            'english_paragraphs': english_paragraphs,
            'structure_preservation': structure_preservation
        }

    def _translate_to_english(self, content: str, zh_filename: str) -> tuple[str, dict]:
        """翻译中文文章为英文，返回翻译内容和统计信息"""
        start_time = datetime.now()
        
        try:
            # 提取front-matter和正文
            parts = content.split('---', 2)
            if len(parts) < 3:
                return "", {'processing_time': 0, 'success': False, 'error': 'Invalid content format'}
                
            front_matter = parts[1]
            article_content = parts[2]
            
            # 提取原始front-matter中的各个字段
            import re
            title_match = re.search(r'title:\s*(.+)', front_matter)
            slug_match = re.search(r'slug:\s*(.+)', front_matter)
            author_match = re.search(r'author:\s*(.+)', front_matter)
            cover_match = re.search(r'cover:\s*(.+)', front_matter)
            tags_match = re.search(r'tags:\s*\n((?:\s*-\s*.+\n?)*)', front_matter)
            categories_match = re.search(r'categories:\s*\n((?:\s*-\s*.+\n?)*)', front_matter)
            password_match = re.search(r'password:\s*(.+)', front_matter)
            abbrlink_match = re.search(r'abbrlink:\s*(.+)', front_matter)
            date_match = re.search(r'date:\s*(.+)', front_matter)
            
            # 加载翻译提示词模板
            translate_template = self._load_prompt_template(self.translator_config)
            if not translate_template:
                # 备用提示词
                translate_template = """请将以下中文技术博客文章翻译为英文，要求：
1. 保持技术准确性和专业性
2. 使用地道的英文表达
3. 保持Markdown格式不变
4. 不要翻译代码块中的内容
5. 保持文章结构和段落布局
6. 使用技术写作的标准英文表达

原文章正文内容：
{article_content}

请直接返回翻译后的英文正文内容。"""
            
            # 生成完整的翻译提示词
            translate_prompt = translate_template.format(article_content=article_content)

            translated_content = None
            final_result = ""
            
            # 生成英文版本的front-matter
            def generate_english_title(chinese_title):
                # 简单的中英文映射
                mappings = {
                    '详解': 'Explained',
                    '指南': 'Guide', 
                    '教程': 'Tutorial',
                    '入门': 'Getting Started',
                    '实战': 'Practice',
                    '深入': 'Deep Dive',
                    '优化': 'Optimization',
                    '最佳实践': 'Best Practices',
                    '装饰器': 'Decorators',
                    '写文章': 'Writing Articles'
                }
                
                english_title = chinese_title
                for cn, en in mappings.items():
                    if cn in english_title:
                        english_title = english_title.replace(cn, en)
                
                return english_title
            
            def generate_english_slug(chinese_slug):
                # 保持slug的基本结构，如果已经是英文就不变
                if chinese_slug and all(ord(c) < 128 for c in chinese_slug.replace('-', '')):
                    return chinese_slug
                else:
                    # 简单转换
                    return chinese_slug.replace('hexo', 'hexo').replace('typora', 'typora')
            
            # 使用AI客户端进行翻译
            if self.client:
                try:
                    translated_content = self.client.generate(translate_prompt, max_tokens=4000, temperature=0.7)
                    if translated_content and translated_content.strip():
                        # 构建英文版本的front-matter
                        original_title = title_match.group(1).strip() if title_match else "Article"
                        english_title = generate_english_title(original_title)
                        original_slug = slug_match.group(1).strip() if slug_match else "article"
                        english_slug = generate_english_slug(original_slug)
                        
                        # 翻译标签 - 保持正确的YAML格式
                        original_tags = tags_match.group(1).strip() if tags_match else ""
                        if original_tags:
                            # 处理标签翻译，保持缩进
                            english_tags_lines = []
                            for line in original_tags.split('\n'):
                                if line.strip().startswith('- '):
                                    tag = line.strip()[2:].strip()
                                    # 翻译常见标签
                                    tag_translations = {
                                        '装饰器': 'Decorators',
                                        '后端开发': 'Backend Development', 
                                        '技术分享': 'Tech Sharing',
                                        '博客': 'Blog',
                                        '前端开发': 'Frontend Development',
                                        '数据库': 'Database',
                                        '算法': 'Algorithm'
                                    }
                                    translated_tag = tag_translations.get(tag, tag)
                                    english_tags_lines.append(f"  - {translated_tag}")
                            english_tags = '\n'.join(english_tags_lines)
                        else:
                            english_tags = "  - Tech"
                        
                        # 翻译分类 - 保持正确的YAML格式
                        original_categories = categories_match.group(1).strip() if categories_match else ""
                        if original_categories:
                            # 处理分类翻译，保持缩进
                            english_categories_lines = []
                            for line in original_categories.split('\n'):
                                if line.strip().startswith('- '):
                                    category = line.strip()[2:].strip()
                                    # 翻译常见分类
                                    category_translations = {
                                        'Python编程': 'Python Programming',
                                        '技术分享': 'Tech Sharing',
                                        '个人经历': 'Personal Experience',
                                        '前端技术': 'Frontend Tech',
                                        '后端技术': 'Backend Tech'
                                    }
                                    translated_category = category_translations.get(category, category)
                                    english_categories_lines.append(f"  - {translated_category}")
                            english_categories = '\n'.join(english_categories_lines)
                        else:
                            english_categories = "  - Tech Sharing"
                        
                        # 构建完整的英文front-matter，确保正确的YAML格式
                        english_front_matter = f"""title: {english_title}
slug: {english_slug}
author: {author_match.group(1).strip() if author_match else 'Leion Charrrrls'}
cover: {cover_match.group(1).strip() if cover_match else "''"}
tags:
{english_tags}
categories:
{english_categories}
password: {password_match.group(1).strip() if password_match else "''"}
abbrlink: {abbrlink_match.group(1).strip() if abbrlink_match else ''}
date: {date_match.group(1).strip() if date_match else ''}"""
                        
                        final_result = f"---\n{english_front_matter}\n---\n\n{translated_content.strip()}"
                except Exception as e:
                    self.console.print(f"[dim red]🔍 AI客户端翻译失败: {e}[/dim red]")
                    translated_content = None
                    
            # 备用方案：使用ai_helper脚本 
            if not final_result:
                success, translated_content = self._run_command(
                    f'python3 "{self.ai_helper_script}" translate "{self._clean_summary_for_command(translate_prompt)}"'
                )
                
                if success and translated_content and translated_content.strip():
                    # 构建简单的英文front-matter
                    original_title = title_match.group(1).strip() if title_match else "Article"
                    english_title = f"{original_title} (English Version)"
                    
                    # 保持原有的front-matter结构，只修改title
                    english_front_matter = front_matter.replace(original_title, english_title)
                    final_result = f"---{english_front_matter}---\n\n{translated_content.strip()}"
            
            # 计算处理时间
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            if final_result:
                # 提取翻译后的正文用于分析
                final_parts = final_result.split('---', 2)
                if len(final_parts) >= 3:
                    translated_article_content = final_parts[2]
                    
                    # 分析翻译质量
                    analysis = self._analyze_translation_quality(article_content, translated_article_content)
                    analysis['processing_time'] = processing_time
                    analysis['success'] = True
                    original_title = title_match.group(1).strip() if title_match else "Article"
                    analysis['original_title'] = original_title
                    
                    # 提取翻译后的标题
                    translated_title_match = re.search(r'title:\s*(.+)', final_parts[1])
                    analysis['translated_title'] = translated_title_match.group(1).strip() if translated_title_match else f"{original_title} (English)"
                    
                    return final_result, analysis
                else:
                    return final_result, {'processing_time': processing_time, 'success': True, 'basic_translation': True}
            else:
                return "", {'processing_time': processing_time, 'success': False}
                
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            self.console.print(f"[dim red]🔍 翻译失败: {e}[/dim red]")
            return "", {'processing_time': processing_time, 'success': False, 'error': str(e)}

    def optimize_blog_article(self, partial_title: str) -> bool:
        """优化中文博客文章"""
        # 创建专业优化标题
        start_time = datetime.now()
        
        # Leion 优化品牌标题
        header_text = Text()
        header_text.append("✨ ", style="bold magenta")
        header_text.append("LEION", style="bold white on blue")
        header_text.append(" ", style="")
        header_text.append("BLOG", style="bold white on green")
        header_text.append(" ", style="")
        header_text.append("OPTIMIZER", style="bold white on magenta")
        header_text.append(" 🚀", style="bold yellow")
        
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
        copyright_text.append("Professional Blog Optimization & Translation Suite", style="dim green")
        
        title_content = Text()
        title_content.append(header_text)
        title_content.append("\n")
        title_content.append(version_text)
        title_content.append("\n")
        title_content.append(copyright_text)
        
        title_panel = Panel(
            Align.center(title_content),
            box=box.DOUBLE_EDGE,
            style="bright_magenta",
            padding=(1, 3),
            title="[bold white]🎯 AI-Powered Blog Optimization Platform[/bold white]",
            subtitle="[dim cyan]Chinese Content Enhancement & Improvement[/dim cyan]",
            title_align="center"
        )
        
        self.console.clear()
        self.console.print(title_panel)
        self.console.print()
        
        if not partial_title:
            self.console.print("[red]❌ 请提供文章标题关键词[/red]")
            return False
            
        # 智能文件匹配阶段
        with Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task("[cyan]🔍 智能文件匹配中...[/cyan]", total=None)
            matched_file = self._find_matching_file(partial_title)
            
        if not matched_file:
            self.console.print(f"[red]❌ 未找到匹配的文章文件（搜索词：{partial_title}）[/red]")
            self.console.print("[yellow]💡 提示：请确保文件名以 '-zh.md' 结尾[/yellow]")
            return False
            
        self.console.print(f"[green]✅[/green] [bold green]找到匹配文件: {os.path.basename(matched_file)}[/bold green]")
        self.console.print()
        
        # 读取原文章内容
        try:
            with open(matched_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            self.console.print(f"[red]❌ 读取文件失败: {e}[/red]")
            return False
            
        # AI优化中文版本
        with Progress(
            SpinnerColumn(style="magenta"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),  
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task("[magenta]🤖 AI优化中文内容...[/magenta]", total=None)
            optimized_content, optimize_stats = self._optimize_chinese_article(original_content)
        
        # 显示中文优化详细统计
        if optimize_stats.get('success'):
            self.console.print()
            self.console.print(Rule("[bold magenta]📊 中文优化详细分析[/bold magenta]", style="magenta"))
            self.console.print()
            
            # 优化统计表格
            optimize_table = Table(
                show_header=True,
                header_style="bold white on magenta",
                box=box.ROUNDED,
                title="[bold white]✨ AI 内容优化报告[/bold white]",
                title_style="bold magenta",
                border_style="bright_magenta",
                padding=(0, 1),
                expand=True
            )
            optimize_table.add_column("指标", style="bold cyan", width=18)
            optimize_table.add_column("优化前", style="bold yellow", width=12, justify="right")
            optimize_table.add_column("优化后", style="bold green", width=12, justify="right") 
            optimize_table.add_column("变化", style="bold white", width=15, justify="center")
            optimize_table.add_column("说明", style="dim white", min_width=20)
            
            # 字符统计
            char_change = optimize_stats['char_diff']
            char_icon = "📈" if char_change > 0 else "📉" if char_change < 0 else "➖"
            char_color = "green" if char_change > 0 else "red" if char_change < 0 else "yellow"
            optimize_table.add_row(
                "📝 文章字数",
                f"{optimize_stats['original_chars']:,}",
                f"{optimize_stats['optimized_chars']:,}",
                f"[{char_color}]{char_icon} {char_change:+,}[/{char_color}]",
                f"变化 {optimize_stats['char_change_percent']:+.1f}%"
            )
            
            # 词数统计
            word_change = optimize_stats['word_diff']
            word_icon = "📈" if word_change > 0 else "📉" if word_change < 0 else "➖"
            word_color = "green" if word_change > 0 else "red" if word_change < 0 else "yellow"
            optimize_table.add_row(
                "🔤 词汇数量",
                f"{optimize_stats['original_words']:,}",
                f"{optimize_stats['optimized_words']:,}",
                f"[{word_color}]{word_icon} {word_change:+,}[/{word_color}]",
                "词汇丰富度分析"
            )
            
            # 标题结构
            header_change = optimize_stats['header_diff']
            header_icon = "📈" if header_change > 0 else "📉" if header_change < 0 else "➖"
            header_color = "green" if header_change > 0 else "red" if header_change < 0 else "yellow"
            optimize_table.add_row(
                "📑 章节标题",
                f"{optimize_stats['original_headers']}",
                f"{optimize_stats['optimized_headers']}",
                f"[{header_color}]{header_icon} {header_change:+}[/{header_color}]",
                "文章结构优化"
            )
            
            # 段落统计
            para_change = optimize_stats['paragraph_diff']
            para_icon = "📈" if para_change > 0 else "📉" if para_change < 0 else "➖"
            para_color = "green" if para_change > 0 else "red" if para_change < 0 else "yellow"
            optimize_table.add_row(
                "📄 段落数量",
                f"{optimize_stats['original_paragraphs']}",
                f"{optimize_stats['optimized_paragraphs']}",
                f"[{para_color}]{para_icon} {para_change:+}[/{para_color}]",
                "内容组织结构"
            )
            
            # 处理性能
            processing_speed = optimize_stats['original_chars'] / optimize_stats['processing_time'] if optimize_stats['processing_time'] > 0 else 0
            optimize_table.add_row(
                "⚡ 处理性能",
                f"{optimize_stats['processing_time']:.2f}s",
                f"{processing_speed:.0f} 字/秒",
                "[bright_green]🚀 高效[/bright_green]",
                "AI 优化处理速度"
            )
            
            self.console.print(optimize_table)
            self.console.print()
            
        # 保存优化后的中文版本
        try:
            with open(matched_file, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
            
            if optimize_stats.get('success'):
                self.console.print(f"[green]✅[/green] [bold green]中文版本优化完成 - 内容增强 {optimize_stats['char_change_percent']:+.1f}%[/bold green]")
            else:
                self.console.print("[yellow]⚠️[/yellow] [bold yellow]中文版本保存完成（优化可能失败）[/bold yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ 保存优化版本失败: {e}[/red]")
            return False
            
        self.console.print()
            
        # 成功完成展示
        elapsed = datetime.now() - start_time
        elapsed_seconds = elapsed.total_seconds()
        
        self.console.print()
        self.console.print(Rule("[bold green]🎉 中文博客优化完成[/bold green]", style="green"))
        self.console.print()
        
        # 综合结果仪表板
        result_table = Table(
            show_header=True,
            header_style="bold white on green", 
            box=box.DOUBLE_EDGE,
            title="[bold white]🏆 优化任务执行报告[/bold white]",
            title_style="bold green on black",
            border_style="bright_green",
            padding=(1, 2),
            expand=True
        )
        result_table.add_column("任务阶段", style="bold cyan", width=18)
        result_table.add_column("文件名", style="bold white", min_width=25)
        result_table.add_column("处理结果", style="bold green", width=12, justify="center")
        result_table.add_column("性能指标", style="bold yellow", width=15, justify="center")
        result_table.add_column("质量评估", style="dim white", min_width=20)
        
        # 文件匹配阶段
        result_table.add_row(
            "🔍 智能匹配",
            os.path.basename(matched_file),
            "🟢 成功",
            "< 0.1s",
            "精准文件定位"
        )
        
        # 中文优化阶段
        if optimize_stats.get('success'):
            opt_performance = f"{optimize_stats['processing_time']:.1f}s"
            opt_quality = f"内容增强 {optimize_stats['char_change_percent']:+.1f}%"
            result_table.add_row(
                "✨ 中文优化",
                os.path.basename(matched_file),
                "🟢 优化",
                opt_performance,
                opt_quality
            )
        else:
            result_table.add_row(
                "✨ 中文优化",
                os.path.basename(matched_file),
                "🟡 保持",
                "N/A",
                "保持原内容"
            )
        
        # 总体性能
        total_chars = optimize_stats.get('original_chars', 0)
        overall_speed = total_chars / elapsed_seconds if elapsed_seconds > 0 and total_chars > 0 else 0
        result_table.add_row(
            "⚡ 整体性能",
            f"处理 {total_chars:,} 字符",
            "🚀 高效",
            f"{elapsed_seconds:.2f}s",
            f"平均 {overall_speed:.0f} 字/秒"
        )
        
        self.console.print(result_table)
        self.console.print()
        
        # 详细成果统计面板
        content_summary = []
        
        if optimize_stats.get('success'):
            content_summary.append(f"✨ 中文内容优化：{optimize_stats['char_change_percent']:+.1f}% 字符变化")
            content_summary.append(f"📑 章节结构：{optimize_stats.get('original_headers', 0)}→{optimize_stats.get('optimized_headers', 0)} 个标题")
            content_summary.append(f"📄 段落扩充：{optimize_stats.get('original_paragraphs', 0)}→{optimize_stats.get('optimized_paragraphs', 0)} 个段落")
            
        final_panel = Panel(
            f"[bold white]🎯 中文博客优化任务完成[/bold white]\n\n"
            f"[bright_green]📁 处理文件：{os.path.basename(matched_file)}[/bright_green]\n"
            f"[bright_blue]📂 文件位置：{self.posts_dir}[/bright_blue]\n"
            f"[bright_magenta]⏱️  总处理时间：{elapsed_seconds:.2f} 秒[/bright_magenta]\n\n"
            f"[bold cyan]📊 优化成果摘要：[/bold cyan]\n" +
            '\n'.join([f"   {summary}" for summary in content_summary]) + "\n\n" +
            "[dim white]您的中文博客文章已优化完成，内容更加专业详实！[/dim white]\n"
            "[dim yellow]💡 提示：使用 'btr \"关键词\"' 可以将优化后的文章翻译为英文[/dim yellow]\n"
            "[dim cyan]Crafted with ❤️ by Leion • Professional AI Blog Solutions[/dim cyan]",
            title="[bold yellow]🚀 LEION 博客优化器 - 任务完成[/bold yellow]",
            border_style="yellow",
            box=box.DOUBLE_EDGE,
            padding=(1, 2)
        )
        
        self.console.print(final_panel)
        self.console.print()
        
        return True

    def translate_blog_article(self, partial_title: str) -> bool:
        """翻译中文博客文章为英文版本"""
        # 创建专业翻译标题
        start_time = datetime.now()
        
        # Leion 翻译品牌标题
        header_text = Text()
        header_text.append("🌐 ", style="bold blue")
        header_text.append("LEION", style="bold white on blue")
        header_text.append(" ", style="")
        header_text.append("BLOG", style="bold white on green")
        header_text.append(" ", style="")
        header_text.append("TRANSLATOR", style="bold white on blue")
        header_text.append(" 🚀", style="bold yellow")
        
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
        copyright_text.append("Professional Blog Translation & Localization Suite", style="dim green")
        
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
            title="[bold white]🎯 AI-Powered Blog Translation Platform[/bold white]",
            subtitle="[dim cyan]Chinese to English Professional Translation[/dim cyan]",
            title_align="center"
        )
        
        self.console.clear()
        self.console.print(title_panel)
        self.console.print()
        
        if not partial_title:
            self.console.print("[red]❌ 请提供文章标题关键词[/red]")
            return False
            
        # 智能文件匹配阶段
        with Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task("[cyan]🔍 智能文件匹配中...[/cyan]", total=None)
            matched_file = self._find_matching_file(partial_title)
            
        if not matched_file:
            self.console.print(f"[red]❌ 未找到匹配的文章文件（搜索词：{partial_title}）[/red]")
            self.console.print("[yellow]💡 提示：请确保文件名以 '-zh.md' 结尾[/yellow]")
            return False
            
        self.console.print(f"[green]✅[/green] [bold green]找到匹配文件: {os.path.basename(matched_file)}[/bold green]")
        self.console.print()
        
        # 读取原文章内容
        try:
            with open(matched_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            self.console.print(f"[red]❌ 读取文件失败: {e}[/red]")
            return False
        
        # AI翻译英文版本
        with Progress(
            SpinnerColumn(style="blue"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task("[blue]🌐 AI翻译英文版本...[/blue]", total=None)
            english_content, translate_stats = self._translate_to_english(original_content, os.path.basename(matched_file))
        
        # 显示翻译详细统计
        if translate_stats.get('success') and english_content:
            self.console.print()
            self.console.print(Rule("[bold blue]🌍 英文翻译质量分析[/bold blue]", style="blue"))
            self.console.print()
            
            # 翻译统计表格
            translate_table = Table(
                show_header=True,
                header_style="bold white on blue",
                box=box.ROUNDED,
                title="[bold white]🌐 AI 翻译质量报告[/bold white]",
                title_style="bold blue",
                border_style="bright_blue",
                padding=(0, 1),
                expand=True
            )
            translate_table.add_column("指标", style="bold cyan", width=18)
            translate_table.add_column("中文原文", style="bold yellow", width=12, justify="right")
            translate_table.add_column("英文译文", style="bold green", width=12, justify="right")
            translate_table.add_column("比率", style="bold white", width=12, justify="center")
            translate_table.add_column("质量评估", style="dim white", min_width=20)
            
            # 标题信息
            if 'original_title' in translate_stats and 'translated_title' in translate_stats:
                translate_table.add_row(
                    "📰 文章标题",
                    f"{translate_stats['original_title'][:15]}...",
                    f"{translate_stats['translated_title'][:15]}...",
                    "[bright_green]✓[/bright_green]",
                    "标题专业翻译"
                )
            
            # 字符对比
            char_ratio = translate_stats['char_ratio']
            char_quality = "优秀" if 1.2 <= char_ratio <= 2.0 else "良好" if 0.8 <= char_ratio < 1.2 or 2.0 < char_ratio <= 2.5 else "一般"
            char_color = "bright_green" if char_quality == "优秀" else "green" if char_quality == "良好" else "yellow"
            translate_table.add_row(
                "📝 字符数量",
                f"{translate_stats['chinese_chars']:,}",
                f"{translate_stats['english_chars']:,}",
                f"{char_ratio:.2f}x",
                f"[{char_color}]{char_quality}[/{char_color}] 翻译比例"
            )
            
            # 词汇对比
            word_ratio = translate_stats['word_ratio']
            word_quality = "优秀" if 0.7 <= word_ratio <= 1.3 else "良好" if 0.5 <= word_ratio < 0.7 or 1.3 < word_ratio <= 1.8 else "一般"
            word_color = "bright_green" if word_quality == "优秀" else "green" if word_quality == "良好" else "yellow"
            translate_table.add_row(
                "🔤 词汇数量",
                f"{translate_stats['chinese_words']:,}",
                f"{translate_stats['english_words']:,}",
                f"{word_ratio:.2f}x",
                f"[{word_color}]{word_quality}[/{word_color}] 词汇密度"
            )
            
            # 结构保持
            structure_percent = translate_stats['structure_preservation']
            structure_quality = "优秀" if structure_percent >= 95 else "良好" if structure_percent >= 85 else "一般"
            structure_color = "bright_green" if structure_quality == "优秀" else "green" if structure_quality == "良好" else "yellow"
            translate_table.add_row(
                "🏗️ 结构保持",
                f"{translate_stats['chinese_headers']} 标题",
                f"{translate_stats['english_headers']} 标题",
                f"{structure_percent:.1f}%",
                f"[{structure_color}]{structure_quality}[/{structure_color}] 结构完整性"
            )
            
            # 技术内容保持
            code_preserved = translate_stats['chinese_code_blocks'] == translate_stats['english_code_blocks']
            link_preserved = abs(translate_stats['chinese_links'] - translate_stats['english_links']) <= 1
            tech_quality = "优秀" if code_preserved and link_preserved else "良好" if code_preserved or link_preserved else "一般"
            tech_color = "bright_green" if tech_quality == "优秀" else "green" if tech_quality == "良好" else "yellow"
            translate_table.add_row(
                "💻 技术内容",
                f"{translate_stats['chinese_code_blocks']} 代码块",
                f"{translate_stats['english_code_blocks']} 代码块",
                "[bright_green]✓[/bright_green]" if code_preserved else "[yellow]~[/yellow]",
                f"[{tech_color}]{tech_quality}[/{tech_color}] 技术准确性"
            )
            
            # 翻译性能
            translation_speed = translate_stats['chinese_chars'] / translate_stats['processing_time'] if translate_stats['processing_time'] > 0 else 0
            translate_table.add_row(
                "⚡ 翻译性能",
                f"{translate_stats['processing_time']:.2f}s",
                f"{translation_speed:.0f} 字/秒",
                "[bright_green]🚀 高效[/bright_green]",
                "AI 翻译处理速度"
            )
            
            self.console.print(translate_table)
            self.console.print()
            
            # 生成英文文件路径
            en_filename = os.path.basename(matched_file).replace('-zh.md', '-en.md')
            en_filepath = os.path.join(self.posts_dir, en_filename)
            
            try:
                with open(en_filepath, 'w', encoding='utf-8') as f:
                    f.write(english_content)
                self.console.print(f"[green]✅[/green] [bold green]英文版本生成完成 - 翻译质量 {structure_quality}，字符比例 {char_ratio:.2f}x[/bold green]")
            except Exception as e:
                self.console.print(f"[red]❌ 保存英文版本失败: {e}[/red]")
                return False
        else:
            self.console.print("[yellow]⚠️[/yellow] [bold yellow]英文翻译失败[/bold yellow]")
            if 'error' in translate_stats:
                self.console.print(f"[dim red]错误详情: {translate_stats['error']}[/dim red]")
            return False
            
        # 成功完成展示
        elapsed = datetime.now() - start_time
        elapsed_seconds = elapsed.total_seconds()
        
        self.console.print()
        self.console.print(Rule("[bold blue]🎉 英文翻译完成[/bold blue]", style="blue"))
        self.console.print()
        
        # 最终成果面板
        en_filename = os.path.basename(matched_file).replace('-zh.md', '-en.md')
        
        final_panel = Panel(
            f"[bold white]🎯 英文翻译任务完成[/bold white]\n\n"
            f"[bright_green]📁 源文件：{os.path.basename(matched_file)}[/bright_green]\n"
            f"[bright_blue]📁 译文：{en_filename}[/bright_blue]\n"
            f"[bright_magenta]⏱️  翻译时间：{elapsed_seconds:.2f} 秒[/bright_magenta]\n\n"
            f"[bold cyan]📊 翻译成果：[/bold cyan]\n"
            f"   🌐 翻译质量：{structure_quality}级别\n"
            f"   📝 字符比例：{char_ratio:.2f}x (中→英)\n"
            f"   🏗️ 结构保持：{structure_percent:.1f}%\n\n"
            "[dim white]您的英文博客文章已准备就绪，可以发布到国际平台！[/dim white]\n"
            "[dim cyan]Crafted with ❤️ by Leion • Professional AI Blog Solutions[/dim cyan]",
            title="[bold yellow]🚀 LEION 博客翻译器 - 任务完成[/bold yellow]",
            border_style="yellow",
            box=box.DOUBLE_EDGE,
            padding=(1, 2)
        )
        
        self.console.print(final_panel)
        self.console.print()
        
        return True


def main():
    parser = argparse.ArgumentParser(description="博客管理工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # new命令
    new_parser = subparsers.add_parser('new', help='创建新文章')
    new_parser.add_argument('title', help='文章标题')
    
    # push命令
    push_parser = subparsers.add_parser('push', help='推送博客到GitHub')
    
    # serve命令
    serve_parser = subparsers.add_parser('serve', help='启动本地服务器')
    
    # generate命令
    gen_parser = subparsers.add_parser('generate', help='生成静态文件')
    
    # optimize命令 - bop功能
    optimize_parser = subparsers.add_parser('optimize', help='优化中文文章')
    optimize_parser.add_argument('title', help='文章标题关键词（用于匹配现有文章）')
    
    # translate命令 - btr功能
    translate_parser = subparsers.add_parser('translate', help='翻译中文文章为英文')
    translate_parser.add_argument('title', help='文章标题关键词（用于匹配现有文章）')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    blog = BlogManager()
    
    success = False
    if args.command == 'new':
        success = blog.new_article(args.title)
    elif args.command == 'push':
        success = blog.push_blog()
    elif args.command == 'serve':
        success = blog.serve_blog()
    elif args.command == 'generate':
        success = blog.generate_blog()
    elif args.command == 'optimize':
        success = blog.optimize_blog_article(args.title)
    elif args.command == 'translate':
        success = blog.translate_blog_article(args.title)
        
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()