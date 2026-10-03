import streamlit as st
import math


# -----------------------------
# Page settings
# -----------------------------

st.set_page_config(
    page_title="Scientific Calculator",
    layout="centered"
)

st.title("Scientific Calculator")


# -----------------------------
# Session State
# -----------------------------

if "display" not in st.session_state:
    st.session_state.display = ""


# -----------------------------
# Calculator functions
# -----------------------------

def calculate(numbers, operator):

    match operator:

        case "+":
            total = 0

            for number in numbers:
                total += number

            return total

        case "-":
            result = numbers[0]

            for number in numbers[1:]:
                result -= number

            return result

        case "*":
            result = 1

            for number in numbers:
                result *= number

            return result

        case "/":
            result = numbers[0]

            for number in numbers[1:]:

                if number == 0:
                    return "Cannot divide by zero"

                result /= number

            return result


def scientific(number, operation):

    match operation:

        case "√":
            return math.sqrt(number)

        case "x²":
            return number ** 2

        case "x³":
            return number ** 3

        case "sin":
            return math.sin(math.radians(number))

        case "cos":
            return math.cos(math.radians(number))

        case "tan":
            return math.tan(math.radians(number))

        case "log":
            return math.log10(number)

        case "ln":
            return math.log(number)


# -----------------------------
# Button function
# -----------------------------

def press_button(value):

    if value == "C":

        st.session_state.display = ""

    else:

        st.session_state.display += value


# -----------------------------
# Equal function
# -----------------------------

def press_equal():

    try:

        expression = st.session_state.display

        if "+" in expression:

            parts = expression.split("+")

            numbers = []

            for part in parts:
                numbers.append(float(part))

            result = calculate(numbers, "+")


        elif "*" in expression:

            parts = expression.split("*")

            numbers = []

            for part in parts:
                numbers.append(float(part))

            result = calculate(numbers, "*")


        elif "/" in expression:

            parts = expression.split("/")

            numbers = []

            for part in parts:
                numbers.append(float(part))

            result = calculate(numbers, "/")


        elif "-" in expression:

            parts = expression.split("-")

            numbers = []

            for part in parts:
                numbers.append(float(part))

            result = calculate(numbers, "-")


        else:

            result = float(expression)


        st.session_state.display = str(result)

    except:

        st.session_state.display = "Error"


# -----------------------------
# Calculator body
# -----------------------------

with st.container(border=True):

    # Display

    st.text_input(
        "Display",
        key="display",
        label_visibility="collapsed",
        placeholder="0"
    )


    st.write("")


    # -------------------------
    # Scientific buttons
    # -------------------------

    scientific_buttons = [
        "sin",
        "cos",
        "tan",
        "√",
        "x²",
        "x³",
        "log",
        "ln"
    ]


    for i in range(0, len(scientific_buttons), 4):

        columns = st.columns(4)

        for j in range(4):

            button = scientific_buttons[i + j]

            if columns[j].button(
                button,
                width="stretch"
            ):

                try:

                    number = float(
                        st.session_state.display
                    )

                    result = scientific(
                        number,
                        button
                    )

                    st.session_state.display = str(result)

                except:

                    st.session_state.display = "Error"


    st.write("")


    # -------------------------
    # Number buttons
    # -------------------------

    buttons = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["C", "0", ".", "+"]
    ]


    for row in buttons:

        columns = st.columns(4)

        for i in range(4):

            button = row[i]

            columns[i].button(
                button,
                width="stretch",
                on_click=press_button,
                args=(button,)
            )


    st.write("")


    # -------------------------
    # Equal button
    # -------------------------

    st.button(
        "=",
        type="primary",
        width="stretch",
        on_click=press_equal
    )