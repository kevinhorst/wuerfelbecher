from . import dice_roller, parser, statistics

# TODO: must adhere selector
# TODO: must be randomized internally, selected what is displayed
# TODO: change sum logic: +-> sum all, +1 -> do not sum, add to result
# TODO: ++1 -> sum all, add +1
def roll(message: str) -> str:
    try:
        out = ""
        parsed = parser.parse_roll(message.lower())
        out += "  "
        rolls = []
        for _ in range(parsed.count):
            rolls.append(dice_roller.roll_dice(parsed.dice_type))

        out += "[ **" + "  ".join([str(i) for i in rolls]) + "** ]"
        if parsed.modifier is not None:
            print("parsed.modifier: ", parsed.modifier)

            sum_rolls = sum(rolls)
            if parsed.modifier > 0:
                out += "+" + str(parsed.modifier)
            elif parsed.modifier < 0:
                out += str(parsed.modifier)
            out += "=**" + str(sum_rolls + parsed.modifier) + "**"
        return out.lstrip().rstrip()
    except ValueError:
        return "That did not work. Ask for *!help*"


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
