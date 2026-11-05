## Restricted calculator

**Source commit:** [`1d88d7a`](https://github.com/AftabHussain/agent-souriva/commit/1d88d7a16180169c295765bfb55cfe14bcf7ba26)

### Change

Added a restricted arithmetic calculator for approved tool execution.

The recursive evaluator accepts only numeric constants and explicitly listed arithmetic nodes:

    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        left, right = evaluate(node.left), evaluate(node.right)
        return _BINARY[type(node.op)](left, right)
    raise ValueError("Only numeric arithmetic is allowed")

Names, calls, and attributes never match an allowed branch, so they are rejected instead of being evaluated as Python code.

### Architecture

The calculator is transport-independent so the agent and MCP server can share identical behavior.

### Design notes

The calculator walks a small arithmetic AST and rejects names, calls, attributes, oversized exponents, and extreme results.

### Verification

Compiled source and tests and checked the diff. Cases cover normal arithmetic and attempted code execution.

### Result

Approved arithmetic has a small, testable implementation ready for agent and MCP exposure.
