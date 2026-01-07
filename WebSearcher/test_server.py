#!/usr/bin/env python3
"""
快速测试脚本：验证WebSearcher MCP服务器（本地和远程模式）

使用方法：
    python test_server.py
"""

import subprocess
import time
import requests
import sys


def test_stdio_mode():
    """测试stdio模式"""
    print("=" * 60)
    print("测试 1: stdio模式（本地模式）")
    print("=" * 60)
    
    print("\n启动服务器（stdio模式）...")
    print("提示：按Ctrl+C停止服务器\n")
    
    try:
        # 启动服务器
        process = subprocess.Popen(
            ["python", "-m", "src.server", "--mode", "stdio"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待一下看是否有错误
        time.sleep(2)
        
        if process.poll() is not None:
            # 进程已退出
            stdout, stderr = process.communicate()
            print("❌ 服务器启动失败")
            print(f"错误信息：\n{stderr}")
            return False
        else:
            print("✅ 服务器启动成功（stdio模式）")
            print("   服务器正在运行，等待stdin输入...")
            
            # 终止进程
            process.terminate()
            process.wait(timeout=5)
            return True
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_http_mode():
    """测试HTTP模式"""
    print("\n" + "=" * 60)
    print("测试 2: HTTP模式（远程模式）")
    print("=" * 60)
    
    print("\n启动服务器（HTTP模式）...")
    
    try:
        # 启动服务器
        process = subprocess.Popen(
            ["python", "-m", "src.server", "--mode", "http", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        print("等待服务器启动...")
        time.sleep(3)
        
        if process.poll() is not None:
            # 进程已退出
            stdout, stderr = process.communicate()
            print("❌ 服务器启动失败")
            print(f"错误信息：\n{stderr}")
            return False
        
        print("✅ 服务器启动成功")
        
        # 测试健康检查
        print("\n测试健康检查端点...")
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查成功: {data}")
            else:
                print(f"❌ 健康检查失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
            return False
        
        # 测试工具列表
        print("\n测试工具列表...")
        try:
            request_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            response = requests.post(
                "http://127.0.0.1:8000/message",
                json=request_data,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    tools = data["result"]["tools"]
                    print(f"✅ 工具列表获取成功: 找到 {len(tools)} 个工具")
                    for tool in tools:
                        print(f"   - {tool['name']}")
                else:
                    print(f"❌ 工具列表获取失败: {data.get('error')}")
                    return False
            else:
                print(f"❌ 工具列表获取失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 工具列表获取失败: {e}")
            return False
        
        # 测试搜索功能（如果配置了API密钥）
        print("\n测试搜索功能...")
        try:
            request_data = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "web_search",
                    "arguments": {
                        "query": "test",
                        "max_results": 3
                    }
                }
            }
            response = requests.post(
                "http://127.0.0.1:8000/message",
                json=request_data,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    print("✅ 搜索功能正常")
                    content = data["result"]["content"][0]["text"]
                    # 只显示前200个字符
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(f"   结果预览: {preview}")
                else:
                    error = data.get("error", {})
                    if "not configured" in error.get("message", "").lower():
                        print("⚠️  搜索功能未配置API密钥（这是正常的）")
                        print("   提示：配置.env文件中的API密钥以启用搜索功能")
                    else:
                        print(f"❌ 搜索失败: {error.get('message')}")
            else:
                print(f"❌ 搜索请求失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️  搜索测试失败: {e}")
            print("   （如果未配置API密钥，这是正常的）")
        
        # 终止服务器
        print("\n停止服务器...")
        process.terminate()
        process.wait(timeout=5)
        print("✅ 服务器已停止")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        if 'process' in locals():
            process.terminate()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("WebSearcher MCP 服务器测试")
    print("=" * 60)
    print()
    
    # 检查依赖
    print("检查依赖...")
    try:
        import mcp
        import httpx
        import aiohttp
        print("✅ 所有依赖已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("\n请运行: pip install -e .")
        sys.exit(1)
    
    print()
    
    # 测试stdio模式
    stdio_result = test_stdio_mode()
    
    # 测试HTTP模式
    http_result = test_http_mode()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"stdio模式: {'✅ 通过' if stdio_result else '❌ 失败'}")
    print(f"HTTP模式:  {'✅ 通过' if http_result else '❌ 失败'}")
    print()
    
    if stdio_result and http_result:
        print("🎉 所有测试通过！")
        print("\n下一步：")
        print("1. 配置.env文件添加API密钥")
        print("2. 选择运行模式：")
        print("   - 本地模式: python -m src.server --mode stdio")
        print("   - 远程模式: python -m src.server --mode http")
        print("3. 查看文档了解更多：")
        print("   - README.md")
        print("   - 配置参数说明.md")
        print("   - 远程部署指南.md")
        return 0
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
