# Restricted calculator

## Change

Added a restricted arithmetic calculator for approved tool execution.

## Architecture

The calculator is transport-independent so the agent and MCP server can share identical behavior.

## Design notes

The calculator walks a small arithmetic AST and rejects names, calls, attributes, oversized exponents, and extreme results.

## Verification

Compiled source and tests and checked the diff. Cases cover normal arithmetic and attempted code execution.

## Result

Approved arithmetic has a small, testable implementation ready for agent and MCP exposure.
