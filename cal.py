
import streamlit as st
import math
import ast
import operator
import re

# -----------------------------
# Page settings
# -----------------------------
st.set_page_config(
    page_title="Iqra Mahmood | Scientific Calculator",
    page_icon="💙",
    layout="centered"
)

# -----------------------------
# Dark blue GUI
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #071426;
    color: #F1F5FF;
}
.block-container {
    max-width: 650px;
    padding-top: 1.5rem;
}
h1, h2, h3, p, label {
    color: #EAF2FF !important;
}
div[data-testid="stTextInput"] input {
    background-color: #102544 !important;
    color: white !important;
    border: 2px solid #4F8CFF !important;
    border-radius: 14px !important;
    font-size: 25px !important;
    padding: 12px !important;
}
div.stButton > button {
    background-color: #16365D;
    color: white;
    border: 1px solid #315B91;
    border-radius: 13px;
    min-height: 48px;
    font-size: 17px;
    font-weight: 600;
}
div.stButton > button:hover {
    background-color: #28558B;
    color: white;
    border-color: #81B5FF;
}
div.stButton > button[kind="primary"] {
    background-color: #4F8CFF;
    color: white;
}
.result-preview {
    color: #80B5FF;
    font-size: 20px;
    font-weight: bold;
    text-align: right;
    min-height: 28px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    "<h1 style='text-align:center;color:#80B5FF !important;'>"
    "✦ Iqra Mahmood ✦</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;'>SCIENTIFIC CALCULATOR 💙</p>",
    unsafe_allow_html=True
)

# -----------------------------
# Session state
# -----------------------------
if "calculator_input" not in st.session_state:
    st.session_state.calculator_input = ""

if "calculator_error" not in st.session_state:
    st.session_state.calculator_error = ""

if "last_answer" not in st.session_state:
    st.session_state.last_answer = "0"

# -----------------------------
# Accurate trigonometric functions
# Angles are in DEGREES
# -----------------------------
def clean_trig_result(value):
    nearest_integer = round(value)
    if math.isclose(value, nearest_integer,
                    rel_tol=0.0, abs_tol=1e-15):
        return float(nearest_integer)
    return value


def sin_degrees(angle):
    return clean_trig_result(
        math.sin(math.radians(angle))
    )


def cos_degrees(angle):
    return clean_trig_result(
        math.cos(math.radians(angle))
    )


def tan_degrees(angle):
    radians = math.radians(angle)

    if math.isclose(
        math.cos(radians), 0.0,
        rel_tol=0.0, abs_tol=1e-15
    ):
        raise ValueError("tan is undefined at this angle.")

    return clean_trig_result(math.tan(radians))


SCIENTIFIC_FUNCTIONS = {
    "sin": sin_degrees,
    "cos": cos_degrees,
    "tan": tan_degrees,
    "sqrt": math.sqrt,
    "ln": math.log,
    "log": math.log10,
    "abs": abs,
    "exp": math.exp,
}

CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}

OPERATIONS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

UNARY_OPERATIONS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# -----------------------------
# Safe mathematical evaluator
# -----------------------------
def evaluate(node):
    if isinstance(node, ast.Expression):
        return evaluate(node.body)

    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float):
            return float(node.value)
        raise ValueError("Invalid number")

    if isinstance(node, ast.Name):
        if node.id in CONSTANTS:
            return CONSTANTS[node.id]
        raise ValueError("Unknown constant")

    if isinstance(node, ast.UnaryOp):
        operation = type(node.op)
        if operation not in UNARY_OPERATIONS:
            raise ValueError("Invalid operator")
        return UNARY_OPERATIONS[operation](
            evaluate(node.operand)
        )

    if isinstance(node, ast.BinOp):
        operation = type(node.op)

        if operation not in OPERATIONS:
            raise ValueError("Invalid operator")

        left = evaluate(node.left)
        right = evaluate(node.right)

        if isinstance(node.op, ast.Div) and right == 0:
            raise ZeroDivisionError(
                "Cannot divide by zero."
            )

        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Power is too large.")

        if (
            isinstance(node.op, ast.Pow)
            and left < 0
            and not float(right).is_integer()
        ):
            raise ValueError(
                "Negative number with fractional power is invalid."
            )

        result = OPERATIONS[operation](left, right)

        if isinstance(result, complex) or not math.isfinite(result):
            raise ValueError("Invalid result")

        return result

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Invalid function")

        name = node.func.id

        if name not in SCIENTIFIC_FUNCTIONS:
            raise ValueError("Unknown function")

        if len(node.args) != 1 or node.keywords:
            raise ValueError("Function needs one number.")

        argument = evaluate(node.args[0])

        if name == "sqrt" and argument < 0:
            raise ValueError("Square root of a negative number is invalid.")

        if name in ("log", "ln") and argument <= 0:
            raise ValueError("Logarithm requires a number greater than zero.")

        result = SCIENTIFIC_FUNCTIONS[name](argument)

        if not math.isfinite(result):
            raise ValueError("Invalid result")

        return result

    raise ValueError("Invalid expression")


