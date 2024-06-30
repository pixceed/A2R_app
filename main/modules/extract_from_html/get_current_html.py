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
# from constants import (
#     CATEGORY_SET_BEFOREINFO_MP,
#     CATEGORY_SET_MP,
#     CATEGORY_SET_RACERESULT_MP,
# )
import numpy as np
import random
import time


class RaceInfo(Enum):
    list = "racelist"
    beforeinfo = "beforeinfo"


RACE_INFO_LITERAL = Literal[RaceInfo.list, RaceInfo.beforeinfo]
# dataディレクトリのpath
DIR_DATA_PATH = "../../../../data/html"

def create_data_path_str(
    race_num: int = 1,
    joh_code: int = 4,
    yearday_8keta: datetime = datetime.datetime(2024, 1, 4),
    info_kind: RACE_INFO_LITERAL = RaceInfo.list.value,
):
    """レース番号、場コード、日付情報から、データとファイルのフルパスを作成します"""
    dir_path = (
        DIR_DATA_PATH
        + "/"
        + info_kind
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
    info_kind: RACE_INFO_LITERAL = RaceInfo.list.value,
) -> bool | None:
    """htmlをクエリしてローカルに保存します。
    ！！注意！！既存ファイルが存在しても上書き保存します。"""
    # URLを作成
    url = (
        "https://www.boatrace.jp/owpc/pc/race/"
        + info_kind
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
        race_num, joh_code, yearday_8keta, info_kind
    )
    # yearのディレクトリがなければ作成
    if not os.path.exists(dir_full_path):
        os.makedirs(dir_full_path)
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


def extract_data_from_localHTML_racelist(
    race_num: int = 1,
    joh_code: int = 4,
    yearday_8keta: datetime = datetime.datetime(2024, 1, 4),
):
    """ローカルのhtmlファイルの出走表からデータを取得します"""
    # key:コース枠番号, value:racerの登録番号
    race_info = []
    _, file_path = create_data_path_str(race_num, joh_code, yearday_8keta)
    if not os.path.exists(file_path):
        return pd.DataFrame()
    with codecs.open(file_path, "r", "utf-8") as file:
        # BeautifulSoupオブジェクトを作成し、parserとしてhtml.parserを使用
        soup = BeautifulSoup(file, "html.parser")
        # レース名
        race = soup.find_all("h2")[0].get_text().strip()
        race_info.append(race)
        # 何日目
        race_daycounts = soup.find_all("ul", class_="tab2_tabs")[0]
        race_daycount = (
            soup.find("li", class_="is-active2")
            .find("span")
            .find("span")
            .get_text()
            .strip()
        )
        race_daycount_int = 1
        if race_daycount == "初日":
            race_daycount_int = 1
        elif race_daycount == "最終日":
            a = race_daycounts.find_all("a")[-2].find("span").get_text(strip=True)
            number = get_int_from_str(a)
            race_daycount_int = int(zenkaku_to_hankaku(number)) + 1
        elif race_daycount == "順延":
            junn_ei_day = 1
            for one_day in race_daycounts.find_all("span", class_=""):
                if one_day.get_text() == "順延":
                    race_daycount_int = junn_ei_day
                    break
                junn_ei_day += 1
        else:
            race_daycount_int = int(get_int_from_str(zenkaku_to_hankaku(race_daycount)))
        race_info.append(race_daycount_int)
        # 開催日
        race_info.append(yearday_8keta.strftime("%Y/%m/%d"))
        # 開催場所
        race_info.append(joh_code)
        # ラウンド番号
        race_info.append(race_num)
        # コース長
        course_len = soup.find_all("h3")[0].get_text(separator=" ", strip=True).split()
        race_info.append(int(get_int_from_str(course_len[-1])))

        # 選手と成績情報が載っているタグを抽出
        styled_content_divs = soup.find_all(
            "div", class_="table1 is-tableFixed__3rdadd"
        )
        # 要素が1つだけでない場合は例外raiseする
        if len(styled_content_divs) != 1:
            raise Exception()
        # 各選手のデータを格納
        each_racer = styled_content_divs[0].find_all("tbody")
        # 各レーサー
        racer_info = {}
        for one_racer in each_racer:
            # レーサーの基本情報オブジェクトのみを取得
            one_racer_row = one_racer.find_all("tr")[0]
            # コース番号
            lane_region = one_racer_row.find_all("td", class_="is-fs14")
            lane_num_str = zenkaku_to_hankaku(lane_region[0].get_text(strip=True))
            racer_info[int(lane_num_str)] = []
            # 登録番号と級別
            racer_info_html = one_racer_row.find_all("td")[2]
            register_region = racer_info_html.find_all("div", class_="is-fs11")[0]
            # divタグのテキスト全体を取得し、改行やスペースを削除
            text = register_region.get_text(strip=True)
            grade = register_region.find_all("span")[0].get_text()
            # 正規表現で数字部分だけを抽出
            toban = get_int_from_str(text)
            racer_info[int(lane_num_str)].append(toban)
            player = racer_info_html.find("a").get_text().replace("　", "")
            racer_info[int(lane_num_str)].append(player)
            # 支部と出身地と年齢と体重
            info_text = racer_info_html.find_all("div", class_="is-fs11")[1].get_text(
                strip=True
            )
            pattern = re.compile(
                r"(?P<branch>.+?)/(?P<birthplace>.+?)(?P<age>\d+歳)/(?P<weight>\d+(\.\d+)?kg)"
            )
            match = pattern.match(info_text)
            branch = match.group("branch")
            birthplace = match.group("birthplace")
            age = match.group("age")
            weight = match.group("weight")
            racer_info[int(lane_num_str)].append(age)
            racer_info[int(lane_num_str)].append(branch)
            racer_info[int(lane_num_str)].append(weight)
            racer_info[int(lane_num_str)].append(
                grade
            )  # アーカイブデータと合わせるため
            # 成績
            records = one_racer_row.find_all("td", class_="is-lineH2")
            # 全国
            national_victory_rate = records[1].decode_contents().split("<br/>")
            # 全国勝率
            racer_info[int(lane_num_str)].append(national_victory_rate[0].strip())
            # 全国2連率
            racer_info[int(lane_num_str)].append(national_victory_rate[1].strip())
            # 当地
            local_victory_rate = records[2].decode_contents().split("<br/>")
            # 当地勝率
            racer_info[int(lane_num_str)].append(local_victory_rate[0].strip())
            # 当地2連率
            racer_info[int(lane_num_str)].append(local_victory_rate[1].strip())
            # モーター
            motor_victory_rate = records[3].decode_contents().split("<br/>")
            # モーター勝率
            racer_info[int(lane_num_str)].append(motor_victory_rate[0].strip())
            # モーター2連率
            racer_info[int(lane_num_str)].append(motor_victory_rate[1].strip())
            # ボート
            boat_victory_rate = records[4].decode_contents().split("<br/>")
            # ボート勝率
            racer_info[int(lane_num_str)].append(boat_victory_rate[0].strip())
            # ボート2連率
            racer_info[int(lane_num_str)].append(boat_victory_rate[1].strip())
        df = pd.DataFrame()
        for one_racer_info_key in racer_info:
            one_racer_info = [one_racer_info_key] + racer_info[one_racer_info_key]
            df_temp = pd.DataFrame(
                np.asarray(race_info + one_racer_info).reshape(1, -1),
                columns=CATEGORY_SET_MP,
            )
            df = pd.concat([df, df_temp])
        return df


