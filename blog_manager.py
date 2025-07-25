#!/usr/bin/env python3
"""
博客管理脚本 - by 阮阮
提供博客创建、推送、服务等功能
"""

import os
import sys
import subprocess
import re
import argparse
from datetime import datetime
from pathlib import Path
from color_utils import print_error, print_success, print_warning, print_info, print_progress, colored_print, MessageType


class BlogManager:
    def __init__(self):
        self.blog_dir = "/Users/leion/Charles/LeionWeb/blog"
        self.posts_dir = f"{self.blog_dir}/source/_posts"
        self.main_blog_dir = "/Users/leion/Charles/LeionWeb"
        self.ai_helper_script = "/Users/leion/scripts/ai_helper.py"
        
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
                commit_msg = commit_msg.strip('"\'')

                # 确保commit信息不为空且合理
                if len(commit_msg) > 10 and len(commit_msg) < 100:
                    return commit_msg

        except Exception as e:
            print_warning(f"AI生成commit信息失败: {e}")

        # 备用方案：基于时间的默认信息
        return f"Update blog content: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

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

        # 获取文件统计信息
        success, stat_output = self._run_command("git diff --cached --stat")
        if not success:
            return self._get_simple_changes_summary()

        # 获取详细diff内容
        success, diff_output = self._run_command("git diff --cached")
        if not success:
            return self._get_simple_changes_summary()

        # 解析每个文件的更改
        files_info = self._parse_diff_output(diff_output, stat_output)

        for file_info in files_info[:3]:  # 最多分析3个文件
            summary = self._generate_file_summary(file_info)
            if summary:
                changes_info.append(summary)

        if len(files_info) > 3:
            changes_info.append(f"等{len(files_info)}个文件")

        return "; ".join(changes_info) if changes_info else "文件更改"

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

    def _parse_diff_output(self, diff_output: str, stat_output: str) -> list:
        """解析git diff输出，提取文件更改信息"""
        files_info = []

        # 解析统计信息
        stat_lines = stat_output.strip().split('\n')
        file_stats = {}

        for line in stat_lines:
            if '|' in line and ('+' in line or '-' in line):
                parts = line.split('|')
                if len(parts) >= 2:
                    filename = parts[0].strip()
                    stats_part = parts[1].strip()

                    # 提取添加和删除的行数
                    additions = stats_part.count('+')
                    deletions = stats_part.count('-')

                    file_stats[filename] = {
                        'additions': additions,
                        'deletions': deletions
                    }

        # 解析详细diff内容
        current_file = None
        added_lines = []
        deleted_lines = []

        for line in diff_output.split('\n'):
            if line.startswith('diff --git'):
                # 保存上一个文件的信息
                if current_file:
                    files_info.append({
                        'filename': current_file,
                        'stats': file_stats.get(current_file, {'additions': 0, 'deletions': 0}),
                        'added_lines': added_lines[:10],  # 最多保留10行
                        'deleted_lines': deleted_lines[:10]
                    })

                # 开始新文件
                parts = line.split(' ')
                if len(parts) >= 4:
                    current_file = parts[3].replace('b/', '')
                added_lines = []
                deleted_lines = []

            elif line.startswith('+') and not line.startswith('+++'):
                added_lines.append(line[1:].strip())
            elif line.startswith('-') and not line.startswith('---'):
                deleted_lines.append(line[1:].strip())

        # 保存最后一个文件的信息
        if current_file:
            files_info.append({
                'filename': current_file,
                'stats': file_stats.get(current_file, {'additions': 0, 'deletions': 0}),
                'added_lines': added_lines[:10],
                'deleted_lines': deleted_lines[:10]
            })

        return files_info

    def _generate_file_summary(self, file_info: dict) -> str:
        """为单个文件生成详细摘要"""
        filename = file_info['filename']
        stats = file_info['stats']
        added_lines = file_info['added_lines']
        deleted_lines = file_info['deleted_lines']

        # 基础文件信息
        basename = os.path.basename(filename)
        file_type = self._get_file_type(filename)

        # 统计信息
        additions = stats['additions']
        deletions = stats['deletions']

        # 生成统计描述
        change_desc = []
        if additions > 0:
            change_desc.append(f"+{additions}行")
        if deletions > 0:
            change_desc.append(f"-{deletions}行")

        stats_str = f"({', '.join(change_desc)})" if change_desc else ""

        # 内容分析
        content_analysis = self._analyze_file_content(filename, added_lines, deleted_lines)

        # 组合摘要
        if content_analysis:
            return f"{file_type}: {basename} {stats_str} - {content_analysis}"
        else:
            return f"{file_type}: {basename} {stats_str}"

    def _get_file_type(self, filename: str) -> str:
        """获取文件类型描述"""
        if filename.endswith('.md'):
            if 'source/_posts/' in filename:
                return "博客文章"
            else:
                return "Markdown文档"
        elif filename.endswith(('.yml', '.yaml')):
            return "配置文件"
        elif filename.endswith(('.js', '.css', '.html')):
            return "主题文件"
        elif filename.endswith(('.py', '.java', '.cpp', '.c')):
            return "代码文件"
        elif filename.endswith(('.json', '.xml')):
            return "数据文件"
        else:
            return "文件"

    def _analyze_file_content(self, filename: str, added_lines: list, deleted_lines: list) -> str:
        """分析文件内容变化"""
        if filename.endswith('.md'):
            return self._analyze_markdown_content(added_lines, deleted_lines)
        elif filename.endswith(('.yml', '.yaml')):
            return self._analyze_config_content(added_lines, deleted_lines)
        elif filename.endswith(('.py', '.js', '.java')):
            return self._analyze_code_content(added_lines, deleted_lines)
        else:
            return self._analyze_general_content(added_lines, deleted_lines)

    def _analyze_markdown_content(self, added_lines: list, deleted_lines: list) -> str:
        """分析Markdown文件内容变化"""
        analysis = []

        # 分析添加的内容
        added_headers = [line for line in added_lines if line.startswith('#')]
        added_links = [line for line in added_lines if '[' in line and '](' in line]
        added_code = [line for line in added_lines if line.startswith('```') or line.startswith('    ')]

        # 分析删除的内容
        deleted_headers = [line for line in deleted_lines if line.startswith('#')]

        if added_headers:
            headers = [h.strip('#').strip() for h in added_headers[:2]]
            analysis.append(f"新增章节: {', '.join(headers)}")

        if deleted_headers:
            headers = [h.strip('#').strip() for h in deleted_headers[:2]]
            analysis.append(f"删除章节: {', '.join(headers)}")

        if added_links:
            analysis.append(f"添加{len(added_links)}个链接")

        if added_code:
            analysis.append("添加代码示例")

        # 分析一般内容
        if not analysis:
            if len(added_lines) > len(deleted_lines):
                analysis.append("补充内容")
            elif len(deleted_lines) > len(added_lines):
                analysis.append("删减内容")
            else:
                analysis.append("修改内容")

        return ", ".join(analysis[:3])

    def _analyze_config_content(self, added_lines: list, deleted_lines: list) -> str:
        """分析配置文件内容变化"""
        analysis = []

        # 查找配置项变化，更智能地处理复杂配置
        added_configs = []
        deleted_configs = []

        for line in added_lines:
            if ':' in line and not line.strip().startswith('#'):
                config_key = line.split(':')[0].strip()
                # 清理配置键名，移除特殊字符
                config_key = config_key.replace('-', '').replace('_', '')
                if config_key and len(config_key) < 30:  # 避免过长的键名
                    added_configs.append(config_key)

        for line in deleted_lines:
            if ':' in line and not line.strip().startswith('#'):
                config_key = line.split(':')[0].strip()
                config_key = config_key.replace('-', '').replace('_', '')
                if config_key and len(config_key) < 30:
                    deleted_configs.append(config_key)

        if added_configs:
            # 只显示前2个配置项，避免过长
            configs_str = ', '.join(added_configs[:2])
            analysis.append(f"新增配置项: {configs_str}")

        if deleted_configs:
            configs_str = ', '.join(deleted_configs[:2])
            analysis.append(f"删除配置项: {configs_str}")

        if not analysis:
            if len(added_lines) > len(deleted_lines):
                analysis.append("新增配置内容")
            elif len(deleted_lines) > len(added_lines):
                analysis.append("删除配置内容")
            else:
                analysis.append("修改配置")

        return ", ".join(analysis[:2])

    def _analyze_code_content(self, added_lines: list, deleted_lines: list) -> str:
        """分析代码文件内容变化"""
        analysis = []

        # 查找函数定义
        added_functions = [line.strip() for line in added_lines if 'def ' in line or 'function ' in line]
        deleted_functions = [line.strip() for line in deleted_lines if 'def ' in line or 'function ' in line]

        # 查找导入语句
        added_imports = [line.strip() for line in added_lines if line.strip().startswith(('import ', 'from '))]

        if added_functions:
            analysis.append(f"新增函数: {len(added_functions)}个")

        if deleted_functions:
            analysis.append(f"删除函数: {len(deleted_functions)}个")

        if added_imports:
            analysis.append(f"新增导入: {len(added_imports)}个")

        if not analysis:
            if len(added_lines) > len(deleted_lines):
                analysis.append("增加代码")
            else:
                analysis.append("修改代码")

        return ", ".join(analysis[:2])

    def _analyze_general_content(self, added_lines: list, deleted_lines: list) -> str:
        """分析一般文件内容变化"""
        if len(added_lines) > len(deleted_lines) * 2:
            return "大量新增内容"
        elif len(deleted_lines) > len(added_lines) * 2:
            return "大量删除内容"
        elif len(added_lines) > 0 and len(deleted_lines) > 0:
            return "修改内容"
        elif len(added_lines) > 0:
            return "新增内容"
        elif len(deleted_lines) > 0:
            return "删除内容"
        else:
            return "文件变化"

    def push_blog(self) -> bool:
        """推送博客到GitHub"""
        print_info("切换到博客主目录...")

        if not os.path.exists(self.main_blog_dir):
            print_error(f"博客目录不存在: {self.main_blog_dir}")
            return False

        original_dir = os.getcwd()

        try:
            os.chdir(self.main_blog_dir)

            # 检查是否是Git仓库
            if not os.path.exists(".git"):
                print_error("当前目录不是Git仓库")
                return False

            # 检查Git状态
            success, status_output = self._run_command("git status --porcelain")
            if not success:
                print_error("无法获取Git状态")
                return False

            if not status_output.strip():
                print_success("没有新的更改需要提交")
                return True
                
            # 显示将要提交的文件
            print_info("将要提交的文件：")
            success, short_status = self._run_command("git status --short")
            if success:
                colored_print(short_status, MessageType.NORMAL)

            # 添加所有更改
            print_progress("添加所有更改到暂存区...")
            success, _ = self._run_command("git add .")
            if not success:
                print_error("添加文件到暂存区失败")
                return False

            # 智能生成提交信息
            print_progress("正在分析更改")
            changes_summary = self._get_changes_summary()
            # 打印更改信息
            colored_print(changes_summary, MessageType.NORMAL)
            print_progress("开始生成commit信息...")
            commit_msg = self._generate_commit_message(changes_summary)

            print_info(f"提交信息: {commit_msg}")
            
            success, _ = self._run_command(f'git commit -m "{commit_msg}"')
            if not success:
                print_error("提交失败")
                return False

            # 推送到远程仓库
            print_progress("推送到GitHub...")
            success, push_output = self._run_command("git push origin main")

            if success:
                print_success("推送成功！")
                print_info("仓库地址: https://github.com/charrrrls/LeionWeb")
                print_info(f"本次提交: {commit_msg}")
                return True
            else:
                print_error("推送失败！请检查网络连接和Git配置")
                print_error(f"错误信息: {push_output}")
                return False
                
        finally:
            os.chdir(original_dir)
            
    def serve_blog(self) -> bool:
        """启动博客本地服务器"""
        if not os.path.exists(self.blog_dir):
            print_error(f"博客目录不存在: {self.blog_dir}")
            return False

        print_progress("启动本地博客服务器...")
        os.chdir(self.blog_dir)

        # 清理并启动服务器
        success, _ = self._run_command("hexo clean")
        if not success:
            print_warning("清理缓存失败，继续启动服务器...")

        print_info("正在启动服务器，访问 http://localhost:4000")
        print_info("按 Ctrl+C 停止服务器")

        # 启动服务器（阻塞运行）
        try:
            subprocess.run("hexo server", shell=True, cwd=self.blog_dir)
            return True
        except KeyboardInterrupt:
            print_warning("\n服务器已停止")
            return True
        except Exception as e:
            print_error(f"启动服务器失败: {e}")
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
        
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()