# -----------------------------
# Calculate expression
# -----------------------------
def calculate(expression):
    expression = expression.strip()

    if not expression:
        raise ValueError("Enter a calculation.")

    # Convert calculator symbols
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("−", "-")
    expression = expression.replace("^", "**")
    expression = expression.replace("π", "pi")
    expression = expression.replace("√", "sqrt")

    # Automatically close missing brackets
    open_brackets = expression.count("(")
    close_brackets = expression.count(")")

    if close_brackets > open_brackets:
        raise ValueError("Check your brackets.")

    if open_brackets > close_brackets:
        expression += ")" * (open_brackets - close_brackets)

    # Allow only safe mathematical characters
    if not re.fullmatch(
        r"[0-9A-Za-z_+\-*/().%\s]+", expression
    ):
        raise ValueError("Invalid characters.")

    if len(expression) > 256:
        raise ValueError("Calculation is too long.")

    tree = ast.parse(expression, mode="eval")

    if sum(1 for _ in ast.walk(tree)) > 100:
        raise ValueError("Calculation is too long.")

    result = evaluate(tree)

    if not math.isfinite(result):
        raise ValueError("Invalid result.")

    return result


# -----------------------------
# Button actions
# -----------------------------
def press_button(label):
    expression = st.session_state.calculator_input

    if label == "AC":
        st.session_state.calculator_input = ""
        st.session_state.calculator_error = ""
        return

    if label == "DEL":
        st.session_state.calculator_input = expression[:-1]
        st.session_state.calculator_error = ""
        return

    if label == "=":
        try:
            result = calculate(expression)
            answer = f"{result:.12g}"

            st.session_state.calculator_input = answer
            st.session_state.last_answer = answer
            st.session_state.calculator_error = ""

        except Exception as error:
            st.session_state.calculator_error = str(error)

        return

    if label == "Ans":
        label = st.session_state.last_answer

    st.session_state.calculator_input += label
    st.session_state.calculator_error = ""


def sanitize_input():
    expression = st.session_state.calculator_input

    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("−", "-")
    expression = expression.replace("π", "pi")
    expression = expression.replace("√", "sqrt")

    st.session_state.calculator_input = expression
    st.session_state.calculator_error = ""


# -----------------------------
# Calculator display
# -----------------------------
with st.container(border=True):

    st.markdown(
        "<h3 style='text-align:center;'>My Calculator</h3>",
        unsafe_allow_html=True
    )

    st.text_input(
        "Calculator display",
        key="calculator_input",
        placeholder="Example: sin(90)",
        label_visibility="collapsed",
        on_change=sanitize_input
    )

    # Live preview without displaying error messages
    expression = st.session_state.calculator_input
    preview = ""

    if expression.strip():
        try:
            preview = f"= {calculate(expression):.12g}"
        except Exception:
            preview = ""

    st.markdown(
        f"<div class='result-preview'>{preview}</div>",
        unsafe_allow_html=True
    )

    st.write("")

    # Scientific buttons
    scientific_rows = [
        ["sin(", "cos(", "tan(", "sqrt("],
        ["log(", "ln(", "(", ")"],
        ["x²", "x³", "^", "π"],
    ]

    for row_index, row in enumerate(scientific_rows):
        columns = st.columns(4)

        for column, label in zip(columns, row):
            if label == "x²":
                value = "**2"
            elif label == "x³":
                value = "**3"
            else:
                value = label

            column.button(
                label,
                key=f"sci_{row_index}_{label}",
                use_container_width=True,
                on_click=press_button,
                args=(value,)
            )

    st.write("")

    # Number and operator buttons
    button_rows = [
        ["AC", "DEL", "%", "÷"],
        ["7", "8", "9", "×"],
        ["4", "5", "6", "−"],
        ["1", "2", "3", "+"],
        ["Ans", "0", ".", "="],
    ]

    for row_index, row in enumerate(button_rows):
        columns = st.columns(4)

        for column, label in zip(columns, row):
            columns_label = label

            column.button(
                columns_label,
                key=f"btn_{row_index}_{label}",
                use_container_width=True,
                type="primary" if label == "=" else "secondary",
                on_click=press_button,
                args=(label,)
            )

    if st.session_state.calculator_error:
        st.error(st.session_state.calculator_error)

st.caption("Press Enter in the display or click = to calculate.")
st.caption("Made with 💙 by Iqra Mahmood")
