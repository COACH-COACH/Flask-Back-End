# 라우트 및 라우트 핸들러를 정의하는 파일
from flask import Flask, Blueprint, request, jsonify, current_app
from app.models import *   # DB 모델 임포트
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import logging

# Flask 애플리케이션 설정
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)  # 로그 레벨 설정

# 로거에 스트림 핸들러 추가
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

bp = Blueprint('tester', __name__)

# main_view에 user의 정보를 JSON 형태로 Get하는 예시 코드
@bp.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == "GET":
        # 모든 User 객체 가져오기
        users = User.query.all()
        print(users)
        # User 객체를 JSON으로 직렬화하여 반환

        return jsonify([user.serialize() for user in users])
    
@bp.route('/timeSeries', methods=['POST'])
def process_data():
    # 요청 로그 출력
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.data.decode('utf-8'))  # 요청 본문을 UTF-8로 디코드하여 로그로 출력

    # JSON 데이터 받기
    json_data = request.get_json()
    if json_data is None: # 올바르지 않은 JSON 형식
        return jsonify({'error': 'Invalid JSON data'}), 400

    # 받은 데이터를 이용하여 처리 로직 수행
    try:
        result = do_prediction(json_data)
        response = {'result': result}
        return jsonify(response)
    except Exception as e:
        app.logger.error('Error processing data: %s', str(e))
        return jsonify({'error': 'Error processing data'}), 500

def do_prediction(json_data):

    # JSON 데이터를 받아옴
    # data = request.json

    # JSON 데이터를 DataFrame으로 변환
    df = pd.DataFrame(json_data)

    # 데이터 정규화
    scaler = MinMaxScaler()
    df['TOT_USE_AM_normalized'] = scaler.fit_transform(df[['consumption']])

    # 시퀀스 생성 함수
    def create_sequences(data, seq_length):
        X = []
        y = []
        for i in range(len(data) - seq_length):
            X.append(data[i:i + seq_length])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)

    # 시퀀스 길이와 특징 수 설정
    seq_length = 2  # 시퀀스 길이 - 시퀀스 길이란 LSTM 모델에 입력될 때 한 번에 고려될 데이터 포인트(타임스텝)의 수
    n_features = 1  # 특징 수

    # LSTM 모델 정의
    model = Sequential([
        LSTM(50, input_shape=(seq_length, n_features)),
        Dense(1)
    ])

    # 모델 컴파일
    model.compile(optimizer='adam', loss='mse')

    # BAS_YH 열을 기준으로 데이터프레임 정렬
    df_sorted = df.sort_values(by='paymentQuarter')

    # 해당 SEQ에 대한 행의 개수 확인
    if len(df_sorted) <= 2:
        print("과거 분기 데이터가 2개 이하 : 예측에 필요한 데이터가 부족합니다.")
        return

    seq_data = df_sorted['TOT_USE_AM_normalized'].values

    # 시퀀스 생성
    X_seq, y_seq = create_sequences(seq_data, seq_length)
    X_seq = X_seq.reshape((X_seq.shape[0], X_seq.shape[1], n_features))

    # 모델 훈련
    model.fit(X_seq, y_seq, epochs=30, verbose=0)

    # # 마지막 시퀀스 데이터 가져오기
    last_seq_data = seq_data[-seq_length:].reshape((1, seq_length, n_features))

    # # 예측 수행
    predicted_data_normalized = model.predict(last_seq_data)

    # # 원래 스케일로 복원
    predicted_data = scaler.inverse_transform(predicted_data_normalized)

    # 다음 분기 소비 예측량
    return float(round(predicted_data[0][0], 2))
