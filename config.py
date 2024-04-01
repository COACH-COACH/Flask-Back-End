import os
from dotenv import load_dotenv

# .env 불러오기
load_dotenv()

myDBid = os.environ.get('MYSQL_USER')
myDBpw = os.environ.get('MYSQL_PASSWORD')
mySecretKey = os.environ.get('SECRET_KEY')
myDBname= os.environ.get('MYSQL_DB')
MYSQL_HOST= os.environ.get('MYSQL_HOST')
# AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
# AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
# BUCKET_NAME = os.environ.get('BUCKET_NAME')
# AWS_STORAGE_OVERRIDE = os.environ.get('AWS_STORAGE_OVERRIDE')
# AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')

# db를 저장할 폴더/파일이름 
BASE_DIR = os.path.dirname(__file__)
ssl = 'ssl_verify_identity=True'
# SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'test.db'))
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{myDBid}:{myDBpw}@{MYSQL_HOST}/{myDBname}?{ssl}".format(os.path.join(BASE_DIR,'app.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY= mySecretKey

# 또한 디버그모드를 False로 주고 ALLOWED_HOSTS를 '*'로 변경해줍니다.
DEBUG = False
ALLOWED_HOSTS = ['*'] # 모든 ip에서 접근 가능하도록 설정