def extract_data_from_localHTML_beforeinfo(
    race_num: int = 1,
    joh_code: int = 4,
    yearday_8keta: datetime = datetime.datetime(2024, 1, 3),
):
    """ローカルのhtmlファイルの直前情報からデータを取得します"""
    _, file_path = create_data_path_str(
        race_num, joh_code, yearday_8keta, RaceInfo.beforeinfo.value
    )
    df_race = pd.DataFrame()
    if not os.path.exists(file_path):
        return df_race
    with codecs.open(file_path, "r", "utf-8") as file:
        race_info = []
        # BeautifulSoupオブジェクトを作成し、parserとしてhtml.parserを使用
        soup = BeautifulSoup(file, "html.parser")
        # レース名
        race = soup.find_all("h2")[0].get_text().strip()
        race_info.append(race)
        # 何日目
        race_daycounts = soup.find_all("ul", class_="tab2_tabs")[0]
        race_daycount = (
            soup.find("li", class_="is-active2")
            .find("span")
            .find("span")
            .get_text()
            .strip()
        )
        race_daycount_int = 1
        if race_daycount == "初日":
            race_daycount_int = 1
        elif race_daycount == "最終日":
            a = race_daycounts.find_all("a")[-2].find("span").get_text(strip=True)
            number = get_int_from_str(a)
            race_daycount_int = int(zenkaku_to_hankaku(number)) + 1
        elif race_daycount == "順延":
            junn_ei_day = 1
            for one_day in race_daycounts.find_all("span", class_=""):
                if one_day.get_text() == "順延":
                    race_daycount_int = junn_ei_day
                    break
                junn_ei_day += 1
        else:
            race_daycount_int = int(zenkaku_to_hankaku(get_int_from_str(race_daycount)))
        race_info.append(race_daycount_int)
        # 開催日
        race_info.append(yearday_8keta.strftime("%Y/%m/%d"))
        # 開催場所
        race_info.append(joh_code)
        # ラウンド番号
        race_info.append(race_num)
        # コース長
        course_len = soup.find_all("h3")[0].get_text(separator=" ", strip=True).split()
        course_len_int = int(get_int_from_str(course_len[-1]))
        race_info.append(course_len_int)

        # 各選手のデータを格納
        each_racer = soup.find_all("tbody")
        racer_info = []
        for racer_num in range(1, 7):
            # 欠場の選手はスキップする
            if "is-miss" in each_racer[racer_num].get("class"):
                continue
            td_all = each_racer[racer_num].find_all("td")
            souban = int(td_all[0].get_text())
            player_name = td_all[2].get_text().replace("　", "").replace(" ", "")
            mod_weight = float(
                each_racer[racer_num].find_all("tr")[2].find("td").get_text()
            )
            exhibition_time = float(td_all[4].get_text())
            tilt = float(td_all[5].get_text())
            one_racer_info = [souban, player_name, mod_weight, exhibition_time, tilt]
            racer_info.append(one_racer_info)
        # 天気などの環境の情報
        wind_direction_class = soup.find_all("p", class_="weather1_bodyUnitImage")[
            -1
        ].get("class")[-1]
        weather_str = soup.find_all("span", class_="weather1_bodyUnitLabelTitle")[
            1
        ].get_text()
        weather_info = soup.find_all("span", class_="weather1_bodyUnitLabelData")
        wind_strength = float(get_int_from_str(weather_info[1].get_text()))
        wind_direction = int(get_int_from_str(wind_direction_class))
        temperature = float(get_int_from_str(weather_info[0].get_text()))
        water_temperature = float(get_int_from_str(weather_info[2].get_text()))
        wave_height = float(get_int_from_str(weather_info[3].get_text()))
        env_info = [
            weather_str,
            wind_strength,
            wind_direction,
            temperature,
            water_temperature,
            wave_height,
        ]

        # 各レーサーのデータをそれぞれ1レコードとしてDataframeを作成する
        for one_racer in racer_info:
            data = np.asarray(race_info + env_info + one_racer).reshape(1, -1)
            df_temp = pd.DataFrame(data, columns=CATEGORY_SET_BEFOREINFO_MP)
            df_race = pd.concat([df_race, df_temp])

    return df_race


