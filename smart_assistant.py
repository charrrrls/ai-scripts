#!/usr/bin/env python3
"""
智能助手集成工具 - by 阮阮
集成千问模型和本地向量库，提供智能问答功能
"""

import argparse
import sys
from typing import List, Optional
from pathlib import Path

from ai_client import get_client
from qwen_client import get_qwen_client
from vector_manager import get_vector_manager, Document
from ai_config import get_config
from color_utils import (
    print_error, print_success, print_warning, 
    print_info, print_progress, print_debug,
    colored_print, MessageType
)


class SmartAssistant:
    """智能助手"""
    
    def __init__(self, use_qwen: bool = False, vector_db_path: str = "./vector_db"):
        self.config = get_config()
        self.use_qwen = use_qwen
        
        # 初始化AI客户端
        if use_qwen:
            try:
                self.ai_client = get_qwen_client()
                print_success("已启用千问模型")
            except Exception as e:
                print_warning(f"千问模型初始化失败: {e}")
                print_info("回退到默认GLM模型")
                self.ai_client = get_client()
                self.use_qwen = False
        else:
            self.ai_client = get_client()
        
        # 初始化向量管理器
        self.vector_manager = get_vector_manager(vector_db_path)
        print_success("向量库初始化完成")
    
    def query_with_context(self, question: str, use_vector: bool = True, top_k: int = 3) -> str:
        """基于上下文的智能问答"""
        try:
            context_docs = []
            
            if use_vector:
                print_progress("搜索相关文档...")
                
                # 先尝试向量相似度搜索
                similar_results = self.vector_manager.search_similar(question, top_k)
                if similar_results:
                    context_docs = [doc for doc, similarity in similar_results]
                    print_success(f"找到 {len(context_docs)} 个相关文档")
                else:
                    # 如果没有相似文档，尝试关键词搜索
                    print_info("向量搜索无结果，尝试关键词搜索...")
                    context_docs = self.vector_manager.text_search(question, top_k)
                    if context_docs:
                        print_success(f"关键词搜索找到 {len(context_docs)} 个文档")
            
            # 生成回答
            if context_docs:
                print_progress("正在生成基于上下文的回答...")
                if self.use_qwen and hasattr(self.ai_client, 'generate_with_context'):
                    answer = self.ai_client.generate_with_context(question, context_docs)
                else:
                    # 为非千问客户端构建上下文提示
                    context_text = "\n\n".join([f"参考文档{i+1}: {doc.title}\n{doc.content}" 
                                               for i, doc in enumerate(context_docs)])
                    
                    enhanced_prompt = f"""基于以下参考文档回答问题：

参考文档：
{context_text}

问题：{question}

请基于上述文档内容回答问题，如果文档中没有相关信息，请结合你的知识回答。"""
                    
                    answer = self.ai_client.chat(enhanced_prompt)
            else:
                print_info("未找到相关文档，使用通用知识回答...")
                answer = self.ai_client.chat(question)
            
            return answer
            
        except Exception as e:
            print_error(f"问答生成失败: {e}")
            return "抱歉，我无法回答这个问题，请稍后再试。"
    
    def add_document_from_file(self, file_path: str, title: str = None) -> bool:
        """从文件添加文档到向量库"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                print_error(f"文件不存在: {file_path}")
                return False
            
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                print_error("文件编码错误，请确保是UTF-8格式")
                return False
            
            # 使用文件名作为默认标题
            if not title:
                title = file_path.stem
            
            # 添加到向量库
            metadata = {
                "source_file": str(file_path),
                "file_size": file_path.stat().st_size,
                "file_type": file_path.suffix
            }
            
            return self.vector_manager.add_document(title, content, metadata)
            
        except Exception as e:
            print_error(f"添加文件失败: {e}")
            return False
    
    def add_document_from_text(self, title: str, content: str) -> bool:
        """从文本添加文档到向量库"""
        try:
            metadata = {
                "source": "text_input",
                "content_length": len(content)
            }
            
            return self.vector_manager.add_document(title, content, metadata)
            
        except Exception as e:
            print_error(f"添加文档失败: {e}")
            return False
    
    def list_documents(self, limit: int = 20) -> None:
        """列出向量库中的文档"""
        try:
            docs = self.vector_manager.list_documents(limit)
            
            if not docs:
                print_warning("向量库为空")
                return
            
            print_info(f"向量库文档列表 (最新 {len(docs)} 条):")
            print("-" * 80)
            
            for i, doc in enumerate(docs, 1):
                print(f"{i:2d}. {doc.title}")
                print(f"    ID: {doc.id}")
                print(f"    创建时间: {doc.created_at}")
                print(f"    内容长度: {len(doc.content)} 字符")
                if doc.metadata:
                    print(f"    元数据: {doc.metadata}")
                print()
                
        except Exception as e:
            print_error(f"列出文档失败: {e}")
    
    def search_documents(self, query: str, method: str = "vector", top_k: int = 5) -> None:
        """搜索文档"""
        try:
            print_progress(f"使用 {method} 搜索: {query}")
            
            if method == "vector":
                results = self.vector_manager.search_similar(query, top_k)
                if results:
                    print_success(f"向量搜索找到 {len(results)} 个相似文档:")
                    print("-" * 80)
                    for i, (doc, similarity) in enumerate(results, 1):
                        print(f"{i}. {doc.title} (相似度: {similarity:.3f})")
                        print(f"   {doc.content[:150]}...")
                        print()
                else:
                    print_warning("向量搜索无结果")
                    
            elif method == "text":
                results = self.vector_manager.text_search(query, top_k)
                if results:
                    print_success(f"文本搜索找到 {len(results)} 个匹配文档:")
                    print("-" * 80)
                    for i, doc in enumerate(results, 1):
                        print(f"{i}. {doc.title}")
                        print(f"   {doc.content[:150]}...")
                        print()
                else:
                    print_warning("文本搜索无结果")
                    
        except Exception as e:
            print_error(f"搜索失败: {e}")
    
    def show_stats(self) -> None:
        """显示系统统计信息"""
        try:
            # 向量库统计
            vector_stats = self.vector_manager.get_stats()
            
            # AI模型信息
            if self.use_qwen:
                model_info = self.ai_client.get_model_info()
            else:
                model_info = self.ai_client.get_model_info()
            
            print_info("=== 智能助手系统状态 ===")
            print()
            
            # 模型信息
            colored_print("🤖 AI模型信息:", MessageType.INFO)
            for key, value in model_info.items():
                print(f"  {key}: {value}")
            print()
            
            # 向量库信息
            colored_print("📚 向量库统计:", MessageType.INFO)
            for key, value in vector_stats.items():
                print(f"  {key}: {value}")
            print()
            
        except Exception as e:
            print_error(f"获取统计信息失败: {e}")
    
    def interactive_mode(self) -> None:
        """交互式问答模式"""
        print_success("🎯 智能助手交互模式已启动")
        print_info("输入 'quit' 或 'exit' 退出")
        print_info("输入 'help' 查看帮助")
        print("-" * 50)
        
        while True:
            try:
                question = input("\n💭 请输入问题: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', '退出']:
                    print_success("再见！")
                    break
                
                if question.lower() in ['help', '帮助']:
                    self._show_help()
                    continue
                
                if question.lower() in ['stats', '统计']:
                    self.show_stats()
                    continue
                
                if question.lower() in ['list', '列表']:
                    self.list_documents()
                    continue
                
                # 回答问题
                print_progress("正在思考...")
                answer = self.query_with_context(question)
                
                print()
                colored_print("🎯 回答:", MessageType.SUCCESS)
                print(answer)
                print("-" * 50)
                
            except KeyboardInterrupt:
                print_warning("\n用户中断操作")
                break
            except Exception as e:
                print_error(f"处理失败: {e}")
    
    def _show_help(self) -> None:
        """显示帮助信息"""
        help_text = """
