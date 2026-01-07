# WebSearcher MCP 服务器

一个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 的服务器，为AI助手提供网页搜索功能。该服务器使AI模型能够使用各种搜索引擎API实时搜索网页。

## 🌟 特性

- **MCP协议兼容**：完全实现Model Context Protocol规范
- **多搜索引擎支持**：支持Google自定义搜索、Bing网页搜索和SerpAPI
- **灵活配置**：通过环境变量轻松配置
- **健壮的错误处理**：全面的错误处理和日志记录
- **类型安全**：使用Python类型提示构建，提高代码质量
- **异步操作**：高效的异步/等待操作

## 📋 什么是MCP？

Model Context Protocol（模型上下文协议）是一个开放协议，用于标准化AI应用程序与外部数据源和工具的连接方式。它提供：

- **标准化通信**：基于JSON-RPC 2.0的客户端-服务器通信协议
- **工具集成**：允许AI模型调用外部工具和函数
- **资源访问**：使AI能够访问外部数据源
- **提示模板**：支持可重用的提示模板

### MCP架构

```
┌─────────────────┐         ┌──────────────────┐
│   MCP Client    │◄───────►│   MCP Server     │
│  (AI助手)       │  stdio  │ (WebSearcher)    │
└─────────────────┘         └──────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  搜索引擎API    │
                            │   (Google,      │
                            │   Bing等)       │
                            └─────────────────┘
```

## 🚀 快速开始

### 前置要求

