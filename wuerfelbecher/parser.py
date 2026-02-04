import re
from collections import namedtuple
from pprint import pprint
from lark import Lark, Transformer, v_args

SetToRoll = namedtuple("SetToRoll", ["count", "dice_type", "modifier", "selected"])

grammar = """
    start: roll+
    roll: count dice sides [modifier] [modifier_number] [selector]

    count: INT
    dice: "d"
    sides: INT
    modifier: SIGN
    modifier_number: INT
    selector: "(" INT ")"

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
    def to_rollingset(self, children):
        print(children)
        count = children[0]
        # children[1] is dice ("d"), we skip it
        sides = children[2]

        # Extract optionals
        modifier = None
        modifier_number = None
        selector = None

        for child in children[3:]:
            if isinstance(child, str) and child in ['+', '-']:
                modifier = child
            elif isinstance(child, int):
                if modifier is not None and modifier_number is None:
                    modifier_number = child
                else:
                    selector = child

        # Calculate final modifier
        final_modifier = None
        if modifier and modifier_number is not None:
            final_modifier = modifier_number if modifier == "+" else -modifier_number

        selected = selector if selector is not None else 1

        if selected > count:
            selected = count

        return SetToRoll(count, sides, final_modifier, selected)

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
