# 🤖 AI Scripts - 智能AI脚本工具集

[![GitHub stars](https://img.shields.io/github/stars/charrrrls/ai-scripts?style=social)](https://github.com/charrrrls/ai-scripts/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/charrrrls/ai-scripts?style=social)](https://github.com/charrrrls/ai-scripts/network)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个功能强大的AI脚本工具集，支持流式对话、智能博客生成、自动化推送等功能。基于GLM-4-32B-0414模型，提供ChatGPT级别的交互体验。

## ✨ 核心特性

### 🎭 流式对话体验
- **实时输出**: 类似ChatGPT的逐字符打字效果
- **智能切换**: 根据使用场景自动选择最佳模式
- **彩色输出**: 美观的终端显示效果

### 🚀 智能自动化
- **智能推送**: 自动生成commit信息并推送博客
- **博客生成**: AI驱动的博客文章结构生成
- **场景适配**: 不同场景使用最优配置

### 🔧 现代化架构
- **统一配置**: 集中管理所有AI相关配置
- **模块化设计**: 易于扩展和维护
- **错误处理**: 完善的重试和异常处理机制

## 🎯 快速开始

### 安装依赖
```bash
pip install requests
```

### 基础使用
```bash
# AI对话（流式输出）
./kimi "你好，请介绍一下你自己"

# 交互模式
./kimi -i

# 智能博客推送
./bp

# 生成博客文章
python3 blog_ai_generator.py "文章标题" --ai
```

## 📚 功能详解

### 💬 AI对话 (`kimi`)
```bash
# 流式对话（默认）
kimi "请解释一下机器学习"

# 批量模式
kimi --batch "简单问题"

# 交互模式
kimi -i
```

### 📝 博客管理 (`bp`)
```bash
# 智能推送（自动生成commit信息）
bp

# 普通推送
bp -m "自定义commit信息"

# 强制推送
bp -f
```

### 📖 博客生成
```bash
# AI生成博客结构
python3 blog_ai_generator.py "深度学习入门" --ai

# 手动模式
python3 blog_ai_generator.py "文章标题"
```

### 🔧 AI助手
```bash
# 对话
python3 ai_helper.py chat "你的问题"

# 流式对话
python3 ai_helper.py chat "问题" --stream

# 生成commit信息
python3 ai_helper.py commit "文件更改摘要"
```

## 🏗️ 架构设计

### 配置层 (`ai_config.py`)
- 多环境支持（开发/生产/测试）
- 场景化配置（对话/提交/博客）
- 灵活的参数管理

### API调用层 (`ai_client.py`)
- 统一的API调用接口
- 流式和批量模式支持
- 智能重试机制

### 应用层
- `ai_helper.py`: 核心AI功能
- `blog_ai_generator.py`: 博客生成
- `blog_manager.py`: 博客管理
- `kimi`: 便捷对话脚本
- `bp`: 智能推送脚本

## 🎭 使用场景

### 📱 日常AI对话
```bash
kimi "帮我写一个Python函数"
# ✨ 实时流式输出，即时反馈
```

### 🤖 自动化工作流
```bash
bp
# 🎯 自动分析更改，生成commit信息，推送博客
```

### 📝 内容创作
```bash
python3 blog_ai_generator.py "技术分享：Docker容器化实践" --ai
# 📖 生成完整的博客文章结构
```

## ⚙️ 配置说明

### 环境变量
```bash
export AI_API_KEY="your-api-key"
export AI_MODEL_NAME="THUDM/GLM-4-32B-0414"
export AI_TEMPERATURE="0.7"
```

### 配置文件
创建 `ai_config_production.json`:
```json
{
    "model_name": "自定义模型",
    "temperature": 0.5,
    "max_tokens": 2000
}
```

## 🎯 场景配置

### 对话场景（流式模式）
- 实时输出，更好的交互体验
- 较高的创造性（temperature=0.8）
- 显示思考状态

### 提交场景（批量模式）
- 稳定可靠，适合自动化
- 较低的创造性（temperature=0.3）
- 快速生成短文本

### 博客场景（批量模式）
- 处理长文本内容
- 平衡的创造性（temperature=0.7）
- 支持大量tokens

## 🔧 开发指南

### 添加新功能
1. 在 `ai_config.py` 中添加场景配置
2. 在 `ai_client.py` 中实现API调用
3. 在应用层添加用户界面

### 自定义配置
```python
from ai_config import get_config, set_environment, Environment

# 切换环境
set_environment(Environment.DEVELOPMENT)

# 获取配置
config = get_config()
custom_config = config.get_scenario_config("custom")
```

## 📊 性能特点

### 流式模式
- ⚡ 即时反馈，感知速度快
- 🎨 更好的用户体验
- 💬 适合交互式对话

### 批量模式
- 🛡️ 稳定可靠
- 🤖 适合自动化脚本
- 📊 完整结果处理

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [SiliconFlow](https://siliconflow.cn/) - 提供GLM-4-32B-0414模型API
- [THUDM](https://github.com/THUDM) - GLM模型开发团队

## 📞 联系方式

- GitHub: [@charrrrls](https://github.com/charrrrls)
- Issues: [GitHub Issues](https://github.com/charrrrls/ai-scripts/issues)

---

⭐ 如果这个项目对您有帮助，请给个Star支持一下！
