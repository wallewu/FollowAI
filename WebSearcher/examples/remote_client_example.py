"""
示例：如何通过HTTP调用远程WebSearcher MCP服务器

这个脚本演示了如何使用Python的requests库与远程MCP服务器通信。
"""

import requests
import json


class WebSearcherClient:
    """WebSearcher MCP客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端
        
        Args:
            base_url: MCP服务器的基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.message_url = f"{self.base_url}/message"
        self.health_url = f"{self.base_url}/health"
    
    def check_health(self) -> dict:
        """
        检查服务器健康状态
        
        Returns:
            健康状态响应
        """
        response = requests.get(self.health_url)
        response.raise_for_status()
        return response.json()
    
    def list_tools(self) -> dict:
        """
        列出可用的工具
        
        Returns:
            工具列表
        """
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(
            self.message_url,
            json=request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def search(self, query: str, max_results: int = 10) -> dict:
        """
        执行网页搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            搜索结果
        """
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "web_search",
                "arguments": {
                    "query": query,
                    "max_results": max_results
                }
            }
        }
        
        response = requests.post(
            self.message_url,
            json=request,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()


def main():
    """主函数：演示如何使用客户端"""
    
    # 创建客户端（修改URL为你的服务器地址）
    client = WebSearcherClient("http://localhost:8000")
    
    print("=" * 60)
    print("WebSearcher MCP 远程客户端示例")
    print("=" * 60)
    print()
    
    # 1. 检查服务器健康状态
    print("1. 检查服务器健康状态...")
    try:
        health = client.check_health()
        print(f"   ✅ 服务器状态: {health['status']}")
        print(f"   服务名称: {health['service']}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return
    print()
    
    # 2. 列出可用工具
    print("2. 列出可用工具...")
    try:
        tools_response = client.list_tools()
        if "result" in tools_response:
            tools = tools_response["result"]["tools"]
            print(f"   找到 {len(tools)} 个工具:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print(f"   ❌ 错误: {tools_response.get('error', {}).get('message')}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    print()
    
    # 3. 执行搜索
    print("3. 执行网页搜索...")
    query = "Python 3.12 新特性"
    print(f"   搜索查询: {query}")
    try:
        search_response = client.search(query, max_results=5)
        
        if "result" in search_response:
            content = search_response["result"]["content"][0]["text"]
            print(f"   ✅ 搜索成功!")
            print()
            print("   搜索结果:")
            print("   " + "-" * 56)
            # 缩进输出
            for line in content.split('\n'):
                print(f"   {line}")
        else:
            error = search_response.get("error", {})
            print(f"   ❌ 搜索失败: {error.get('message')}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    print()
    
    print("=" * 60)
    print("示例完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
