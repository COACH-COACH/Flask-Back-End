from enum import Enum
from app import db

class LifeStage(Enum):
    UNI = 'UNI'
    NEW_JOB = 'NEW_JOB'
    NEW_WED = 'NEW_WED'
    HAVE_CHILD = 'HAVE_CHILD'
    NO_CHILD = 'NO_CHILD'
    RETIR = 'RETIR'

class Sex(Enum):
    M = 'M'
    F = 'F'

class ProductType(Enum):
    DEPOSIT = 'DEPOSIT'
    SAVINGS = 'SAVINGS'

class DepositCycle(Enum):
    FLEXIBLE = 'FLEXIBLE'
    FIXED = 'FIXED'
    HOLD = 'HOLD'


class User(db.Model):
    __tablename__ = 'USER_TB'

    ID_PK = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 고객 ID
    BIRTH_DATE = db.Column(db.Date)  # 생년월일
    REGIST_DATE = db.Column(db.Date)  # 가입일
    FULL_NAME = db.Column(db.String(255))  # 이름
    LOGIN_ID = db.Column(db.String(255))  # 로그인 아이디
    LOGIN_PW = db.Column(db.String(255))  # 로그인 비밀번호
    REGION = db.Column(db.String(255))  # 지역
    SEQ = db.Column(db.String(255))  # SEQ
    LIFE_STAGE = db.Column(db.Enum(LifeStage))  # 라이프 스테이지
    SEX = db.Column(db.Enum(Sex))  # 성별

    def serialize(self):
        return {
            'ID_PK': self.ID_PK,
            'BIRTH_DATE': self.BIRTH_DATE.strftime('%Y-%m-%d') if self.BIRTH_DATE else None,
            'REGIST_DATE': self.REGIST_DATE.strftime('%Y-%m-%d') if self.REGIST_DATE else None,
            'FULL_NAME': self.FULL_NAME,
            'LOGIN_ID': self.LOGIN_ID,
            'LOGIN_PW': self.LOGIN_PW,
            'REGION': self.REGION,
            'SEQ': self.SEQ,
            'LIFE_STAGE': self.LIFE_STAGE.value if self.LIFE_STAGE else None,
            'SEX': self.SEX.value if self.SEX else None
        }

class Goal(db.Model):
    __tablename__ = 'GOAL_TB'

    ID_PK = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 목표 ID
    USER_ID_FK = db.Column(db.Integer, db.ForeignKey('USER_TB.ID_PK'), nullable=False)  # 고객 ID
    GOAL_NAME = db.Column(db.String(100), nullable=False)  # 목표 분류(학자금, 여행, 어학연수, 전자기기 ...)
    TARGET_COST = db.Column(db.DECIMAL(19, 0), nullable=False)  # 목표 금액(최대 1경)
    ACCUMULATED_BALANCE = db.Column(db.DECIMAL(19, 0), nullable=False, default=0)  # 누적 금액(최대 1경)
    GOAL_ST = db.Column(db.Boolean, nullable=False, default=False)  # 목표 달성 상태(0:진행 / 1:완료)
    GOAL_PERIOD = db.Column(db.Integer, nullable=False)  # 목표 기간(개월 단위)
    START_DATE = db.Column(db.Date, nullable=False)  # 시작일
    END_DATE = db.Column(db.Date)  # 마감일

    def serialize(self):
        return {
            'ID_PK': self.ID_PK,
            'USER_ID_FK': self.USER_ID_FK,
            'GOAL_NAME': self.GOAL_NAME,
            'TARGET_COST': int(self.TARGET_COST) if self.TARGET_COST is not None else None,
            'ACCUMULATED_BALANCE': int(self.ACCUMULATED_BALANCE) if self.ACCUMULATED_BALANCE is not None else None,
            'GOAL_ST': self.GOAL_ST,
            'GOAL_PERIOD': self.GOAL_PERIOD,
            'START_DATE': self.START_DATE.strftime('%Y-%m-%d') if self.START_DATE else None,
            'END_DATE': self.END_DATE.strftime('%Y-%m-%d') if self.END_DATE else None
        }

class Product(db.Model):
    __tablename__ = 'PRODUCT_TB'

    ID_PK = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 상품 ID
    PRODUCT_NAME = db.Column(db.String(300))                             # 상품명
    PRODUCT_TYPE = db.Column(db.Enum(ProductType))                       # 상품 종류
    ELIGIBILITY = db.Column(db.String(500))                              # 가입 대상
    MAX_INTEREST_RATE = db.Column(db.DECIMAL(17, 2))                    # 최대 가입 금액
    DEPOSIT_CYCLE = db.Column(db.Enum(DepositCycle))                    # 입금 주기
    INTEREST_RATE = db.Column(db.DECIMAL(5, 2))                          # 금리
    MATURITY = db.Column(db.Integer)
    CREATE_DATE = db.Column(db.Date)
    CAUTION = db.Column(db.String(500)) 
    LIMIT_AMT = db.Column(db.String(500)) 
    MEMBERSHIP_CONDITION = db.Column(db.String(500)) 
    PREFER_CONDITION = db.Column(db.String(500)) 
    PRODUCT_DETAIL = db.Column(db.String(200))

    def serialize(self):
        return {
            'ID_PK': self.ID_PK,
            'PRODUCT_NAME': self.PRODUCT_NAME,
            'PRODUCT_TYPE': self.PRODUCT_TYPE.value if self.PRODUCT_TYPE else None,
            'ELIGIBILITY': self.ELIGIBILITY,
            'MAX_INTEREST_RATE': str(self.MAX_INTEREST_RATE),
            'DEPOSIT_CYCLE': self.DEPOSIT_CYCLE.value if self.DEPOSIT_CYCLE else None,
            'INTEREST_RATE': str(self.INTEREST_RATE),
            'MATURITY': self.MATURITY,
            'CREATE_DATE': self.CREATE_DATE,
            'CAUTION': self.CAUTION,
            'LIMIT_AMT': self.LIMIT_AMT,
            'MEMBERSHIP_CONDITION': self.MEMBERSHIP_CONDITION,
            'PREFER_CONDITION': self.PREFER_CONDITION,
            'PRODUCT_DETAIL': self.PRODUCT_DETAIL
        }

class Payment(db.Model):
    __tablename__ = 'PAYMENT_TB'

    ID_PK = db.Column(db.Integer, primary_key=True, autoincrement=True)         # 소비 ID
    CUSTOMER_ID_FK = db.Column(db.Integer, db.ForeignKey('CUSTOMER_TB.ID_PK'))  # 고객 ID
    CONSUMPTION = db.Column(db.DECIMAL(17, 2))                                  # 소비 금액
    PAYMENT_TYPE = db.Column(db.String(500))                                    # 결제 타입
    PAYMENT_QUARTER = db.Column(db.String(10))                                  # 분기
    CATEGORY = db.Column(db.String(100))                                        # 카테고리명

    def serialize(self):
        return {
            'ID_PK': self.ID_PK,
            'CUSTOMER_ID_FK': self.CUSTOMER_ID_FK,
            'CONSUMPTION': float(self.CONSUMPTION) if self.CONSUMPTION is not None else None,
            'PAYMENT_TYPE': self.PAYMENT_TYPE.value if self.PAYMENT_TYPE else None,
            'PAYMENT_QUARTER': self.PAYMENT_QUARTER,
            'CATEGORY': self.CATEGORY
        }