🎯 智能助手帮助信息:

基本命令:
  help/帮助    - 显示此帮助信息
  stats/统计   - 显示系统统计信息  
  list/列表    - 列出向量库文档
  quit/exit/退出 - 退出程序

问答方式:
  直接输入问题即可获得智能回答
  系统会自动搜索相关文档并结合AI知识回答

特性:
  ✨ 向量相似度搜索
  🔍 关键词文本搜索
  🤖 多模型支持(GLM/千问)
  📚 本地知识库
        """
        colored_print(help_text, MessageType.INFO)


def main():
    parser = argparse.ArgumentParser(
        description="智能助手 - 集成千问模型和本地向量库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  %(prog)s                              # 启动交互模式  
  %(prog)s -q "什么是机器学习?"           # 单次问答
  %(prog)s --qwen -q "Python基础"        # 使用千问模型
  %(prog)s --add-file document.txt       # 添加文档到向量库
  %(prog)s --list                        # 列出所有文档
  %(prog)s --search "Python" --method vector  # 向量搜索
  %(prog)s --stats                       # 显示统计信息
        """
    )
    
    # 基本选项
    parser.add_argument('-q', '--query', help='单次问答')
    parser.add_argument('--qwen', action='store_true', help='使用千问模型')
    parser.add_argument('--vector-db', default='./vector_db', help='向量库路径')
    
    # 文档管理
    parser.add_argument('--add-file', help='添加文件到向量库')
    parser.add_argument('--add-text', nargs=2, metavar=('TITLE', 'CONTENT'), 
                       help='添加文本到向量库')
    parser.add_argument('--list', action='store_true', help='列出所有文档')
    parser.add_argument('--search', help='搜索文档')
    parser.add_argument('--method', choices=['vector', 'text'], default='vector',
                       help='搜索方法')
    parser.add_argument('--top-k', type=int, default=5, help='返回结果数量')
    
    # 系统信息
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    
    args = parser.parse_args()
    
    try:
        # 创建智能助手
        assistant = SmartAssistant(use_qwen=args.qwen, vector_db_path=args.vector_db)
        
        # 处理不同操作
        if args.add_file:
            success = assistant.add_document_from_file(args.add_file)
            sys.exit(0 if success else 1)
            
        elif args.add_text:
            title, content = args.add_text
            success = assistant.add_document_from_text(title, content)
            sys.exit(0 if success else 1)
            
        elif args.list:
            assistant.list_documents()
            
        elif args.search:
            assistant.search_documents(args.search, args.method, args.top_k)
            
        elif args.stats:
            assistant.show_stats()
            
        elif args.query:
            answer = assistant.query_with_context(args.query)
            print()
            colored_print("🎯 回答:", MessageType.SUCCESS)
            print(answer)
            
        else:
            # 默认启动交互模式
            assistant.interactive_mode()
        
    except Exception as e:
        print_error(f"程序运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()