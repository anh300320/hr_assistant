from enum import Enum, auto
from typing import Self

from src.common.exceptions import InvalidBooleanException


class Operator(Enum):
    AND = "AND"
    OR = "OR"


class BooleanSearch:

    def __init__(self, value = None) -> None:
        self.left: Self | None = None
        self.right: Self | None = None
        self.value: str | Operator | None = value

    def _op(self, other: Self, operator: Operator) -> Self:
        new_bool = BooleanSearch()
        new_bool.left = self
        new_bool.right = other
        new_bool.value = operator
        return new_bool

    def __and__(self, other: Self) -> Self:
        return self._op(other, Operator.AND)

    def __or__(self, other: Self) -> Self:
        return self._op(other, Operator.OR)


def _tokenize_boolean_query(query: str) -> list[str]:
    tokens = []
    current_token = ""
    for i in range(len(query)):

        if not query[i].isalnum():
            if current_token:
                tokens.append(current_token)
            if query[i] in ["(", ")"]:
                tokens.append(query[i])
            current_token = ""
            continue

        current_token += query[i]

    if current_token:
        tokens.append(current_token)

    current = []
    operators = [op.value for op in Operator]
    operators.extend(["(", ")"])
    grouped_tokens = []
    for token in tokens:
        if token in operators:
            if current:
                grouped_tokens.append(" ".join(current))
            grouped_tokens.append(token)
            current = []
        else:
            current.append(token)

    if current:
        grouped_tokens.append(" ".join(current))

    return grouped_tokens


def _postfix_expression(
    tokens: list[str],
) -> list[str]:
    output = []
    ops = []
    operators = [c.value for c in Operator]
    for i, token in enumerate(tokens):
        if token in operators:
            while ops and ops[-1] != "(":
                last_op = ops.pop()
                output.append(last_op)
            ops.append(token)
        elif token == "(":
            ops.append(token)
        elif token == ")":
            while ops and ops[-1] != "(":
                last_op = ops.pop()
                output.append(last_op)
            if ops:
                ops.pop()
        else:
            output.append(token)

    while ops:
        output.append(ops.pop())

    return output


def _evaluate_postfix(tokens: list) -> BooleanSearch:
    values: list[BooleanSearch] = []
    operators = [c.value for c in Operator]
    for token in tokens:
        if token not in operators:
            values.append(BooleanSearch(token))
        else:
            first_value = values.pop()
            second_value = values.pop()
            if Operator(token) == Operator.AND:
                value = first_value & second_value
            else:
                value = first_value | second_value
            values.append(value)
    return values.pop()


def parse_raw_boolean_search(query: str) -> BooleanSearch:
    tokens = _tokenize_boolean_query(query)
    postfix = _postfix_expression(tokens)
    result = _evaluate_postfix(postfix)
    return result
