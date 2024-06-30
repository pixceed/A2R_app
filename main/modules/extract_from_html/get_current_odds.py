import requests
from bs4 import BeautifulSoup
import datetime
import os
import codecs
import re
from typing import Literal
from enum import Enum
import pandas as pd
from main.modules.extract_from_html.constants import (
    CATEGORY_SET_BEFOREINFO_MP,
    CATEGORY_SET_MP,
    CATEGORY_SET_RACERESULT_MP,
)
import numpy as np
import random
import time


# dataディレクトリのpath
DIR_DATA_PATH = "../../../../data/html"


def create_data_path_str(
    race_num: int = 1,
    joh_code: int = 4,
    yearday_8keta: datetime = datetime.datetime(2024, 1, 4),
):
    """3連単オッズ表のデータとファイルのフルパスを作成します"""
    dir_path = (
        DIR_DATA_PATH
        + "/"
        + "odds3t"
        + "/"
        + str(joh_code).zfill(2)
        + "/"
        + str(yearday_8keta.year)
        + "/"
        + yearday_8keta.strftime("%m%d")
    )
    file_path = dir_path + "/" + str(race_num).zfill(2) + ".html"
    return dir_path, file_path


def query_html_and_save(
    race_num: int = 1,
    joh_code: int = 4,
    yearday_8keta: datetime = datetime.datetime(2024, 1, 4),
) -> bool | None:
    """htmlをクエリしてローカルに保存します。
    ！！注意！！既存ファイルが存在しても上書き保存します。"""
    # URLを作成
    url = (
        "https://www.boatrace.jp/owpc/pc/race/odds3t"
        + "?rno="
        + str(race_num)
        + "&jcd="
        + str(joh_code).zfill(2)
        + "&hd="
        + yearday_8keta.strftime("%Y%m%d")
    )
    print(url)
    # Requestsを使って、URLからHTMLを取得
    response = requests.get(url)
    if "表示条件を変更してもう一度処理を行ってください。" in response.text:
        return False
    # エラーがあればここで例外を発生させる
    response.raise_for_status()
    # ディレクトリとファイル名のfull pathを作成
    dir_full_path, filename_full_path = create_data_path_str(
        race_num, joh_code, yearday_8keta
    )
    # yearのディレクトリがなければ作成
    os.makedirs(dir_full_path, exist_ok=True)
    # HTMLデータをローカルファイルに保存
    with open(filename_full_path, "w", encoding="utf-8") as file:
        file.write(response.text)
    return True


def zenkaku_to_hankaku(text: str) -> str:
    """全角文字列をすべて半角文字列に変換します"""
    return text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))


def johcode_to_place(johcode: int = 4) -> str:
    place = ""
    if johcode == 1:
        place = "桐生"
    elif johcode == 2:
        place = "戸田"
    elif johcode == 3:
        place = "江戸川"
    elif johcode == 4:
        place = "平和島"
    elif johcode == 5:
        place = "多摩川"
    elif johcode == 6:
        place = "浜名湖"
    elif johcode == 7:
        place = "蒲郡"
    elif johcode == 8:
        place = "常滑"
    elif johcode == 9:
        place = "津"
    elif johcode == 10:
        place = "三国"
    elif johcode == 11:
        place = "琵琶湖"
    elif johcode == 12:
        place = "住之江"
    elif johcode == 13:
        place = "尼崎"
    elif johcode == 14:
        place = "鳴門"
    elif johcode == 15:
        place = "丸亀"
    elif johcode == 16:
        place = "児島"
    elif johcode == 17:
        place = "宮島"
    elif johcode == 18:
        place = "徳山"
    elif johcode == 19:
        place = "下関"
    elif johcode == 20:
        place = "若松"
    elif johcode == 21:
        place = "芦屋"
    elif johcode == 22:
        place = "福岡"
    elif johcode == 23:
        place = "唐津"
    elif johcode == 24:
        place = "大村"
    return place


def get_int_from_str(input_str: str) -> str:
    pattern = r"\d+\.\d+|\d+"
    match = re.search(pattern, input_str)
    if match:
        return match.group()
    else:
        return "0"


