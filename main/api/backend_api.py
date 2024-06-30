import datetime
import pickle
import pandas as pd
import lightgbm as lgb

from flask import Blueprint, request

from main.modules.extract_from_html.get_current_html \
    import query_1race_info_and_generate_dataframe

from main.modules.extract_from_html.get_current_odds \
    import query_1race_odds_and_generate_dataframe

from main.modules.extract_from_html.calc_expectation \
    import calc_expectation

try:

    with open('test.txt', 'w') as f:
        f.write('もいもい')
except Exception as e:
    with open('test.txt', 'w') as f:
        f.write(str(e))


backend_api = Blueprint('backend_api', __name__)

@backend_api.route('/your-backend-endpoint', methods=['POST'])
def backend_process():

    # データを受け取る
    json = request.get_json()
    jcd = json['jcd']
    race_num = json['racenum']
    year = int(json['date'].split('-')[0])
    month = int(json['date'].split('-')[1])
    day = int(json['date'].split('-')[2])
    should_dl = json['should_dl']

    # レース情報を取得
    target_df = query_1race_info_and_generate_dataframe(
        race_num=race_num,
        jcd_code=jcd,
        target_date=datetime.datetime(year, month, day),
        should_download=should_dl,
    )

    # データを加工
    preprocess_df = preprocess_data(target_df)

    # LightGBMモデルを読み込み
    model_path = "main/lgb_models/mrnk_model.pkl"
    with open(model_path, "rb") as fp:
        model = pickle.load(fp)    

    # 予測
    pred = model.predict(preprocess_df, num_iteration=model.best_iteration)
    
    # 辞書型に変換
    # pred_dict = {
    #     1: pred[0].tolist(),

    #     2: pred[1].tolist(),
    #     3: pred[2].tolist(),
    #     4: pred[3].tolist(),
    #     5: pred[4].tolist(),
    #     6: pred[5].tolist(),
    # }

    pred_dict = {}
    for i, player_pred in enumerate(pred):
        pred_dict[i+1] = {}
        for j, p in enumerate(player_pred):
            pred_dict[i+1][j+1] = float(p)

    # オッズデータの取得
    odds_data = query_1race_odds_and_generate_dataframe(
        race_num=race_num,
        jcd_code=jcd,
        target_date=datetime.datetime(year, month, day),
        should_download=should_dl,
    )

    # 期待値の計算
    expectation = calc_expectation(odds_data, pred_dict, 120)

    try:

        expectation_result = ""
        for i, e in enumerate(expectation):
            except_result = e['expectation']
            odds = e['odds']
            order3t = f"{e['first']} - {e['second']} - {e['third']}"
            expectation_result += f"{i+1}位: {order3t} 期待値: {except_result} オッズ: {odds}\n"

        with open('test.txt', 'w') as f:
            f.write(str(pred_dict))
    
    except Exception as e:

        with open('test.txt', 'w') as f:
            f.write(str(e))

    return expectation


# データを加工する関数
def preprocess_data(target_df):

    df = target_df.loc[:, [
        'souban', 'touban', 'age', 'weight', 'grade', 'allwin', 'allniren',
        'localwin', 'localniren', 'motor', 'motorniren', 'boat', 'boatniren',
        'weather', 'wind_strength', 'wind_direction', 'temperature', 'water_temperature',
        'wave_height', 'mod_weight', 'exhibition_time', 'tilt',
        ]]
    
    weader_label = {
        '晴': 0,
        '曇り': 1,
        '雨': 2,
        '雪': 3,
    }

    grade_label = {
        'A1': 0,
        'A2': 1,
        'B1': 2,
        'B2': 3,
    }

    df['age'] = df['age'].replace('歳', '', regex=True).astype(int)
    df['weight'] = df['weight'].replace('kg', '', regex=True).astype(float)
    df['grade'] = df['grade'].replace(grade_label)
    df['weather'] = df['weather'].replace(weader_label)

    df = df.astype(float)

    return df