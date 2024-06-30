import pandas as pd
import numpy as np


def calc_expectation(odds: dict, probabilities: dict, num_choose: int):
    expectation_list = []
    for first in odds:
        for second in odds[first]:
            for third in odds[first][second]:
                one_expectation = {}
                one_odds = odds[first][second][third]

                # first が1位になる確率
                first_prob = probabilities[first][1]
                # second が2位になる確率
                second_prob = probabilities[second][2]
                # third が3位になる確率
                third_prob = probabilities[third][3]

                
                # # first が1位になる確率
                # first_prob = probabilities[first][1]
                # # second が2位になる確率
                # second_prob = probabilities[second][1]
                # # third が3位になる確率
                # third_prob = probabilities[third][1]

                # 期待値
                expectation = one_odds * first_prob * second_prob * third_prob
                one_expectation["first"] = first
                one_expectation["second"] = second
                one_expectation["third"] = third
                one_expectation["expectation"] = expectation
                one_expectation["odds"] = one_odds
                expectation_list.append(one_expectation)

    # sort : 期待値 -> 1着の艇番 -> 2着の艇番 -> 3着の艇番
    expectation_sorted_list = sorted(
        expectation_list,
        key=lambda x: (x["expectation"], x["first"], x["second"], x["third"], x["odds"]),
        reverse=True,
    )
    return expectation_sorted_list[:num_choose]


if __name__ == "__main__":
    print("hello")
