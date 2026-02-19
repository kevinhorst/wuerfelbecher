import random

from lark import  UnexpectedToken

from . import dice_roller, parser, statistics
from .parser import ACTION_SELECT, ACTION_SUM, ACTION_ADD


def roll(message: str) -> str:
    try:
        parsed = parser.parse_roll(message.lower())

        rolls = []
        for _ in range(parsed.count):
            rolls.append(dice_roller.roll_dice(parsed.dice_type))

        help_text = ""
        if len(parsed.actions) > 0:
            help_text = "*Rolled* : "
            help_text += "[ **" + "  ".join([str(i) for i in rolls]) + "** ]" + "\n"

        modified = rolls
        if ACTION_SELECT in  parsed.actions:
            print("ACTION SELECT")
            print(modified)
            random.shuffle(modified)
            print("Shuffled:")
            print(modified)

            print("selected")
            modified = [modified[parsed.selector-1]]
            print(modified)
            help_text += "*Selected dice* : " + "**" +str(parsed.selector) + "**" + "\n"

        if ACTION_SUM in parsed.actions:
            print("ACTION SUM")
            print(modified)

            modified = [sum(modified)]
            print("summed")
            print(modified)
            help_text += "*Summed all rolls*: **yes**"  + "\n"

        if ACTION_ADD in parsed.actions:
            print("ACTION ADD")
            print(modified)
            modified = list(map(lambda r: r + parsed.modifier_number, modified))
            print("Added:")
            print(modified)
            help_text += "*Added to result* : " + "**" + str(parsed.modifier_number) + "**" + "\n"

        print_help = True
        out = "*Result*: [ **" + "  ".join([str(i) for i in modified]) + "** ]"

        if print_help:
            out = help_text + out

        return out.strip()
    except ValueError:
        return "That did not work. Ask for *!help*"
    except UnexpectedToken:
        return "Failed to parse dice roll. Wrong format. Ask for *!help*"


def stats(message: str) -> str:
    try:
        number_of_sides = parser.parse_stats(message.lower())
        rolls, counts = statistics.get_stats(number_of_sides)
        p = 1.0 / number_of_sides
        return "```You rolled the d{0} {1} times. Those are the results including how many standard deviations (σ) the result deviates from the expectation value:\n{2}```".format(  # noqa: E501
            number_of_sides,
            rolls,
            "".join(
                [
                    "{0:>3}: {1:>3}  ({2:.2f}σ)\n".format(
                        i,
                        counts[i],
                        statistics.binomial_std_deviations(
                            counts[i],
                            statistics.binomial_expectation_value(rolls, p),
                            statistics.binomial_variance(rolls, p),
                        ),
                    )
                    for i in range(1, number_of_sides + 1)
                ]
            ),
        )
    except ValueError:
        return "That did not work. Ask for *!help*"
