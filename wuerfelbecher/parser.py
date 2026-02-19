import re
from collections import namedtuple
from pprint import pprint
from lark import Lark, Transformer, v_args

SetToRoll = namedtuple("SetToRoll", ["count", "dice_type",  "selector", "modifier_number", "actions"])

ACTION_SELECT = "select"
ACTION_SUM = "sum"
ACTION_ADD = "add"

grammar = """
    start: roll+
    roll: count dice sides [selector] [modifier] [modifier_number]

    count: INT
    dice: "d"
    sides: INT
    selector: "(" INT ")"
    modifier: SIGN
    modifier_number: INT

    INT: /[1-9][0-9]*/
    SIGN: "+" | "-"

    %import common.WS
    %ignore WS
"""


class DiceRollTransformer(Transformer):
    @v_args(inline=True)
    def INT(self, token):
        return int(token)

    @v_args(inline=True)
    def SIGN(self, token):
        return str(token)

    @v_args(inline=True)
    def count(self, value):
        return value

    def dice(self, value):
        return "d"  # Just return the string, we don't need it

    @v_args(inline=True)
    def sides(self, value):
        return value

    @v_args(inline=True)
    def modifier(self, sign):
        return sign

    @v_args(inline=True)
    def modifier_number(self, value):
        return value

    @v_args(inline=True)
    def selector(self, value):
        return value

    # Don't use inline here - get children as a list, makes getting the optional params cleaner
    #TODO: needs STATE for different cases
    def to_rollingset(self, children):
        count = children[0]
        # children[1] is "d", skip
        sides = children[2]
        selector = children[3]  # int or None
        modifier = children[4]  # "+" | "-" or None
        modifier_number = children[5]  # int or None

        actions = []

        if selector is not None:
            actions.append(ACTION_SELECT)
            selector = count if selector > count else selector

        if modifier is not None:
            actions.append(ACTION_SUM)

            if modifier_number is not None:
                modifier_number = modifier_number if modifier == '+' else -modifier_number
                actions.append(ACTION_ADD)

        return SetToRoll(count, sides, selector, modifier_number, actions)

    def start(self, children):
        return children[0]


def parse_roll(message: str) -> SetToRoll:
    message = preprocess(message)
    result = Lark(grammar, parser='lalr', transformer=DiceRollTransformer()).parse(message)
    pprint(result.children)

    return DiceRollTransformer().to_rollingset(children=result.children)


def parse_stats(message: str) -> int:
    dice_type_match = re.match(r"^[dw]([1-9][0-9]*)$", message.lstrip().rstrip())
    if dice_type_match:
        return int(dice_type_match.group(1))


def preprocess(message: str) -> str:
    stripped = message.strip()

    # Add count if missing (starts with 'd')
    if stripped.startswith('d'):
        stripped = '1' + stripped

    return stripped
