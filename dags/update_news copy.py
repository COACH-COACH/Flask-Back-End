from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonVirtualenvOperator
from airflow.operators.bash import BashOperator
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from konlpy.tag import Okt
from typing import List
import requests
import xml.etree.ElementTree as ET
from html.parser import HTMLParser


# DAG 설정
default_args = {
    'owner': 'airflow',
    # 'depends_on_past': False,
    'start_date': datetime(2024, 5, 3),
    # 'email': ['your_email@example.com'],
    # 'email_on_failure': False,
    # 'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id = 'policy_news_etl1',
    default_args=default_args,
    description='A simple tutorial DAG for fetching policy news',
    schedule_interval=timedelta(days=4),
) as dag:

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
            'serviceKey': "3CMBhPv/8ZOqAWpYtL2gjJDh91ZhOX9I81Ju7VUC+x4UYfAdDYjs29TnTjM34RjdFNihnhKEy/rwhbvjmCYCLw==",
            'startDate': start_date,
            'endDate': end_date
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.content
        else:
            print("Error:", response.status_code)
            return None
        
    # XML 데이터를 파싱하고 뉴스를 처리하는 함수
    def parse_xml_and_process_news(xml_data):
        root = ET.fromstring(xml_data)
        news_list = []
        for item in root.findall('.//NewsItem'):  # XPath를 사용하여 모든 뉴스 항목을 찾습니다.
            news_title = item.find('Title').text
            news_link = item.find('OriginalUrl').text
            news_pub_date = item.find('ApporoveDate').text
            news_description = item.find('DataContents').text

            # HTML 태그 제거
            parser = MyHTMLParser()
            parser.feed(news_description)
            cleaned_description = parser.get_data()

            # Okt를 사용한 텍스트 처리
            tokenizer = OktTokenizer()
            keywords = tokenizer.extract_keywords(cleaned_description)

            # 뉴스 데이터 구조화
            news = {
                'news_title': news_title,
                'news_link': news_link,
                'news_pub_date': news_pub_date,
                'news_description': cleaned_description,
                'keywords': keywords
            }
            news_list.append(news)
        
        return news_list

    # Elasticsearch 서버의 URL 설정
    es = Elasticsearch(["http://52.78.112.2:9200"])

    def save_to_elasticsearch(news_list):
        for news in news_list:
            response = es.index(index="news", document=news)
            print(response['result'])

    # 중복 뉴스를 제거하는 함수
    def remove_duplicates(news_list):
        unique_news_list = []
        seen_titles = set()
        for news in news_list:
            if news['news_title'] not in seen_titles:
                seen_titles.add(news['news_title'])
                unique_news_list.append(news)
        return unique_news_list

    # 오래된 뉴스를 삭제하는 함수
    def delete_old_news():
        es = Elasticsearch(["http://52.78.112.2:9200"])
        old_date = datetime.now() - timedelta(days=28)
        try:
            es.delete_by_query(
                index="news",
                body={
                    "query": {
                        "range": {
                            "news_date": {
                                "lt": old_date.strftime("%Y-%m-%d")
                            }
                        }
                    }
                }
            )
        except NotFoundError:
            print("No old news to delete.")

    # Airflow에서 실행할 메인 함수
    def policy_news_etl():
        now = datetime.now()
        four_days_ago = now - timedelta(days=4)
        start_date = four_days_ago.strftime("%Y%m%d")
        end_date = now.strftime("%Y%m%d")

        xml_data = fetch_policy_news(start_date, end_date)
        if xml_data:
            # XML 파싱 및 중복 제거 등의 로직
            news_list = parse_xml_and_process_news(xml_data)
            unique_news_list = remove_duplicates(news_list)
            save_to_elasticsearch(unique_news_list)

    # PythonOperator를 사용하여 Airflow 태스크 정의
    fetch_and_process_news_task = PythonVirtualenvOperator(
        task_id='fetch_and_process_news1',
        python_callable=policy_news_etl,
        requirements=["konlpy"],
        system_site_packages=False,
        dag=dag,
    )

    delete_old_news_task = PythonVirtualenvOperator(
        task_id='delete_old_news1',
        python_callable=delete_old_news,
        dag=dag,
        requirements=["konlpy"],
        system_site_packages=False,
    )
    news_task = BashOperator(
        task_id='delete_old_news12',
        bash_command='pip install -r requirements.txt'
    )
    news_task2 = BashOperator(
        task_id='delete_old_news123',
        bash_command='pip list',
        depends_on_past=True
    )
    
    news_task3 = BashOperator(
        task_id='delete_old_news4',
        bash_command='sudo apt-get update && apt-get install -y default-jdk',
        depends_on_past=True
    )
    # 작업 흐름 정의
    news_task3 >> news_task >> fetch_and_process_news_task >> delete_old_news_task

# DAG 정의 끝
