from flask import Flask, render_template, jsonify, Blueprint
import requests
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from konlpy.tag import Okt
from typing import List
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import config

news = Blueprint('news_bp', __name__)

# HTML 태그 제거를 위한 HTMLParser 클래스 정의
class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ""

    def handle_data(self, data):
        self.text += data

# 토크나이저 불러오기, 설정
class OktTokenizer: 
    okt: Okt = Okt()

    def __call__(self, text: str) -> List[str]:
        tokens: List[str] = self.okt.phrases(text)
        return tokens

# API로부터 정책 뉴스 데이터를 가져오는 함수
def fetch_policy_news(start_date, end_date):
    url = 'http://apis.data.go.kr/1371000/policyNewsService/policyNewsList'
    params = {
        'serviceKey': config.news_api_key,
        'startDate': start_date,
        'endDate': end_date
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.content
    else:
        print("Error:", response.status_code)
        return None

# Elasticsearch 서버의 URL 설정
es = Elasticsearch(["http://52.78.112.2:9200"])

def save_to_elasticsearch(news_list):
    for news in news_list:
        es.index(index="news", document=news)


@news.route('/latest-news')
def index():

    now = datetime.now()
    four_days_ago = now - timedelta(days=4)
    a_day_ago = now - timedelta(days=1)

    start_date = str(four_days_ago.strftime("%Y%m%d"))
    end_date = str(a_day_ago.strftime("%Y%m%d"))
    xml_data = fetch_policy_news(start_date, end_date)
    if xml_data:
        # XML 파싱
        root = ET.fromstring(xml_data)

        # 자연어 처리를 위한 형태소 분석기 초기화
        okt = Okt()

        # HTML 태그 제거 함수
        def remove_html_tags(html):
            parser = MyHTMLParser()
            parser.feed(html)
            return parser.text

        # news_list 초기화
        news_list = []

        # description 추출
        for item in root.findall('.//NewsItem'):
            news_title = item.find('Title').text
            news_date = item.find('ApproveDate').text
            news_description = item.find('DataContents').text
            news_url = item.find('OriginalUrl').text
            news_img = item.find('OriginalimgUrl').text

            # 문자열을 datetime 객체로 파싱
            approve_date = datetime.strptime(news_date, "%m/%d/%Y %H:%M:%S")

            # 새로운 포맷으로 datetime 객체를 문자열로 변환
            news_date = approve_date.strftime("%Y/%m/%d %H:%M")

            # HTML 태그 제거
            news_description = remove_html_tags(news_description)

            # KoNLPy를 사용하여 형태소 분석
            morphemes = okt.morphs(news_description)

            matched_keys = []

            # 각 생애 주기와 목표에 대해 조합을 생성하고 검증
            for life_key, life_values in life_cycle.items():
                for goal_key, goal_values in goals.items():
                    if goal_key == "기타목돈":
                        if any(life_word in morphemes for life_word in life_values):
                            matched_keys.append(f"{life_key} - {goal_key}")
                    else:
                        if any(life_word in morphemes for life_word in life_values) and any(goal_word in morphemes for goal_word in goal_values):
                            matched_keys.append(f"{life_key} - {goal_key}")

            if matched_keys:
                # 중복 기사가 있는지 확인하고 기사 추가
                if not any(news['news_title'] == news_title for news in news_list):
                    news_list.append({
                        'news_title': news_title,
                        'news_date': news_date,
                        'news_description': news_description,
                        'news_url': news_url,
                        'news_keywords': matched_keys,  # 모든 매칭된 키워드 조합
                        'news_img': news_img
                    })

        # XML 파싱 후 사용한 메모리를 해제
        del root

        # Elasticsearch에 저장
        save_to_elasticsearch(news_list)

        # HTML 템플릿 렌더링
        return jsonify([news for news in news_list])
        # return render_template('index.html', news_list=news_list)
    else:
        return "Failed to fetch data from API"

life_cycle = {
    "UNI": ["대학생", "재학생", "수강생", "청년", "젊은이", "20대", "캠퍼스", "대학교생", "대학원생", "스터디", "졸업생", "취업준비생", "청춘", "MZ세대", "MZ"],
    "NEW_JOB": ["사회초년생", "신입사원", "직장인", "사회적응기", "20대 후반", "청년", "취업", "직장인","MZ세대", "MZ", "경력단절", "창업", "프리랜서", "워라밸", "스타트업", "청춘"],
    "NEW_WED": ["신혼", "신랑 신부", "신혼부부", "결혼", "신혼여행", "신혼집", "부부", "연인", "웨딩", "결혼식", "신혼생활","임신", "배우자", "커플", "가정"],
    "NO_CHILD": ["부부", "남편 아내", "배우자", "연인", "동반자", "부부생활", "가정", "결혼", "커플", "딩크", "임신", "노후준비", "가족", "신생아"],
    "HAVE_CHILD": ["자녀", "아이", "딸", "아들", "어린이", "가족", "육아", "양육", "교육", "자녀교육", "청소년", "학생", "교육비","어린이집", "학교", "돌봄","초등학교", "중학교", "고등학교", "대학교","초등학생","중학생","고등학생","대학생"],
    "RETIR": ["은퇴", "노후", "노년", "퇴직", "정년퇴직", "은퇴생활", "노후준비", "후손", "노인", "건강", "연금"]
}

goals = {
    "학자금": ["교육비","학비","학습비","수업료","과외비","교재비","학자금","유학비","유학","장학금","학자금대출","등록금","응시료"],
    "여행": ["여행","휴가","관광","여행","유람","휴양","국내여행","해외여행"],
    "내집마련": ["집","주택","빌라","아파트","연립주택","다세대주택","주택단지","공동주택","전세","월세","주거","자가","자가마련","주택마련","내집마련","내집","부동산","주택담보대출","자가마련대출","주택청약","주택정책"],
    "어학연수": ["유학","교환학생","해외대학","어학연수","워홀","워킹홀리데이"],
    "전자기기": ["전자기기","가전제품","디지털기기","IT기기","스마트기기","휴대폰","컴퓨터","노트북","태블릿","스마트워치"],
    "투자비용": ["목돈","저축","투자상품", "적금", "예금"],
    "자동차": ["자차","자동차","차량","자동차","승용차","SUV","트럭","자동차보험","자동차세","리스"],
    "결혼": ["결혼자금","결혼비용","결혼경비","결혼예산","결혼준비","결혼식","웨딩","스드메"],
    "취미": ["취미","여가","여가활동","흥미","관심사","오락","게임","스포츠","여행","독서","음악감상","영화감상","공예","요리"],
    "반려동물": ["반려동물","애완동물","동물","고양이","강아지","토끼","앵무새","물고기","반려동물용품","동물병원","펫보험","펫","펫샵","동물보호소","동물보호단체","반려동물산업"],
    "자녀": ["자녀","아이","딸","아들","어린이","청소년","학생","유아","영유아","자녀교육","양육","자녀계획","교육비","어린이집","학교", "돌봄","초등학교"],
    "노후대비": ["은퇴","퇴직","노후","노년","노후준비","공직퇴직","민간퇴직","연금","퇴직금"],
    "건강": ["건강", "무병장수", "건강검진", "식습관", "질병", "운동", "건강보험", "손해보험", "화재보험", "건강보험료", "의료보험", "치료", "병원"],
    "자기계발": ["운동", "스터디", "독서", "자기계발", "자아실현", "멘토링", "평생교육원", "노인대학", "특강", "네트워킹", "컨퍼런스"],
    "창업비용": ["창업", "멘토링", "스타트업", '자영업', "사업자", "사업자등록", "자영업자"],
    "기타목돈": []
} 