- Python 3.10或更高版本
- 来自以下支持的搜索引擎之一的API密钥：
  - [Google自定义搜索API](https://developers.google.com/custom-search/v1/overview)
  - [Bing网页搜索API](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)
  - [SerpAPI](https://serpapi.com/)（推荐初学者使用）

### 安装

1. **克隆或下载此项目**：
   ```bash
   cd WebSearcher
   ```

2. **安装依赖**：
   ```bash
   pip install -e .
   ```
   
   或直接安装：
   ```bash
   pip install mcp httpx python-dotenv
   ```

3. **配置环境变量**：
   ```bash
   cp .env.example .env
   ```
   
   编辑`.env`文件并添加您的API密钥：
   ```env
   # 使用SerpAPI（最容易上手）
   SEARCH_ENGINE=serpapi
   SERPAPI_KEY=your_serpapi_key_here
   
   # 或使用Google自定义搜索
   # SEARCH_ENGINE=google
   # GOOGLE_API_KEY=your_google_api_key
   # GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
   
   # 或使用Bing
   # SEARCH_ENGINE=bing
   # BING_API_KEY=your_bing_api_key
   ```

### 运行服务器

服务器使用stdio传输作为MCP服务器运行：

```bash
python -m src.server
```

但是，MCP服务器通常不直接运行。相反，它们在MCP客户端（如Claude Desktop）中配置。

## 🔧 配置

WebSearcher支持两种运行模式：

### 模式1：本地模式（stdio）

适合个人使用，客户端和服务器在同一台机器上。

### 模式2：远程模式（HTTP/SSE）

适合团队使用或云部署，客户端和服务器可以分离。详见[远程部署指南.md](docs/远程部署指南.md)。

**快速启动远程服务器**：
```bash
# 安装额外依赖
pip install aiohttp

# 启动HTTP服务器
python -m src.server --mode http --host 0.0.0.0 --port 8000

# 验证服务器
curl http://localhost:8000/health
```

### MCP客户端配置（本地模式）

#### Claude Desktop

将以下内容添加到您的Claude Desktop配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "websearcher": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/absolute/path/to/WebSearcher",
      "env": {
        "SEARCH_ENGINE": "serpapi",
        "SERPAPI_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### 其他MCP客户端

对于其他MCP客户端，配置它们运行：
```bash
python -m src.server
```

并设置适当的环境变量。

### 环境变量

| 变量名 | 说明 | 默认值 | 是否必需 |
|----------|-------------|---------|----------|
| `SEARCH_ENGINE` | 要使用的搜索引擎（`google`、`bing`、`serpapi`） | `serpapi` | 是 |
| `SERPAPI_KEY` | SerpAPI密钥 | - | 使用SerpAPI时必需 |
| `GOOGLE_API_KEY` | Google API密钥 | - | 使用Google时必需 |
| `GOOGLE_SEARCH_ENGINE_ID` | Google自定义搜索引擎ID | - | 使用Google时必需 |
| `BING_API_KEY` | Bing API密钥 | - | 使用Bing时必需 |
| `MAX_RESULTS` | 默认最大结果数 | `10` | 否 |
| `REQUEST_TIMEOUT` | API请求超时时间（秒） | `30` | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |
| `DEBUG_MODE` | 启用调试模式 | `false` | 否 |

## 🛠️ 使用方法

在MCP客户端中配置后，您可以使用`web_search`工具：

### 示例提示

**在Claude Desktop中**：
```
搜索网页"Python 3.12最新特性"
```

```
查找关于"Model Context Protocol"的信息
```

### 工具模式

`web_search`工具接受：

```json
{
  "query": "搜索查询字符串",
  "max_results": 10
}
```

**参数**：
- `query`（字符串，必需）：搜索查询
- `max_results`（整数，可选）：最大结果数（1-20，默认：10）

**返回**：格式化的文本响应，包含搜索结果：
- 标题
- URL
- 摘要/描述
- 结果位置

## 🧪 测试

### 手动测试

您可以使用MCP Inspector手动测试服务器：

```bash
npx @modelcontextprotocol/inspector python -m src.server
```

### 单元测试

运行测试套件：

```bash
pytest tests/
```

## 📁 项目结构

```
WebSearcher/
├── src/
│   ├── __init__.py          # 包初始化
│   ├── server.py            # 主MCP服务器实现
│   ├── config.py            # 配置管理
│   ├── search_client.py     # 搜索引擎API客户端
│   ├── errors.py            # 错误处理工具
│   └── logging_config.py    # 日志配置
├── tests/                   # 测试文件
├── .env.example             # 环境配置示例
├── .gitignore              # Git忽略规则
├── pyproject.toml          # 项目元数据和依赖
└── README.md               # 本文件
```

## 🔍 工作原理

1. **初始化**：服务器从环境变量加载配置
2. **MCP协议**：通过stdio使用JSON-RPC 2.0与MCP客户端通信
3. **工具注册**：使用其模式注册`web_search`工具
4. **搜索执行**：调用时，验证参数并通过配置的API执行搜索
5. **结果格式化**：格式化并将搜索结果返回给客户端

## 🐛 故障排查

### 服务器无法启动

- 检查是否设置了所有必需的环境变量
- 验证您的API密钥是否有效
- 检查日志以获取具体错误消息

### 没有搜索结果

- 验证您的API密钥是否有足够的配额
- 检查您的互联网连接
- 尝试不同的搜索查询
- 启用调试模式：`DEBUG_MODE=true`

### API速率限制

- 大多数搜索API都有速率限制
- 考虑缓存结果或实施速率限制
- 查看您的API提供商文档

### 日志位置

日志写入stderr。在Claude Desktop中，检查：
- **macOS**: `~/Library/Logs/Claude/`
- **Windows**: `%APPDATA%\Claude\logs\`

## 🤝 贡献

欢迎贡献！改进方向：

- 额外的搜索引擎支持
- 结果缓存
- 速率限制
- 更全面的测试
- 更好的错误消息

## 📄 许可证

本项目按原样提供，用于教育和实际用途。

## 📚 文档

详细文档请查看 [docs](docs/) 目录：

- **[配置参数说明.md](docs/配置参数说明.md)** - 所有配置参数的详细说明
- **[远程部署指南.md](docs/远程部署指南.md)** - 远程部署完整指南
- **[更新说明.md](docs/更新说明.md)** - 最新更新内容
- **[QUICKSTART.md](docs/QUICKSTART.md)** - 快速开始指南（英文）
- **[PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - 项目总结（英文）

## 🔗 资源

- [Model Context Protocol文档](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop](https://claude.ai/download)
- [SerpAPI文档](https://serpapi.com/docs)
- [Google自定义搜索API](https://developers.google.com/custom-search/v1/overview)
- [Bing网页搜索API](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)

## 📝 注意事项

- 此服务器需要活动的互联网连接
- 根据您的提供商，可能会产生搜索API费用
- 结果质量取决于使用的搜索引擎
- 始终遵守搜索引擎服务条款
