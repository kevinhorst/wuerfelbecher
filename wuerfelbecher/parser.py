import re
from collections import namedtuple
from pprint import pprint
from lark import Lark, Transformer, v_args

SetToRoll = namedtuple("SetToRoll", ["count", "dice_type",  "selector", "modifier", "modifier_number", "actions"])

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
        # children[1] is dice ("d"), we skip it
        sides = children[2]

        # Extract optionals
        selector = None
        modifier = None
        modifier_number = None
        actions = []
        print("len(children)", len(children))
        print(children)
        # one optional, may be
        # (1) modifier = ["+ | "-"] (ACTION_SUM),
        # (2) selector = "(INT)"(ACTION_SELECT)
        if len(children) == 4:
            child = children[3]
            # 1
            if isinstance(child, str) and child in ['+', '-']:
                modifier = child
                actions.append('ACTION_SUM')
            # 2
            elif isinstance(child, int):
                selector = child
                actions.append('ACTION_SELECT')

        # two optionals, may be
        #(1) modifier+number (ACTION_SUM + ACTION_ADD or ACTION_SUB),
        #(2) modifier+selector (ACTION_SUM + ACTION_ADD or ACTION_SUB),
        #(3) selector+modifier(ACTION_SELECT),
        if len(children) == 5:
            first = children[3]
            second = children[4]
            # 1, 2
            if isinstance(first, str) and first in ['+', '-'] and isinstance(second, int):
                modifier = first
                actions.append('ACTION_SUM')
                if modifier == '+':
                    actions.append('ACTION_ADD')
                else:
                    actions.append('ACTION_SUB')
                modifier_number = second
            # 3
            if isinstance(first, int) and second in ['+', '-'] and isinstance(second, str):
                selector = first
                actions.append('ACTION_SELECT')

        # three optionals, may be
        # (1) modifier+number+selector (ACTION_SUM + ACTION_ADD or ACTION_SUB)
        # (2) selector+modifier+number (ACTION_SELECT + ACTION_ADD or ACTION_SUB)
        if len(children) == 6:
            first = children[3]
            second = children[4]
            third = children[5]
            # 1
            if isinstance(first, str) and first in ['+', '-'] and isinstance(second, int):
                modifier = first
                actions.append('ACTION_SUM')
                if modifier == '+':
                    actions.append('ACTION_ADD')
                else:
                    actions.append('ACTION_SUB')
                modifier_number = second
            # 2
            if isinstance(first, int) and second in ['+', '-'] and isinstance(second, str) and isinstance(third, int):
                selector = first
                actions.append('ACTION_SELECT')
                modifier = second
                if modifier == '+':
                    actions.append('ACTION_ADD')
                else:
                    actions.append('ACTION_SUB')
                modifier_number = third

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
