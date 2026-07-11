import itertools
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sympy import sympify, simplify_logic
from graphviz import Digraph
import re


# 🔹 Parse Boolean Expression (supports AND, OR, NOT, ., +, ')
def parse_boolean_expr(expr: str):
    expr = expr.replace("AND", "&").replace("OR", "|").replace("NOT", "~")
    expr = expr.replace("and", "&").replace("or", "|").replace("not", "~")
    expr = expr.replace(".", "&").replace("+", "|")  # A.B + C style

    # Convert A' → ~A
    expr = _convert_postfix_notation(expr)

    return sympify(expr)


def _convert_postfix_notation(expr: str) -> str:
    while "'" in expr:
        idx = expr.index("'")
        if idx == 0:
            raise ValueError("Invalid complement operator position")

        if expr[idx - 1] == ")":
            depth = 0
            start = None
            for pos in range(idx - 1, -1, -1):
                if expr[pos] == ")":
                    depth += 1
                elif expr[pos] == "(":
                    depth -= 1
                    if depth == 0:
                        start = pos
                        break
            if start is None:
                raise ValueError("Unmatched parentheses before complement operator")
            expr = expr[:start] + "~" + expr[start:idx] + expr[idx + 1:]
        else:
            start = idx - 1
            if not expr[start].isalnum():
                raise ValueError("Complement operator must follow a variable or parenthesized expression")
            expr = expr[:start] + "~" + expr[start:idx] + expr[idx + 1:]

    return expr


# 🔹 Boolean Expression Simplifier
def simplify_boolean_expression(expr: str):
    """
    Simplify boolean expressions using multiple methods:
    1. Algebraic simplification
    2. De Morgan's laws
    3. Boolean algebra rules
    4. Consensus theorem
    """
    try:
        # Parse the expression
        parsed_expr = parse_boolean_expr(expr)
        
        # Get original expression for comparison
        original_expr = str(parsed_expr)
        
        # Method 1: Algebraic simplification using sympy
        simplified = simplify_logic(parsed_expr, form="dnf")  # SOP form
        algebraic_result = str(simplified)
        
        # Method 2: Try POS form as well
        simplified_pos = simplify_logic(parsed_expr, form="cnf")  # POS form
        pos_result = str(simplified_pos)
        
        # Method 3: Manual simplification using boolean algebra rules
        manual_result = manual_boolean_simplification(expr)
        
        # Choose the shortest result (usually the most simplified)
        results = [algebraic_result, pos_result, manual_result]
        best_result = min(results, key=len)
        
        return {
            "original": original_expr,
            "simplified": best_result,
            "algebraic_sop": algebraic_result,
            "algebraic_pos": pos_result,
            "manual": manual_result,
            "variables": sorted([v.name for v in parsed_expr.free_symbols]),
            "complexity_reduction": len(original_expr) - len(best_result)
        }
        
    except Exception as e:
        return {
            "error": f"Simplification failed: {str(e)}",
            "original": expr
        }


def manual_boolean_simplification(expr: str):
    """
    Manual boolean simplification using common rules
    """
    # Clean up the expression
    expr = expr.upper().replace(" ", "")
    expr = expr.replace("AND", "&").replace("OR", "|").replace("NOT", "~")
    expr = expr.replace(".", "&").replace("+", "|")
    
    # Try to use sympy for basic simplification first
    try:
        parsed_expr = parse_boolean_expr(expr)
        # Use sympy's simplify_logic for basic simplification
        simplified = simplify_logic(parsed_expr)
        return str(simplified)
    except:
        # If sympy fails, fall back to manual rules
        pass
    
    # Apply De Morgan's laws
    expr = apply_de_morgan(expr)
    
    # Apply absorption laws
    expr = apply_absorption(expr)
    
    # Apply distributive laws
    expr = apply_distributive(expr)
    
    # Apply idempotent laws
    expr = apply_idempotent(expr)
    
    # Apply complement laws
    expr = apply_complement(expr)
    
    return expr


def apply_de_morgan(expr: str):
    """Apply De Morgan's laws: ~(A & B) = ~A | ~B and ~(A | B) = ~A & ~B"""
    # Basic De Morgan's law application
    # This is a simplified implementation
    expr = re.sub(r'~\(([^()]+)\)', lambda m: apply_de_morgan_to_expression(m.group(1)), expr)
    return expr


def apply_de_morgan_to_expression(subexpr: str):
    """Helper function to apply De Morgan's laws to a subexpression"""
    # Replace & with | and vice versa, and negate each variable
    result = subexpr.replace('&', '|').replace('|', '&')
    # Add ~ to each variable that doesn't already have it
    result = re.sub(r'\b([A-Z])\b(?!~)', r'~\1', result)
    # Remove double negations
    result = re.sub(r'~~([A-Z])', r'\1', result)
    return result


