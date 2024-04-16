# 라우트 및 라우트 핸들러를 정의하는 파일
from flask import Blueprint, request, jsonify, current_app
from app.models import *   # DB 모델 임포트

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