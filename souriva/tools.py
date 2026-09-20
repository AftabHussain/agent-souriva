import ast
import operator
from collections.abc import Callable
from dataclasses import asdict

from souriva.rag import FaissStore

_BINARY: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def calculator(expression: str) -> float:
    """Evaluate arithmetic syntax without names, calls, or attribute access."""
    if len(expression) > 200:
        raise ValueError("Expression is too long")
    tree = ast.parse(expression, mode="eval")

    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
            left, right = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 12:
                raise ValueError("Exponent is too large")
            return _BINARY[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
            return _UNARY[type(node.op)](evaluate(node.operand))
        raise ValueError("Only numeric arithmetic is allowed")

    result = evaluate(tree)
    if abs(result) > 1e100:
        raise ValueError("Result is too large")
    return result


class DocumentTools:
    """Approved tool surface shared by the agent and MCP transport."""

    def __init__(self, store: FaissStore) -> None:
        self.store = store

    def search_documents(self, query: str, top_k: int = 4) -> list[dict]:
        return [asdict(item) for item in self.store.search(query, top_k=top_k)]

    def get_document_chunk(self, chunk_id: str) -> dict | None:
        chunk = self.store.get(chunk_id)
        return chunk.to_dict() if chunk else None

    def calculator(self, expression: str) -> float:
        return calculator(expression)
