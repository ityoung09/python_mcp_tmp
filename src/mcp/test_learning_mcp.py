"""
test_learning_mcp.py - MCP 服务测试与客户端调用示例

通过本脚本，你可以在不需要启动 Claude Desktop 或外部应用的情况下，
直接通过 Python Client 调用 learning_mcp 服务的 Tools、Resources 与 Prompts，
直观理解客户端与 MCP 服务端之间的交互过程！

运行方式:
    uv run python src/mcp/test_learning_mcp.py
"""

import asyncio
import json
import sys

# 兼容 Windows 控制台输出编码
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastmcp import Client
from learning_mcp import mcp


async def main():
    print("=" * 65)
    print("  [>] 正在启动 MCP 客户端并连接到 Learning MCP 服务...")
    print("=" * 65)

    async with Client(mcp) as client:
        # -------------------------------------------------------------
        # 1. 测试 Tools (工具)
        # -------------------------------------------------------------
        print("\n" + "-" * 30 + " 【1. Tools 工具测试】 " + "-" * 30)
        tools = await client.list_tools()
        print(f"[*] 服务端暴露的工具数量: {len(tools)}")
        for t in tools:
            print(f"  * 工具名: {t.name:<20} 描述: {t.description}")

        # 调用计算器工具
        expr = "15 * (100 - 32) / 1.8"
        print(f"\n[>] 调用工具: calculate | 算式: '{expr}'")
        res_calc = await client.call_tool("calculate", {"expression": expr})
        print(f"    返回结果: {res_calc.data}")

        # 调用编程小知识工具
        print(f"\n[>] 调用工具: get_programming_tip")
        res_tip = await client.call_tool("get_programming_tip", {})
        print(f"    返回结果: {res_tip.data}")

        # 调用添加备忘录工具
        print(f"\n[>] 调用工具: add_memo | 添加一条新的学习笔记")
        res_add = await client.call_tool(
            "add_memo",
            {
                "title": "FastMCP 上手实践",
                "content": "通过 Client(mcp) 可以直接在代码里以内存或网络方式调用 MCP 服务的全部功能！",
                "category": "学习"
            }
        )
        print(f"    返回结果: {res_add.data}")

        # 调用搜索备忘录工具
        print(f"\n[>] 调用工具: search_memos | 搜索分类为 '学习' 的条目")
        res_search = await client.call_tool("search_memos", {"category": "学习"})
        print(f"    搜索到 {len(res_search.data)} 条备忘录:")
        for memo in res_search.data:
            print(f"      - [{memo['id']}] {memo['title']} ({memo['created_at']})")

        # -------------------------------------------------------------
        # 2. 测试 Resources (资源)
        # -------------------------------------------------------------
        print("\n" + "-" * 30 + " 【2. Resources 资源测试】 " + "-" * 30)
        resources = await client.list_resources()
        print(f"[*] 服务端暴露的静态资源数量: {len(resources)}")
        for r in resources:
            print(f"  * 资源 URI: {str(r.uri):<25} 描述: {r.description}")

        # 读取统计资源 memo://stats
        print("\n[>] 读取资源: memo://stats")
        stats_content = await client.read_resource("memo://stats")
        for chunk in stats_content:
            parsed = json.loads(chunk.text)
            print(json.dumps(parsed, ensure_ascii=False, indent=4))

        # 读取动态模板资源 memo://category/生活
        print("\n[>] 读取动态资源模板: memo://category/生活")
        cat_content = await client.read_resource("memo://category/生活")
        for chunk in cat_content:
            print(chunk.text)

        # -------------------------------------------------------------
        # 3. 测试 Prompts (提示词模板)
        # -------------------------------------------------------------
        print("\n" + "-" * 30 + " 【3. Prompts 提示词模板测试】 " + "-" * 30)
        prompts = await client.list_prompts()
        print(f"[*] 服务端提供的 Prompt 模板数量: {len(prompts)}")
        for p in prompts:
            print(f"  * 模板名: {p.name:<25} 描述: {p.description}")

        # 渲染提示词模板
        print("\n[>] 获取 Prompt: summarize_memos_prompt(focus_category='学习')")
        prompt_res = await client.get_prompt("summarize_memos_prompt", {"focus_category": "学习"})
        for msg in prompt_res.messages:
            print(f"    [{msg.role.upper()}]:\n{msg.content.text}")

    print("\n" + "=" * 65)
    print("  [+] MCP 服务全部功能测试通过！")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
