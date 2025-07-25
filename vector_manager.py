#!/usr/bin/env python3
"""
本地向量库管理模块 - by 阮阮
实现文档存储、检索和向量相似度搜索功能
"""

import os
import json
import hashlib
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from ai_client import get_client, AIClientError
from ai_config import get_config
from color_utils import print_error, print_success, print_warning, print_info, print_progress


@dataclass
class Document:
    """文档数据结构"""
    id: str
    title: str
    content: str
    embedding: Optional[List[float]]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VectorManager:
    """本地向量库管理器"""
    
    def __init__(self, db_path: str = "./vector_db"):
        self.config = get_config()
        self.client = get_client()
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        # 初始化SQLite数据库
        self.conn = sqlite3.connect(self.db_path / "documents.db")
        self._init_database()
        
        # 向量配置
        self.vector_config = self.config.get("vector_config", {})
        self.chunk_size = self.vector_config.get("chunk_size", 1000)
        self.chunk_overlap = self.vector_config.get("chunk_overlap", 100)
        self.similarity_threshold = self.vector_config.get("similarity_threshold", 0.7)
        
    def _init_database(self):
        """初始化数据库表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding TEXT,
                metadata TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_title ON documents(title);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_at ON documents(created_at);
        ''')
        
        self.conn.commit()
    
    def _generate_id(self, content: str) -> str:
        """生成文档ID"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _chunk_text(self, text: str) -> List[str]:
        """将长文本分割成小块"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if chunk:
                chunks.append(chunk)
                
        return chunks
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本向量编码"""
        try:
            # 这里使用简化的向量编码，实际项目中应该使用专门的embedding模型
            # 例如：OpenAI embedding API 或本地embedding模型
            
            # 简化实现：使用文本hash + 随机向量作为演示
            np.random.seed(hash(text) % (2**32))
            embedding = np.random.normal(0, 1, 384).tolist()  # 384维向量
            return embedding
            
        except Exception as e:
            print_error(f"获取向量编码失败: {e}")
            return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            print_error(f"计算相似度失败: {e}")
            return 0.0
    
    def add_document(self, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """添加文档到向量库"""
        try:
            doc_id = self._generate_id(content)
            
            # 检查文档是否已存在
            if self.get_document(doc_id):
                print_warning(f"文档已存在: {title}")
                return True
            
            print_progress(f"正在处理文档: {title}")
            
            # 获取向量编码
            embedding = self._get_embedding(content)
            if not embedding:
                print_error("向量编码失败")
                return False
            
            # 创建文档对象
            now = datetime.now().isoformat()
            document = Document(
                id=doc_id,
                title=title,
                content=content,
                embedding=embedding,
                metadata=metadata or {},
                created_at=now,
                updated_at=now
            )
            
            # 保存到数据库
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO documents (id, title, content, embedding, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                document.id,
                document.title,
                document.content,
                json.dumps(document.embedding),
                json.dumps(document.metadata),
                document.created_at,
                document.updated_at
            ))
            
            self.conn.commit()
            print_success(f"文档添加成功: {title}")
            return True
            
        except Exception as e:
            print_error(f"添加文档失败: {e}")
            return False
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """根据ID获取文档"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return Document(
                id=row[0],
                title=row[1],
                content=row[2],
                embedding=json.loads(row[3]) if row[3] else None,
                metadata=json.loads(row[4]) if row[4] else {},
                created_at=row[5],
                updated_at=row[6]
            )
            
        except Exception as e:
            print_error(f"获取文档失败: {e}")
            return None
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """向量相似度搜索"""
        try:
            print_progress(f"正在搜索相似文档: {query}")
            
            # 获取查询向量
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                print_error("查询向量编码失败")
                return []
            
            # 获取所有文档
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE embedding IS NOT NULL')
            rows = cursor.fetchall()
            
            if not rows:
                print_warning("向量库为空")
                return []
            
            # 计算相似度
            results = []
            for row in rows:
                doc = Document(
                    id=row[0],
                    title=row[1], 
                    content=row[2],
                    embedding=json.loads(row[3]),
                    metadata=json.loads(row[4]) if row[4] else {},
                    created_at=row[5],
                    updated_at=row[6]
                )
                
                similarity = self._cosine_similarity(query_embedding, doc.embedding)
                if similarity >= self.similarity_threshold:
                    results.append((doc, similarity))
            
            # 按相似度排序
            results.sort(key=lambda x: x[1], reverse=True)
            
            print_success(f"找到 {len(results[:top_k])} 个相似文档")
            return results[:top_k]
            
        except Exception as e:
            print_error(f"搜索失败: {e}")
            return []
    
    def text_search(self, keyword: str, top_k: int = 5) -> List[Document]:
        """文本关键词搜索"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM documents 
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (f'%{keyword}%', f'%{keyword}%', top_k))
            
            rows = cursor.fetchall()
            results = []
            
            for row in rows:
                doc = Document(
                    id=row[0],
                    title=row[1],
                    content=row[2],
                    embedding=json.loads(row[3]) if row[3] else None,
                    metadata=json.loads(row[4]) if row[4] else {},
                    created_at=row[5],
                    updated_at=row[6]
                )
                results.append(doc)
            
            print_success(f"找到 {len(results)} 个匹配文档")
            return results
            
        except Exception as e:
            print_error(f"文本搜索失败: {e}")
            return []
    
    def list_documents(self, limit: int = 20) -> List[Document]:
        """列出所有文档"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM documents 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            results = []
            
            for row in rows:
                doc = Document(
                    id=row[0],
                    title=row[1],
                    content=row[2],
                    embedding=json.loads(row[3]) if row[3] else None,
                    metadata=json.loads(row[4]) if row[4] else {},
                    created_at=row[5],
                    updated_at=row[6]
                )
                results.append(doc)
            
            return results
            
        except Exception as e:
            print_error(f"列出文档失败: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
            
            if cursor.rowcount > 0:
                self.conn.commit()
                print_success("文档删除成功")
                return True
            else:
                print_warning("文档不存在")
                return False
                
        except Exception as e:
            print_error(f"删除文档失败: {e}")
            return False
    
    def update_document(self, doc_id: str, title: str = None, content: str = None, 
                       metadata: Dict[str, Any] = None) -> bool:
        """更新文档"""
        try:
            doc = self.get_document(doc_id)
            if not doc:
                print_error("文档不存在")
                return False
            
            # 更新字段
            if title:
                doc.title = title
            if content:
                doc.content = content
                # 重新计算向量
                doc.embedding = self._get_embedding(content)
            if metadata:
                doc.metadata.update(metadata)
            
            doc.updated_at = datetime.now().isoformat()
            
            # 保存更新
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE documents 
                SET title = ?, content = ?, embedding = ?, metadata = ?, updated_at = ?
                WHERE id = ?
            ''', (
                doc.title,
                doc.content,
                json.dumps(doc.embedding),
                json.dumps(doc.metadata),
                doc.updated_at,
                doc_id
            ))
            
            self.conn.commit()
            print_success("文档更新成功")
            return True
            
        except Exception as e:
            print_error(f"更新文档失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取向量库统计信息"""
        try:
            cursor = self.conn.cursor()
            
            # 文档总数
            cursor.execute('SELECT COUNT(*) FROM documents')
            total_docs = cursor.fetchone()[0]
            
            # 有向量的文档数
            cursor.execute('SELECT COUNT(*) FROM documents WHERE embedding IS NOT NULL')
            docs_with_vectors = cursor.fetchone()[0]
            
            # 数据库大小
            db_size = os.path.getsize(self.db_path / "documents.db")
            
            return {
                "total_documents": total_docs,
                "documents_with_vectors": docs_with_vectors,
                "database_size_mb": round(db_size / 1024 / 1024, 2),
                "similarity_threshold": self.similarity_threshold,
                "chunk_size": self.chunk_size
            }
            
        except Exception as e:
            print_error(f"获取统计信息失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


# 全局向量管理器实例
_global_vector_manager: Optional[VectorManager] = None


def get_vector_manager(db_path: str = "./vector_db") -> VectorManager:
    """获取全局向量管理器实例"""
    global _global_vector_manager
    if _global_vector_manager is None:
        _global_vector_manager = VectorManager(db_path)
    return _global_vector_manager


def close_vector_manager():
    """关闭全局向量管理器"""
    global _global_vector_manager
    if _global_vector_manager:
        _global_vector_manager.close()
        _global_vector_manager = None


if __name__ == "__main__":
    # 测试向量管理器
    print("测试向量管理器...")
    
    vm = get_vector_manager()
    
    # 添加测试文档
    test_docs = [
        ("Python基础教程", "Python是一种高级编程语言，具有简洁的语法和强大的功能。"),
        ("机器学习入门", "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。"),
        ("Web开发指南", "Web开发包括前端和后端开发，需要掌握HTML、CSS、JavaScript等技术。")
    ]
    
    for title, content in test_docs:
        vm.add_document(title, content, {"type": "tutorial"})
    
    # 测试搜索
    print("\n=== 相似度搜索测试 ===")
    results = vm.search_similar("Python编程", top_k=3)
    for doc, similarity in results:
        print(f"文档: {doc.title}, 相似度: {similarity:.3f}")
    
    print("\n=== 关键词搜索测试 ===")
    results = vm.text_search("机器学习")
    for doc in results:
        print(f"文档: {doc.title}")
    
    # 显示统计信息
    print("\n=== 统计信息 ===")
    stats = vm.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    vm.close()
    print("\n✅ 向量管理器测试完成")