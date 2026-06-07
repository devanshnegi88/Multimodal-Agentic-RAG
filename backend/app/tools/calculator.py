"""Calculator tool for numeric operations."""
import ast, math, operator

SAFE_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.USub: operator.neg,
}

def _eval(node):
    if isinstance(node, ast.Constant): return node.value
    elif isinstance(node, ast.BinOp):
        op = SAFE_OPERATORS.get(type(node.op))
        if op: return op(_eval(node.left), _eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        op = SAFE_OPERATORS.get(type(node.op))
        if op: return op(_eval(node.operand))
    raise ValueError(f"Unsupported operation: {ast.dump(node)}")

class CalculatorTool:
    name = "calculator"
    description = "Evaluate mathematical expressions safely."
    def run(self, expression: str) -> str:
        try:
            tree = ast.parse(expression, mode='eval')
            result = _eval(tree.body)
            return str(result)
        except Exception as e:
            return f"Error: {e}"
