"""
learning_mcp.py - 一个专门用于学习 MCP (Model Context Protocol) 核心概念的示例服务

本服务全面演示了 MCP 协议的三大核心要素 (Three Primitives)：
1. Tools (工具): 允许大模型调用的外部函数（配合 Pydantic 自动生成结构化 Schema，支持输入验证、错误处理）。
2. Resources (资源): 类似只读 REST API 的数据通道，支持静态 URI 和带参数的动态模板 URI。
3. Prompts (提示词模板): 预定义的提示词模板，供客户端或大模型调用以执行标准化工作流。

支持两种通信传输模式 (Transport):
- SSE (Server-Sent Events): 基于 HTTP，适合局域网/远程微服务调用，默认运行在端口 8001。
- Stdio (标准输入输出): 适合本地 LLM 客户端（如 Claude Desktop, Cursor, Antigravity）通过子进程启动。
"""

import argparse
import ast
import datetime
import json
import logging
import operator
import sys
from typing import Optional
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# 兼容 Windows 控制台输出编码
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("learning-mcp")

# 创建 FastMCP 实例
mcp = FastMCP(
    name="Smart Memo & Utilities MCP",
    instructions="""这是一个用于学习和演示 MCP 协议的示例服务。
提供备忘录知识库管理、数学表达式计算、编程小知识等工具，以及资源查看和预置 Prompt 模板。"""
)


# ======================================================================
# 数据模型 (Pydantic Models)
# FastMCP 会利用 Pydantic 自动为大模型生成高可读性、严格校验的 JSON Schema
# ======================================================================

class MemoItem(BaseModel):
    """备忘录条目数据模型"""
    id: int = Field(description="备忘录唯一 ID")
    title: str = Field(description="备忘录标题")
    category: str = Field(description="分类标签，例如：学习、工作、生活")
    content: str = Field(description="备忘录具体详细内容")
    created_at: str = Field(description="创建时间 (YYYY-MM-DD HH:MM:SS)")


class MemoOperationResult(BaseModel):
    """备忘录操作返回结果"""
    success: bool = Field(description="操作是否成功")
    message: str = Field(description="操作说明或提示信息")
    memo: Optional[MemoItem] = Field(default=None, description="操作相关的备忘录条目")


class CalculationResult(BaseModel):
    """数学计算结果模型"""
    success: bool = Field(description="计算是否成功")
    expression: str = Field(description="计算的原始算式")
    result: Optional[float] = Field(default=None, description="计算得出的数值结果")
    error: Optional[str] = Field(default=None, description="发生错误时的具体信息")


class ProgrammingTip(BaseModel):
    """编程小知识模型"""
    category: str = Field(description="分类（如 MCP、Python、架构）")
    title: str = Field(description="知识点标题")
    content: str = Field(description="详细要点解析")