def get_merged_dataframe(
    race_num=1, joh_code=4, yearday_8keta=datetime.datetime(2024, 1, 3)
):
    try:
        racelist = extract_data_from_localHTML_racelist(
            race_num=race_num, joh_code=joh_code, yearday_8keta=yearday_8keta
        )
        if len(racelist) == 0:
            return racelist
        beforeinfo = extract_data_from_localHTML_beforeinfo(
            race_num=race_num, joh_code=joh_code, yearday_8keta=yearday_8keta
        )
        if len(beforeinfo) == 0:
            return beforeinfo
    except Exception:
        return pd.DataFrame()

    # racelist と beforeinfoの情報をmerge
    category_common = []
    for racelist_col in racelist.columns:
        if racelist_col in beforeinfo.columns:
            category_common.append(racelist_col)
            racelist[racelist_col] = racelist[racelist_col].astype(str)
            beforeinfo[racelist_col] = beforeinfo[racelist_col].astype(str)
    merged_df = pd.merge(racelist, beforeinfo, on=category_common, how="inner")
    return merged_df


def query_1race_info_and_generate_dataframe(
    race_num: int = 1,
    jcd_code: int = 4,
    target_date: datetime = datetime.datetime(2024, 1, 4),
    should_download: bool = False,
):
    output_csv_tail_name = "whole_data.csv"
    if should_download:
        for info_kind in RaceInfo:
            # 出走表/事前情報をダウンロード
            _ = query_html_and_save(
                race_num=race_num,
                joh_code=jcd_code,
                yearday_8keta=target_date,
                info_kind=info_kind.value,
            )
    try:
        target_df = get_merged_dataframe(race_num, jcd_code, target_date)
        print(target_df)
    except Exception:
        print("Error in merging")
    
    return target_df


if __name__ == "__main__":
    target_df = query_1race_info_and_generate_dataframe(
        race_num=1,
        jcd_code=4,
        target_date=datetime.datetime(2024, 6, 15),
        should_download=True,
    )

    print(target_df)
