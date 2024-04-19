from app.models import db, User, Enrollment
from sqlalchemy.sql import func
import os
import joblib
# 데이터 처리, 행렬, 배열 모듈
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
# from sklearn.preprocessing import LabelEncoder
from scipy.sparse import hstack, csr_matrix
# 텍스트 벡터화 모듈
# from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec, KeyedVectors
# 불용어 처리
from konlpy.tag import Okt
# 코사인 유사도를 위한 모듈
from sklearn.metrics.pairwise import cosine_similarity

# 0. 학습시킨 Word2vec 모델 로드하기
def load_model():
  parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
  model_path = os.path.join(parent_dir, 'w2v_model_for_use.pkl')
  model = joblib.load(model_path)
  return model

# 0. life_stage별 csv 파일 로드하기
def load_csv_file():
  parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
  static_folder_path = os.path.join(parent_dir, 'static')

  life_stage_df = {
    'UNI' : pd.read_csv(os.path.join(static_folder_path, 'uni_final.csv')),
    'NEW_JOB' : pd.read_csv(os.path.join(static_folder_path, 'new_job_final.csv')),
    'NEW_WED' : pd.read_csv(os.path.join(static_folder_path, 'new_wed_final.csv')),
    'HAVE_CHILD' : pd.read_csv(os.path.join(static_folder_path, 'have_child_final.csv')),
    'NO_CHILD' : pd.read_csv(os.path.join(static_folder_path, 'no_child_final.csv')),
    'RETIR' : pd.read_csv(os.path.join(static_folder_path, 'retir_final.csv'))
  }
  return life_stage_df

# 1. 기존 고객 대상 아이템 기반 추천 모델링 
# 1) text_to_vector() : PRODUCT_NAME과 PRODUCT_DETAILS를 벡터로 변환하는 함수
def text_to_vector(text, model):
    okt = Okt()
    morphs = okt.morphs(text)
    stop_words = ['의','가','이','은','을','를','는','수','&','인','~','으로','자','에','와','한', '입니다', '합니다','!','에','에서','와','과','하는',',','(',')','.','도', '하여', '데', '할', '상품', '예금', '적금', '하며', '로', '된', '로', '된', '적',
              '있도록', '위', '등', '시', '및', '하세요', '-', 'e', '전용', '며', '아름','다','움', '성','장하', '하기', '과의','통해','받을','정기예금','누구','나','하고','절차','형','기본','연','계','형','금','일부','기여','로운','과의','부',
              '되는','해하','편','리하','게','있는','하게','가능','래','달','겨냥','성하','실','천자','센티','추가', '다', '장병','미니','각하','지날','받고','업','따라','모','모아서','!!','UP','쌓고','할인','쿠폰','하나원','큐','로그인','횟수','하나','합','등록',
              '따라', '여서','대상','확정','제공','운','자유','나은','금리','돕기','만을','운용','사회','절약','스타일','극대','최종','변경','가입','이고','일','참여','에게', '앞당겨', '자유로', '통장']

    # 불용어 리스트
    filtered_morphs = [morph for morph in morphs if morph not in stop_words]

    # 불용어 제거
    word_vectors = [model.wv[morph] for morph in filtered_morphs if morph in model.wv]

    # 벡터의 평균 계산
    if len(word_vectors) == 0:
        return np.zeros(model.vector_size)
    else:
        return np.mean(word_vectors, axis=0)

# 2) products_recommendation_for_existing_customers() : 코사인 유사도를 이용한 아이템 기반 추천 모델
def word2vec_recommendation_for_existing_customers(products: pd.DataFrame, target_product_id: int, life_stage: str, w2v_model):
    ohe = OneHotEncoder()
    scaler = StandardScaler()

    # Word2Vec을 사용하여 상품명과 상품 설명을 벡터화
    product_name_vec = products['PRODUCT_NAME'].apply(lambda x: text_to_vector(x, w2v_model))
    product_details_vec = products['PRODUCT_DETAIL'].apply(lambda x: text_to_vector(x, w2v_model))

    # OneHotEncoder와 StandardScaler를 사용하여 나머지 컬럼 벡터화
    products['DEPOSIT_CYCLE'] = products['DEPOSIT_CYCLE'].apply(lambda x: x.value if x else None) # Enum 타입인 DEPOSIT_CYCLE 문자형으로 변경 후 one-hot-encoding 진행
    deposit_cycle_ohe = ohe.fit_transform(products[['DEPOSIT_CYCLE']])  # 카테고리형 : one-hot-encoding
    maturity_scaled = scaler.fit_transform(products[['MATURITY']])      # 수치형 : scaling
    limit_amt_scaled = scaler.fit_transform(products[['LIMIT_AMT']])    # 수치형 : scaling
    
    # NumPy 배열로 변환
    product_name_vectors = np.stack(product_name_vec)
    product_details_vectors = np.stack(product_details_vec)

    # 통합된 특성 행렬 생성
    combined_features = np.hstack([product_name_vectors, product_details_vectors, deposit_cycle_ohe.toarray(), maturity_scaled, limit_amt_scaled])
    combined_features = csr_matrix(combined_features)

    # 결과를 저장할 리스트 초기화
    recommended_product_ids = []

    # 과거 보유했던 예금 상품에 대한 추천
    if target_product_id:
      recommended_product_ids = get_similar_products(combined_features, products, target_product_id, life_stage)
      return recommended_product_ids

    else:
      # recommendation_for_new_customers(life_stage)
      return "target_id가 없습니다."