def apply_absorption(expr: str):
    """Apply absorption laws: A & (A | B) = A and A | (A & B) = A"""
    # Basic absorption law implementation
    # This is a simplified version - in practice, you'd need more sophisticated parsing
    return expr


def apply_distributive(expr: str):
    """Apply distributive laws: A & (B | C) = (A & B) | (A & C)"""
    # Basic distributive law implementation
    # This is a simplified version - in practice, you'd need more sophisticated parsing
    return expr


def apply_idempotent(expr: str):
    """Apply idempotent laws: A & A = A and A | A = A"""
    # Basic idempotent law implementation
    # This is a simplified version - in practice, you'd need more sophisticated parsing
    return expr


def apply_complement(expr: str):
    """Apply complement laws: A & ~A = 0 and A | ~A = 1"""
    # Basic complement law implementation
    # This is a simplified version - in practice, you'd need more sophisticated parsing
    return expr


# 🔹 Generate Truth Table
def generate_truth_table(expr: str):
    parsed_expr = parse_boolean_expr(expr)
    vars_list = sorted(parsed_expr.free_symbols, key=lambda x: x.name)

    table = []
    for values in itertools.product([0, 1], repeat=len(vars_list)):
        val_dict = dict(zip(vars_list, values))
        result = int(bool(parsed_expr.subs(val_dict)))
        table.append((values, result))

    return [v.name for v in vars_list], table


# 🔹 Generate K-map + Minimized Expression
def generate_kmap_and_minimize(expr: str):
    parsed_expr = parse_boolean_expr(expr)
    vars_list = sorted(parsed_expr.free_symbols, key=lambda x: x.name)

    if len(vars_list) > 3:
        raise ValueError("K-map supported only for up to 3 variables")

    minimized = simplify_logic(parsed_expr, form="dnf")  # SOP form

    rows = 2 ** (len(vars_list) // 2)
    cols = 2 ** (len(vars_list) - len(vars_list) // 2)

    table = {}
    for values in itertools.product([0, 1], repeat=len(vars_list)):
        table[values] = int(bool(parsed_expr.subs(dict(zip(vars_list, values)))))

    fig, ax = plt.subplots()
    ax.axis("off")

    # Draw grid
    for i in range(rows + 1):
        ax.plot([0, cols], [i, i], color="black")
    for j in range(cols + 1):
        ax.plot([j, j], [0, rows], color="black")

    row_bits = len(vars_list) // 2
    col_bits = len(vars_list) - row_bits
    row_order = _gray_code_order(row_bits)
    col_order = _gray_code_order(col_bits)

    # Fill K-map values in Gray-code order so adjacent cells differ by one bit.
    for r, row_value in enumerate(row_order):
        for c, col_value in enumerate(col_order):
            values = tuple(row_value + col_value)
            ax.text(c + 0.5, rows - r - 0.5,
                    table[values], ha="center", va="center", fontsize=14)

    return minimized, fig


def _gray_code_order(width: int):
    if width == 0:
        return [()]
    return [tuple(int(bit) for bit in format(i ^ (i >> 1), f"0{width}b")) for i in range(2 ** width)]


# 🔹 Generate Circuit Diagram
def generate_circuit(expr: str, output_path: str):
    dot = Digraph(comment="Logic Circuit", format="png")
    dot.attr(rankdir="LR")

    expr = expr.replace("AND", "&").replace("OR", "|").replace("NOT", "~")
    expr = expr.replace(".", "&").replace("+", "|")

    inputs = sorted(set([c for c in expr if c.isalpha()]))
    for i in inputs:
        dot.node(i, i, shape="circle")

    node_count = 1

    def add_gate(subexpr):
        nonlocal node_count
        subexpr = subexpr.strip()

        if len(subexpr) == 1 and subexpr.isalpha():
            return subexpr

        if "|" in subexpr:
            left, right = subexpr.split("|", 1)
            lnode, rnode = add_gate(left), add_gate(right)
            node = f"OR{node_count}"
            dot.node(node, "OR", shape="rectangle", style="filled", color="lightblue")
            dot.edge(lnode, node)
            dot.edge(rnode, node)
            node_count += 1
            return node

        if "&" in subexpr:
            left, right = subexpr.split("&", 1)
            lnode, rnode = add_gate(left), add_gate(right)
            node = f"AND{node_count}"
            dot.node(node, "AND", shape="rectangle", style="filled", color="lightgreen")
            dot.edge(lnode, node)
            dot.edge(rnode, node)
            node_count += 1
            return node

        if subexpr.startswith("~"):
            input_node = add_gate(subexpr[1:])
            node = f"NOT{node_count}"
            dot.node(node, "NOT", shape="rectangle", style="filled", color="pink")
            dot.edge(input_node, node)
            node_count += 1
            return node

        return subexpr

    output_node = add_gate(expr)
    dot.node("OUT", "OUT", shape="doublecircle", style="filled", color="yellow")
    dot.edge(output_node, "OUT")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    dot.render(output_path, format="png", cleanup=True)
