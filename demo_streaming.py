#!/usr/bin/env python3
"""
流式功能演示脚本 - by 阮阮
展示流式输出和批量输出的区别
"""

import sys
import time
import subprocess

# 添加当前目录到Python路径
sys.path.insert(0, '/Users/leion/scripts')

from color_utils import print_info, print_success, print_warning, colored_print, MessageType

def demo_streaming_vs_batch():
    """演示流式输出 vs 批量输出"""
    print_info("🎭 流式输出 vs 批量输出演示")
    colored_print("=" * 60, MessageType.NORMAL)
    
    print_info("\n📋 演示内容:")
    demos = [
        "1. 配置场景展示",
        "2. 流式输出效果（kimi默认模式）",
        "3. 批量输出效果（kimi --batch模式）",
        "4. commit信息生成（自动批量模式）",
        "5. 使用建议"
    ]
    
    for demo in demos:
        colored_print(f"  {demo}", MessageType.INFO)
    
    colored_print("\n" + "=" * 60, MessageType.NORMAL)

def show_config_scenarios():
    """展示配置场景"""
    print_info("\n1️⃣ 配置场景展示")
    print_info("-" * 30)
    
    try:
        from ai_config import get_config
        
        config = get_config()
        scenarios = {
            "chat": "对话场景",
            "commit": "提交信息场景", 
            "blog": "博客生成场景"
        }
        
        for scenario_key, scenario_name in scenarios.items():
            scenario_config = config.get_scenario_config(scenario_key)
            stream_mode = scenario_config.get("stream", False)
            temperature = scenario_config.get("temperature", 0.7)
            max_tokens = scenario_config.get("max_tokens", config.max_tokens)
            
            print_info(f"📝 {scenario_name} ({scenario_key})")
            colored_print(f"  流式模式: {'✅ 启用' if stream_mode else '❌ 禁用'}", 
                         MessageType.SUCCESS if stream_mode else MessageType.WARNING)
            colored_print(f"  温度参数: {temperature}", MessageType.NORMAL)
            colored_print(f"  最大tokens: {max_tokens}", MessageType.NORMAL)
            colored_print(f"  思考状态: {'✅ 显示' if config.should_show_thinking(scenario_key) else '❌ 隐藏'}", 
                         MessageType.SUCCESS if config.should_show_thinking(scenario_key) else MessageType.WARNING)
            print("")
            
    except Exception as e:
        print_warning(f"配置展示失败: {e}")

def demo_streaming_output():
    """演示流式输出"""
    print_info("\n2️⃣ 流式输出效果演示")
    print_info("-" * 30)
    
    print_info("💡 特点：AI回复逐字符实时显示，类似ChatGPT打字效果")
    print_info("🚀 命令：kimi \"请简单介绍一下流式输出的优势\"")
    print_info("⏱️  即将开始演示，请观察输出效果...")
    
    input("按回车键开始流式输出演示...")
    
    try:
        subprocess.run([
            '/Users/leion/scripts/kimi', 
            '请简单介绍一下流式输出的优势，用3-4句话概括'
        ], timeout=60)
        
        print_success("\n✅ 流式输出演示完成")
        
    except subprocess.TimeoutExpired:
        print_warning("演示超时")
    except Exception as e:
        print_warning(f"演示失败: {e}")

def demo_batch_output():
    """演示批量输出"""
    print_info("\n3️⃣ 批量输出效果演示")
    print_info("-" * 30)
    
    print_info("💡 特点：等待完整响应后一次性显示，适合自动化脚本")
    print_info("🚀 命令：kimi --batch \"请简单介绍一下批量输出的优势\"")
    print_info("⏱️  即将开始演示，请观察与流式输出的区别...")
    
    input("按回车键开始批量输出演示...")
    
    try:
        subprocess.run([
            '/Users/leion/scripts/kimi', 
            '--batch',
            '请简单介绍一下批量输出的优势，用3-4句话概括'
        ], timeout=60)
        
        print_success("\n✅ 批量输出演示完成")
        
    except subprocess.TimeoutExpired:
        print_warning("演示超时")
    except Exception as e:
        print_warning(f"演示失败: {e}")

def demo_commit_generation():
    """演示commit信息生成"""
    print_info("\n4️⃣ Commit信息生成演示")
    print_info("-" * 30)
    
    print_info("💡 特点：自动使用批量模式，确保稳定的自动化流程")
    print_info("🚀 命令：python3 ai_helper.py commit \"测试摘要\"")
    print_info("⏱️  即将演示commit信息生成...")
    
    input("按回车键开始commit信息生成演示...")
    
    try:
        result = subprocess.run([
            'python3', '/Users/leion/scripts/ai_helper.py', 
            'commit', 
            '博客文章: 流式输出功能.md (+100行, -5行) - 新增流式API调用, 添加实时输出效果, 优化用户体验'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            commit_msg = result.stdout.strip()
            print_success("✅ Commit信息生成成功")
            colored_print(f"生成的commit信息: {commit_msg}", MessageType.SUCCESS)
        else:
            print_warning("Commit信息生成失败")
            
    except subprocess.TimeoutExpired:
        print_warning("演示超时")
    except Exception as e:
        print_warning(f"演示失败: {e}")

def show_usage_recommendations():
    """显示使用建议"""
    print_info("\n5️⃣ 使用建议")
    print_info("-" * 30)
    
    recommendations = [
        {
            "scenario": "💬 日常AI对话",
            "command": "kimi \"你的问题\"",
            "mode": "流式模式",
            "reason": "实时反馈，更好的交互体验"
        },
        {
            "scenario": "🤖 自动化脚本",
            "command": "kimi --batch \"问题\"",
            "mode": "批量模式", 
            "reason": "稳定可靠，适合脚本调用"
        },
        {
            "scenario": "📝 博客推送",
            "command": "bp",
            "mode": "自动批量模式",
            "reason": "确保commit信息生成稳定"
        },
        {
            "scenario": "📖 博客生成",
            "command": "python3 blog_ai_generator.py",
            "mode": "自动批量模式",
            "reason": "长文本生成，需要完整结果"
        }
    ]
    
    for rec in recommendations:
        print_info(f"📋 {rec['scenario']}")
        colored_print(f"  命令: {rec['command']}", MessageType.NORMAL)
        colored_print(f"  模式: {rec['mode']}", MessageType.SUCCESS)
        colored_print(f"  原因: {rec['reason']}", MessageType.INFO)
        print("")

def main():
    """主演示函数"""
    demo_streaming_vs_batch()
    
    # 1. 配置场景展示
    show_config_scenarios()
    
    # 2. 流式输出演示
    demo_streaming_output()
    
    # 3. 批量输出演示
    demo_batch_output()
    
    # 4. commit信息生成演示
    demo_commit_generation()
    
    # 5. 使用建议
    show_usage_recommendations()
    
    # 总结
    colored_print("\n" + "=" * 60, MessageType.NORMAL)
    print_success("🎉 流式功能演示完成！")
    
    print_info("\n💡 核心优势:")
    advantages = [
        "✨ kimi对话：实时流式输出，类似ChatGPT体验",
        "⚡ bp推送：稳定批量模式，确保自动化可靠",
        "🎯 智能切换：根据使用场景自动选择最佳模式",
        "🔧 灵活配置：支持手动指定模式和参数"
    ]
    
    for advantage in advantages:
        colored_print(f"  {advantage}", MessageType.SUCCESS)
    
    colored_print("\n" + "=" * 60, MessageType.NORMAL)

if __name__ == "__main__":
    main()
