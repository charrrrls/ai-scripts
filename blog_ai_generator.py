#!/usr/bin/env python3
"""
增强版博客AI助手 - by 阮阮
集成GLM-4-32B-0414模型，提供智能博客生成功能
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


class BlogAIHelper:
    def __init__(self):
        self.client = get_client()
        self.config = get_config()

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
title: “优化总结后的标题”「注这部分需要你自己优化后总结」
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
        if not title:
            print_error("请提供文章标题")
            return False

        # 检查博客目录
        if not os.path.exists(self.blog_dir):
            print_error(f"博客目录不存在: {self.blog_dir}")
            return False

        print_info(f"准备创建文章：{title}")
        print_info(f"模式：{'AI增强模式' if use_ai else '基础模式'}")

        # 生成文章内容
        if use_ai:
            content = self.generate_ai_article(title)
            filename = re.search(r'title:\s*"([^"]*)"', content).group(1)
        else:
            content = self._get_default_template(title)
        print_debug(f"文件名: {filename}")

        # 生成文件名和路径
        safe_filename = self._generate_safe_filename(filename)
        article_file = f"{self.posts_dir}/{safe_filename}.md"
        article_file = self._ensure_unique_filename(article_file)
        
        try:
            # 写入文件
            with open(article_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print_success("文章创建成功！")
            print_info(f"文件路径: {article_file}")
            print_info(f"文件名: {os.path.basename(article_file)}")

            # 尝试用Typora打开
            try:
                import subprocess
                subprocess.run(['open', '-a', 'Typora', article_file], check=True)
                print_success("Typora 已自动打开，开始您的创作之旅！")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print_warning("无法自动打开Typora，请手动打开文件")

            return True

        except Exception as e:
            print_error(f"创建文章失败: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="博客文章生成工具 - 集成GLM-4-32B-0414智能生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  %(prog)s "Python装饰器详解"           # 基础模式，快速创建
  %(prog)s "Python装饰器详解" --ai      # AI模式，智能生成内容
  %(prog)s "机器学习入门" -ai           # AI模式简写
        """
    )
    
    parser.add_argument('title', help='文章标题')
    parser.add_argument('--ai', '-ai', action='store_true', 
                       help='启用AI增强模式，使用GLM-4-32B-0414生成文章内容')
    
    args = parser.parse_args()
    
    # 创建AI助手实例并生成文章
    helper = BlogAIHelper()
    success = helper.create_blog_article(args.title, args.ai)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()