# ----------------------------------------------------------------------
# 内存数据存储（用于演示资源与工具的状态交互）
# ----------------------------------------------------------------------
MEMO_STORE: list[MemoItem] = [
    MemoItem(
        id=1,
        title="MCP 核心理念",
        category="学习",
        content="MCP (Model Context Protocol) 是 Anthropic 推出的开放标准，让 LLM 与外部数据和工具无缝连接。",
        created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ),
    MemoItem(
        id=2,
        title="MCP 三大支柱",
        category="学习",
        content="Tools (可调用工具), Resources (只读上下文资源), Prompts (可复用提示词模板)。",
        created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ),
    MemoItem(
        id=3,
        title="周末计划",
        category="生活",
        content="上午学习 FastMCP 框架开发，下午跑步 5 公里锻炼身体。",
        created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
]


# ======================================================================
# 第一支柱: Tools (工具)
# 大模型可以自主决定何时调用这些函数，函数的 docstring 和类型注解会自动生成 JSON Schema
# ======================================================================

@mcp.tool()
def add_memo(title: str, content: str, category: str = "学习") -> MemoOperationResult:
    """添加一条新的备忘录/学习笔记。

    Args:
        title (str): 备忘录标题
        content (str): 备忘录内容
        category (str): 备忘录分类，默认为 '学习'

    Returns:
        MemoOperationResult: 包含操作结果与新建备忘录详情的对象
    """
    new_id = (max([m.id for m in MEMO_STORE]) + 1) if MEMO_STORE else 1
    new_memo = MemoItem(
        id=new_id,
        title=title,
        category=category,
        content=content,
        created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    MEMO_STORE.append(new_memo)
    logger.info("成功添加备忘录: ID=%d, Title=%s", new_id, title)
    return MemoOperationResult(
        success=True,
        message=f"备忘录「{title}」已成功保存！",
        memo=new_memo
    )


@mcp.tool()
def search_memos(keyword: str = "", category: str = "") -> list[MemoItem]:
    """搜索或筛选现有的备忘录。

    Args:
        keyword (str): 关键词（搜索标题或内容），留空表示不限制关键词
        category (str): 分类筛选，留空表示所有分类

    Returns:
        list[MemoItem]: 匹配的备忘录对象列表
    """
    results: list[MemoItem] = []
    kw = keyword.lower().strip()
    cat = category.strip()

    for item in MEMO_STORE:
        if cat and item.category != cat:
            continue
        if kw and (kw not in item.title.lower() and kw not in item.content.lower()):
            continue
        results.append(item)

    logger.info("搜索备忘录: keyword='%s', category='%s', 匹配到 %d 条", keyword, category, len(results))
    return results


@mcp.tool()
def delete_memo(memo_id: int) -> MemoOperationResult:
    """根据 ID 删除一条备忘录。

    Args:
        memo_id (int): 要删除的备忘录 ID

    Returns:
        MemoOperationResult: 删除操作结果
    """
    global MEMO_STORE
    initial_len = len(MEMO_STORE)
    deleted_item = next((m for m in MEMO_STORE if m.id == memo_id), None)
    MEMO_STORE = [m for m in MEMO_STORE if m.id != memo_id]

    if len(MEMO_STORE) < initial_len:
        logger.info("删除备忘录成功: ID=%d", memo_id)
        return MemoOperationResult(
            success=True,
            message=f"ID 为 {memo_id} 的备忘录已成功删除",
            memo=deleted_item
        )
    return MemoOperationResult(
        success=False,
        message=f"未找到 ID 为 {memo_id} 的备忘录"
    )


# 安全计算器实现（利用 Python AST 进行安全语法树求值，避免 eval 的安全风险）
_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _eval_ast(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    elif isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPERATORS:
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        return float(_SAFE_OPERATORS[type(node.op)](left, right))
    elif isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPERATORS:
        return float(_SAFE_OPERATORS[type(node.op)](_eval_ast(node.operand)))
    raise ValueError(f"不支持的操作类型或语法节点: {type(node).__name__}")


@mcp.tool()
def calculate(expression: str) -> CalculationResult:
    """计算基础数学表达式（支持 +, -, *, /, //, %, ** 等安全运算）。

    Args:
        expression (str): 数学算式，例如 "12 * (34 + 56) / 2" 或 "2 ** 10"

    Returns:
        CalculationResult: 计算结果或错误描述
    """
    try:
        parsed = ast.parse(expression, mode='eval')
        val = _eval_ast(parsed.body)
        return CalculationResult(
            success=True,
            expression=expression,
            result=val
        )
    except Exception as e:
        return CalculationResult(
            success=False,
            expression=expression,
            error=f"计算失败: {str(e)}"
        )


@mcp.tool()
async def get_programming_tip() -> ProgrammingTip:
    """获取一条实用的编程/MCP 开发小知识与最佳实践。

    Returns:
        ProgrammingTip: 包含技巧分类、标题与核心要点
    """
    tips = [
        ProgrammingTip(
            category="MCP",
            title="清晰的注释与类型注解是 MCP Tool 的灵魂",
            content="大模型在判断是否调用某个 Tool 时，依赖的是函数名、类型定义以及 Docstring 描述，越清晰越容易被准确调用。"
        ),
        ProgrammingTip(
            category="Python",
            title="使用 Pydantic 规范结构化交互",
            content="在 FastMCP 中使用 Pydantic BaseModel 作为输入输出，能让模型获得严格的 JSON Schema 提示并自动完成数据校验。"
        ),
        ProgrammingTip(
            category="架构设计",
            title="单一职责原则 (SRP)",
            content="每个 MCP Tool 应当保持专注与简洁，方便大模型根据复杂的任务链条进行灵活的多工具组合调用。"
        )
    ]
    import random
    return random.choice(tips)


# ======================================================================
# 第二支柱: Resources (资源)
# 资源是静态或只读的数据上下文，类似文件或只读 API，客户端/模型可以主动拉取
# ======================================================================

@mcp.resource("memo://all")
def get_all_memos_resource() -> str:
    """获取当前所有备忘录的完整格式化列表（只读资源）。"""
    lines = ["# 备忘录知识库清单", f"更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for m in MEMO_STORE:
        lines.append(f"### [{m.id}] {m.title} ({m.category})")
        lines.append(f"- 创建时间: {m.created_at}")
        lines.append(f"- 内容: {m.content}")
        lines.append("")
    return "\n".join(lines)


@mcp.resource("memo://stats")
def get_memo_stats_resource() -> str:
    """获取备忘录知识库的统计分析数据（只读资源）。"""
    total = len(MEMO_STORE)
    categories: dict[str, int] = {}
    for m in MEMO_STORE:
        categories[m.category] = categories.get(m.category, 0) + 1

    stats = {
        "service_name": "Smart Memo & Utilities MCP",
        "total_memos": total,
        "categories_breakdown": categories,
        "timestamp": datetime.datetime.now().isoformat()
    }
    return json.dumps(stats, ensure_ascii=False, indent=2)


@mcp.resource("memo://category/{category_name}")
def get_memos_by_category_resource(category_name: str) -> str:
    """动态资源模板：根据分类名称读取属于该分类的所有备忘录。

    Args:
        category_name (str): 分类名称，例如 '学习' 或 '生活'
    """
    matched = [m for m in MEMO_STORE if m.category == category_name]
    if not matched:
        return f"分类「{category_name}」下暂无任何备忘录。"

    lines = [f"# 分类「{category_name}」下的备忘录 ({len(matched)} 条)", ""]
    for m in matched:
        lines.append(f"- [{m.id}] **{m.title}**: {m.content} ({m.created_at})")
    return "\n".join(lines)


# ======================================================================
# 第三支柱: Prompts (提示词模板)
# 预先定义工作流的 Prompt 模版，客户端可以一键将结构化 Prompt 注入给模型
# ======================================================================

@mcp.prompt()
def summarize_memos_prompt(focus_category: str = "学习") -> str:
    """生成对特定分类备忘录进行知识梳理和行动计划制定的提示词模板。

    Args:
        focus_category (str): 重点梳理的分类名称，默认 '学习'
    """
    relevant = [m for m in MEMO_STORE if m.category == focus_category]
    memo_text = "\n".join([f"- {m.title}: {m.content}" for m in relevant])

    return f"""请扮演一位专业的知识管理与学习教练。
下面是关于分类「{focus_category}」的现有备忘录清单：
{memo_text if memo_text else "(暂无该分类条目)"}

请帮我执行以下任务：
1. 提炼并归纳这些备忘录的核心知识要点与关键概念。
2. 指出其中知识结构的不足或可以进一步深入探索的方向。
3. 输出一份清晰的下一步行动指南与学习复盘计划。
"""


@mcp.prompt()
def explain_concept_prompt(concept: str, target_audience: str = "初学者") -> str:
    """生成概念拆解与教学指导的提示词模板。

    Args:
        concept (str): 需要解释的概念（例如 'FastMCP 的三种原语'）
        target_audience (str): 目标受众群体（如 '初学者'、'高级工程师'）
    """
    return f"""你是一位富有耐心且深入浅出的导师。
请向【{target_audience}】解释概念：『{concept}』。

要求：
1. 核心定义：用一句话通俗解释其本质。
2. 生动类比：使用一个贴近日常生活的比喻。
3. 实际案例：结合具体的代码或应用场景演示如何使用。
4. 常见误区：指出初学者容易踩坑的地方并给出避坑建议。
"""


# ======================================================================
# 主入口与运行方式
# ======================================================================

def main():
    parser = argparse.ArgumentParser(description="运行 Smart Memo & Utilities MCP 服务")
    parser.add_argument(
        "--transport",
        choices=["sse", "stdio"],
        default="sse",
        help="传输协议: 'sse' (HTTP网络服务模式，默认) 或 'stdio' (命令行子进程模式)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="SSE 模式绑定的 IP 地址 (默认: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="SSE 模式监听的端口 (默认: 8001，避免与 8000 端口冲突)"
    )
    args = parser.parse_args()

    if args.transport == "sse":
        logger.info("启动 MCP 服务 [SSE 模式]: http://%s:%d/sse", args.host, args.port)
        logger.info("可运行测试脚本验证功能: uv run python src/mcp/test_learning_mcp.py")
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.info("启动 MCP 服务 [Stdio 模式]，等待标准输入输出通信...")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
