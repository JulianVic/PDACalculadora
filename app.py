from dataclasses import dataclass
from typing import Optional, Union, Dict, Any
from flask import Flask, render_template, request, jsonify
from lark import Lark, Transformer, v_args

app = Flask(__name__)

MATH_GRAMMAR = """
    ?start: expr
    ?expr: term
        | expr "+" term   -> addition
        | expr "-" term   -> subtraction
    ?term: factor
        | term "*" factor -> multiplication
        | term "/" factor -> division
    ?factor: NUMBER       -> number
        | "(" expr ")"
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

@dataclass
class Node:
    value: Union[float, str]
    left: Optional['Node'] = None
    right: Optional['Node'] = None

class MathExpressionParser(Transformer):
    @v_args(inline=True)
    def number(self, n: str) -> Node:
        return Node(float(n))
    
    def _create_operation_node(self, args: list, operator: str) -> Node:
        return Node(operator, args[0], args[1])
    
    def addition(self, args: list) -> Node:
        return self._create_operation_node(args, '+')
    
    def subtraction(self, args: list) -> Node:
        return self._create_operation_node(args, '-')
    
    def multiplication(self, args: list) -> Node:
        return self._create_operation_node(args, '*')
    
    def division(self, args: list) -> Node:
        return self._create_operation_node(args, '/')

class ExpressionEvaluator:
    def __init__(self):
        self.parser = Lark(MATH_GRAMMAR, parser='lalr', transformer=MathExpressionParser())
    
    def parse_expression(self, expression: str) -> Dict[str, Any]:
        try:
            tree = self.parser.parse(expression)
            result = eval(expression)  # En un entorno de producción, deberías implementar tu propio evaluador seguro
            return {"result": result, "tree": tree}
        except Exception as e:
            return {"error": str(e)}

class MathAPI:
    def __init__(self):
        self.evaluator = ExpressionEvaluator()
    
    def process_request(self, expression: str) -> Dict[str, Any]:
        return self.evaluator.parse_expression(expression)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        expression = request.form.get("expression")
        math_api = MathAPI()
        return jsonify(math_api.process_request(expression))
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)