def get_similar_products(combined_features, products, target_product_id, life_stage):
    # life_stage 연관 단어
    life_stage_words = {
      'UNI': ["청년", "18", "22", "23", "여행", "취업", "창업", "학업", "학자금", "디지털", "편리", "저축", "전자기기", "월세", "전세", "보증금", "젊은", "꿈"],
      'NEW_JOB': ["취업", "주택", "24", "청년", "첫", "직장", "신입", "반려", "디지털", "편리", "차", "투자", "저축", "여가", "월세", "전세"],
      'NEW_WED': ["주택", "차", "신혼", "가구", "부채", "투자", "30", "자녀", "공무원", "전문직", "공직자", "여가", "차"],
      'HAVE_CHILD': ["가계", "양육", "교육", "아이", "자녀", "어린이", "청소년", "Youth", "저축", "투자", "주택", "30", "40", "50", "맞벌이", "공무원", "전문직", "공직자"],
      'NO_CHILD': ["여가", "반려", "40", "50", "맞벌이", "공무원", "전문직", "공직자", "노후", "주택"],
      'RETIR': ["연금", "저축", "노후", "노년", "고령", "공무원", "전문직", "퇴직", "재취업", "여가"]
      }
    # life_stage별 제외할 단어
    life_stage_except_words = {
      'UNI': ["은퇴", "연금", "노후", "청소년", "어린이"],
      'NEW_JOB': ["은퇴", "연금", "노후", "청소년", "어린이"],
      'NEW_WED': ["은퇴", "연금", "노후", "청년"],
      'HAVE_CHILD': ["은퇴", "연금", "청년"],
      'NO_CHILD': ["은퇴", "연금", "청소년", "어린이", "청년"],
      'RETIR': ["젊은", "청소년", "어린이", "꿈", "청년"]
    }

    # 타겟 상품의 벡터 추출
    target_index = products.index[products['ID_PK'] == target_product_id].tolist()[0]
    target_features = combined_features[target_index]

    # 코사인 유사도 계산
    cosine_similarities = cosine_similarity(target_features, combined_features).flatten()
    # 자기 자신의 유사도는 제외
    cosine_similarities[target_index] = -1

    # 유사도가 높은 순서대로 상품의 인덱스 정렬
    similar_indices = np.argsort(cosine_similarities)[::-1]

    # 1) 제외할 단어가 포함된 상품 필터링 후 유사도 높은 20개의 상품만 선별
    except_keywords = life_stage_except_words[life_stage]
    product_details = products['PRODUCT_NAME'] + " " + products['PRODUCT_DETAIL']
    exclude_flags = product_details.apply(lambda x: any(word in x for word in except_keywords))
    filtered_indices = [idx for idx in similar_indices if not exclude_flags.iloc[idx]][:20]

    # 2) life_stage별 연관 단어 포함 검사
    keywords = life_stage_words[life_stage]
    product_details = products['PRODUCT_NAME'] + " " + products['PRODUCT_DETAIL']
    flags = product_details.apply(lambda x: any(word in x for word in keywords))

    high_priority_indices = [idx for idx in filtered_indices if flags.iloc[idx]]        # 연관 단어 포함 상품
    low_priority_indices = [idx for idx in filtered_indices if not flags.iloc[idx]]     # 연관 단어 미포함 상품

    # 우선순위 재조정된 인덱스
    reordered_indices = high_priority_indices + low_priority_indices
    
    # 상위 5개 상품 index 반환
    top_n_product_index = reordered_indices[:5]

    # # 상위 5개의 상품 ID 반환
    # top_n_product_ids = products.iloc[reordered_indices]['ID_PK'].values[:5]

    return top_n_product_index


# 2. 충분한 고객 특징 데이터가 확보된 기존 고개을 위한 유사 군집 보유 상품 추천 모델 (SEQ 있는 고객)
# similar_customer_recommendation_for_exist_customer() : 비슷한 특징을 가지고 있는 고객이 과거에 보유했던 상품들 추려서 상위 3개씩 노출
def similar_customer_recommendation_for_exist_customer(seq: str, life_stage: str, life_stage_df: pd.DataFrame):
    df = life_stage_df[life_stage]
    customer_cluster = df.loc[df["SEQ"] == seq, "CLUSTER"].iloc[0]  # 가장 처음 분기

    # 접속한 고객과 동일한 군집에 속해 있는 고객 특징 추출
    cluster_deposits = df.loc[df["CLUSTER"]==customer_cluster, "PREVIOUS_DEPOSIT"].head(3).tolist()
    cluster_savings = df.loc[df["CLUSTER"]==customer_cluster, "PREVIOUS_SAVINGS"].head(3).tolist()
    return cluster_deposits + cluster_savings


# 3. 신규 고객을 위한 추천 모델
# recommendation_for_new_customers() : 신규 고객 대상 상품 기반 추천 알고리즘, 동일 생애주기 고객들이 과거에 많이 보유했던 top5 상품 출력
def recommendation_for_new_customers(user_id):
    # 사용자의 life_stage 찾기
    user = User.query.get(user_id)
    if not user:
        return None, "가입되지 않은 고객입니다."

    # 같은 life_stage를 가진 다른 사용자의 Enroll 데이터 조회
    results = db.session.query(
        Enrollment.PRODUCT_ID_FK,
        func.count(Enrollment.PRODUCT_ID_FK).label('count')
    ).join(User).filter(
        User.LIFE_STAGE == user.LIFE_STAGE,
        User.ID_PK != user_id  # 자기 자신을 제외
    ).group_by(Enrollment.PRODUCT_ID_FK
    ).order_by(func.count(Enrollment.PRODUCT_ID_FK).desc()
    ).limit(5).all()  # 상위 5개 상품 가져오기

    if results:
        top5_products_id = [result.PRODUCT_ID_FK for result in results]
        return top5_products_id
    else:
        return None