def extract_data_from_localHTML_odds(
    race_num: int = 1,
    joh_code: int = 4,
    yearday_8keta: datetime = datetime.datetime(2024, 1, 4),
):
    """ローカルのhtmlファイルのオッズ表からデータを取得します"""
    # key:コース枠番号, value:racerの登録番号
    _, file_path = create_data_path_str(race_num, joh_code, yearday_8keta)
    if not os.path.exists(file_path):
        return pd.DataFrame()
    with codecs.open(file_path, "r", "utf-8") as file:
        # BeautifulSoupオブジェクトを作成し、parserとしてhtml.parserを使用
        html_content = file.read()
    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(html_content, "html.parser")
    # 3連単オッズの表を特定
    odds_table = soup.find_all("tbody")[1]  # 必要に応じてインデックスを調整
    # オッズデータを抽出し辞書形式に変換
    odds_data = {}
    first_key = 1
    second_keys = []
    for row in odds_table.find_all("tr"):
        # odds_data[key] = value
        left_col = row.find_all("td", class_="is-borderLeftNone")
        if len(left_col) > 0:
            # first_keyとsecond_keysとthird_keysを更新
            first_key = 1
            second_keys = []
            all_left = row.find_all("td")
            index = 0
            while index <= len(all_left) - 1:
                second_key = int(all_left[index].get_text())
                second_keys.append(second_key)
                index += 1
                third_key = int(all_left[index].get_text())
                index += 1
                value = float(all_left[index].get_text())
                index += 1
                odds_data.setdefault(first_key, {})
                odds_data[first_key].setdefault(second_key, {})
                odds_data[first_key][second_key][third_key] = value
                first_key += 1
        else:
            # first_keyとthird_keysを更新
            first_key = 1
            all_td = row.find_all("td")
            index = 0
            second_key_index = 0
            while index <= len(all_td) - 1:
                second_key = second_keys[second_key_index]
                third_key = int(all_td[index].get_text())
                index += 1
                value = float(all_td[index].get_text())
                index += 1
                odds_data.setdefault(first_key, {})
                odds_data[first_key].setdefault(second_key, {})
                odds_data[first_key][second_key][third_key] = value
                first_key += 1
                second_key_index += 1
    # for a in odds_data:
    #     print(str(a) + ":")
    #     for b in odds_data[a]:
    #         print("  " + str(b) + ":")
    #         for c in odds_data[a][b]:
    #             print("    " + str(c) + ":" + str(odds_data[a][b][c]))
    return odds_data


def extract_data_from_localHTML_odds_3rp(
    race_num: int = 1,
    joh_code: int = 4,
    yearday_8keta: datetime = datetime.datetime(2024, 1, 4),
):
    """ローカルのhtmlファイルのオッズ表からデータを取得します"""
    # key:コース枠番号, value:racerの登録番号
    _, file_path = create_data_path_str(race_num, joh_code, yearday_8keta)
    if not os.path.exists(file_path):
        return pd.DataFrame()
    with codecs.open(file_path, "r", "utf-8") as file:
        # BeautifulSoupオブジェクトを作成し、parserとしてhtml.parserを使用
        html_content = file.read()
    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(html_content, "html.parser")
    # 3連単オッズの表を特定
    odds_table = soup.find_all("tbody")[1]  # 必要に応じてインデックスを調整
    # オッズデータを抽出し辞書形式に変換
    odds_data = {}
    first_key = 1
    second_keys = []
    for row in odds_table.find_all("tr"):
        # odds_data[key] = value
        left_col = row.find_all("td", class_="is-fs14")
        if len(left_col) > 0:
            # first_keyとsecond_keysとthird_keysを更新
            first_key = 1
            second_keys = []
            all_left = row.find_all("td")
            index = 0
            while index <= len(all_left) - 1:
                second_key = int(all_left[index].get_text())
                second_keys.append(second_key)
                index += 1
                third_key = int(all_left[index].get_text())
                index += 1
                value = float(all_left[index].get_text())
                index += 1
                odds_data.setdefault(first_key, {})
                odds_data[first_key].setdefault(second_key, {})
                odds_data[first_key][second_key][third_key] = value
                first_key += 1
        else:
            # first_keyとthird_keysを更新
            first_key = 1
            all_td = row.find_all("td")
            index = 0
            second_key_index = 0
            while index <= len(all_td) - 1:
                second_key = second_keys[second_key_index]
                third_key = int(all_td[index].get_text())
                index += 1
                value = float(all_td[index].get_text())
                index += 1
                odds_data.setdefault(first_key, {})
                odds_data[first_key].setdefault(second_key, {})
                odds_data[first_key][second_key][third_key] = value
                first_key += 1
                second_key_index += 1
    # for a in odds_data:
    #     print(str(a) + ":")
    #     for b in odds_data[a]:
    #         print("  " + str(b) + ":")
    #         for c in odds_data[a][b]:
    #             print("    " + str(c) + ":" + str(odds_data[a][b][c]))
    return odds_data



def query_1race_odds_and_generate_dataframe(
    race_num: int = 1,
    jcd_code: int = 4,
    target_date: datetime = datetime.datetime(2024, 1, 4),
    should_download: bool = False,
):
    if should_download:
        query_html_and_save(race_num, jcd_code, target_date)
    try:
        target_dict = extract_data_from_localHTML_odds(race_num, jcd_code, target_date)
        return target_dict
    except Exception:
        print("Error in data extraction")
        return {}


if __name__ == "__main__":
    # table[1着の艇盤][2着の艇盤][3着の艇盤] = オッズの倍率
    table = query_1race_odds_and_generate_dataframe(
        race_num=12, jcd_code=12, target_date=datetime.datetime(2024, 6, 16)
    )
    print(table)
