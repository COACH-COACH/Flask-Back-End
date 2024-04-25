import pandas as pd
# 라우트 및 라우트 핸들러를 정의하는 파일
from flask import Blueprint, request, jsonify, current_app
from app.models import *  # DB 모델 임포트
# service 모델 임포트
from app.services.product_recommendation import load_model, load_csv_file, word2vec_recommendation_for_existing_customers, recommendation_for_new_customers, similar_customer_recommendation_for_exist_customer
from app.services.product_preprocessing import product_preprocessing


recommendation = Blueprint('recommendation', __name__, url_prefix="/recommendation")

@recommendation.route('/<int:user_id>', methods=['GET', 'POST'])
def show_recommendations(user_id):
    # 접속한 고객의 user 정보 불러오기
    user = User.query.filter_by(ID_PK=user_id).first()
    if user is None:
        return jsonify({'error': '가입되지 않은 고객입니다.'}), 404
    
    # user table에서 seq 불러오기
    seq = user.SEQ
    # user table에서 life_stage 불러오기
    # LifeStage Enum을 문자열로 변환
    life_stage = user.LIFE_STAGE.value if user.LIFE_STAGE else None
    
    # target_product_id : 고객이 가장 최근에 가입한 상품
    latest_enrollment = Enrollment.query.filter_by(USER_ID_FK=user_id).order_by(Enrollment.START_DATE.desc()).first()
    
    # Products 테이블을 데이터 프레임 형식으로 가져오기 및 전처리
    products_origin = pd.read_sql(Product.query.statement, db.engine)
    products_origin = product_preprocessing(products_origin)
    # 중복 상품 제거
    products = products_origin.drop_duplicates(subset=["PRODUCT_NAME"], keep='first')
    
    # 1. 과거 상품 가입 이력이 존재하는 고객
    if latest_enrollment and latest_enrollment.PRODUCT_ID_FK:
        # 추천 모델 실행
        # 0) 미리 학습시킨 w2v_model 불러오기
        w2v_model = load_model()
        # 1) 아이템 기반 추천 알고리즘 실행
        recommended_product_index = word2vec_recommendation_for_existing_customers(
            products,
            latest_enrollment.PRODUCT_ID_FK,
            life_stage,
            w2v_model
        )
        recommended_products = products.iloc[recommended_product_index].loc[:, ["ID_PK", "PRODUCT_NAME", "MAX_INTEREST_RATE", "MATURITY"]]
        recommended_products_dict = recommended_products.to_dict(orient='records')
        
        # 1-2. 충분한 고객 특징 데이터가 확보된 기존 고객을 위한 유사 군집 보유 상품 추천 모델 (SEQ 있는 고객)
        if seq :
            life_stage_df = load_csv_file()
            cluster_products_id = similar_customer_recommendation_for_exist_customer(seq, life_stage, life_stage_df)
            cluster_products = products.loc[products["ID_PK"].isin(cluster_products_id), ["ID_PK", "PRODUCT_NAME", "MAX_INTEREST_RATE", "MATURITY"]]
            cluster_products_dict = cluster_products.to_dict(orient='records')
            return jsonify({
                'item_recommendations' : recommended_products_dict,
                'cluster_recommendations': cluster_products_dict})
        
        # 1-3. 과거이력이 생긴 신규 고객 (과거 이력은 있지만 SEQ 없는 고객)
        else :
            return jsonify({'item_recommendations' : recommended_products_dict})

    # 2. 신규 고객을 위한 추천 시스템
    # elif latest_enrollment is None and latest_enrollment.PRODUCT_ID_FK is None:
    elif not latest_enrollment or not latest_enrollment.PRODUCT_ID_FK:
        products_id = recommendation_for_new_customers(user_id)
        if products_id :
            if products_id in products['ID_PK'].values.tolist():
                products_for_new = products.loc[products['ID_PK'].isin(products_id), ["ID_PK", "PRODUCT_NAME", "MAX_INTEREST_RATE", "MATURITY"]]
                products_for_new_dict = products_for_new.to_dict(orient='records')
                return jsonify({'static_recommendations': products_for_new_dict})
            # 없으면 products_original에서 같은 상품명 찾기
            else:
                product_name = products_origin.loc[products_origin["ID_PK"].isin(products_id), "PRODUCT_NAME"]
                products_for_new = products.loc[products["PRODUCT_NAME"].isin(product_name), ["ID_PK", "PRODUCT_NAME", "MAX_INTEREST_RATE", "MATURITY"]]
                products_for_new_dict = products_for_new.to_dict(orient='records')
                return jsonify({'static_recommendations': products_for_new_dict})
        else:
            return jsonify({'error' : '동일 생애주기에 있는 다른 고객님들의 과거 가입 상품이 존재하지 않습니다.'})
        
    # 3. 해당 사용자를 찾을 수 없거나, 사용자의 ENROLL_TB 정보가 없음
    else:
        return jsonify({'error': 'User not found'}), 404