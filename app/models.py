from app import db

#USER_TB
class User(db.Model):
    __tablename__ = 'USER_TB'

    ID_PK = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 고객 ID
    LOGIN_ID = db.Column(db.String(30))              # 로그인 아이디
    LOGIN_PW = db.Column(db.String(50))              # 로그인 비번
    FULL_NAME = db.Column(db.String(50))             # 이름
    SEX = db.Column(db.CHAR(1))                      # 성별
    BIRTH_DATE = db.Column(db.Date)                  # 생년월일
    REGION = db.Column(db.String(100))               # 지역
    REGIST_DATE = db.Column(db.Date)                 # 가입일
    LIFE_STAGE = db.Column(db.String(50))            # 라이프스테이지

    def serialize(self):
        return {
            'ID_PK': self.ID_PK,
            'LOGIN_ID': self.LOGIN_ID,
            'LOGIN_PW': self.LOGIN_PW,
            'FULL_NAME': self.FULL_NAME,
            'SEX': self.SEX,
            'BIRTH_DATE': self.BIRTH_DATE.strftime('%Y-%m-%d') if self.BIRTH_DATE else None,
            'REGION': self.REGION,
            'REGIST_DATE': self.REGIST_DATE.strftime('%Y-%m-%d') if self.REGIST_DATE else None,
            'LIFE_STAGE': self.LIFE_STAGE
        }
    

# GOAL_TB    
class Goal(db.Model):
    __tablename__ = 'GOAL_TB'

    ID_PK = db.Column(db.Integer, primary_key=True, autoincrement=True)    # 목표 ID
    CUSTOMER_ID_FK = db.Column(db.Integer, db.ForeignKey('CUSTOMER_TB.ID_PK'))  # 고객 ID
    GOAL_NAME = db.Column(db.String(300))                                  # 목표 분류
    TARGET_COST = db.Column(db.DECIMAL(10, 2))                             # 목표 금액
    ACCUMULATED_BALANCE = db.Column(db.DECIMAL(17, 2))                     # 누적 금액
    GOAL_ST = db.Column(db.CHAR(1))                                        # 상태(진행 / 완료)
    GOAL_PERIOD = db.Column(db.String(50))                                 # 목표 기간
    START_DATE = db.Column(db.Date)                                        # 시작일
    END_DATE = db.Column(db.Date)                                          # 마감일

    def serialize(self):
        return {
            'ID_PK': self.ID_PK,
            'CUSTOMER_ID_FK': self.CUSTOMER_ID_FK,
            'GOAL_NAME': self.GOAL_NAME,
            'TARGET_COST': float(self.TARGET_COST) if self.TARGET_COST is not None else None,
            'ACCUMULATED_BALANCE': float(self.ACCUMULATED_BALANCE) if self.ACCUMULATED_BALANCE is not None else None,
            'GOAL_ST': self.GOAL_ST,
            'GOAL_PERIOD': self.GOAL_PERIOD,
            'START_DATE': self.START_DATE.strftime('%Y-%m-%d') if self.START_DATE else None,
            'END_DATE': self.END_DATE.strftime('%Y-%m-%d') if self.END_DATE else None
        }


# PRODUCT_TB
class Product(db.Model):
    __tablename__ = 'PRODUCT_TB'

    ID_PK = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 상품 ID
    PRODUCT_NAME = db.Column(db.String(300))                             # 상품명
    PRODUCT_TYPE = db.Column(db.String(50))                              # 상품 종류
    ELIGIBILITY = db.Column(db.String(500))                              # 가입 대상
    MIN_TERM = db.Column(db.Integer)                                     # 최소 가입 기간
    MAX_TERM = db.Column(db.Integer)                                     # 최대 가입 기간
    MIN_AMT = db.Column(db.DECIMAL(17, 2))                               # 최소 가입 금액
    MAX_AMT = db.Column(db.DECIMAL(17, 2))                               # 최대 가입 금액
    DEPOSIT_CYCLE = db.Column(db.String(50))                             # 입금 주기
    INTEREST_RATE = db.Column(db.DECIMAL(5, 2))                          # 금리
    
    def serialize(self):
        return {
            'ID_PK': self.ID_PK,
            'PRODUCT_NAME': self.PRODUCT_NAME,
            'PRODUCT_TYPE': self.PRODUCT_TYPE,
            'ELIGIBILITY': self.ELIGIBILITY,
            'MIN_TERM': self.MIN_TERM,
            'MAX_TERM': self.MAX_TERM,
            'MIN_AMT': float(self.MIN_AMT) if self.MIN_AMT is not None else None,
            'MAX_AMT': float(self.MAX_AMT) if self.MAX_AMT is not None else None,
            'DEPOSIT_CYCLE': self.DEPOSIT_CYCLE,
            'INTEREST_RATE': float(self.INTEREST_RATE) if self.INTEREST_RATE is not None else None
        }

#ENROLLMENT_TB
class Enrollment(db.Model):
    __tablename__ = 'ENROLL_TB'

    ID_PK = db.Column(db.Integer, primary_key=True, autoincrement=True)         # 상품 가입 ID
    CUSTOMER_ID_FK = db.Column(db.Integer, db.ForeignKey('CUSTOMER_TB.ID_PK'))  # 고객 ID
    PRODUCT_ID_FK = db.Column(db.Integer, db.ForeignKey('PRODUCT_TB.ID_PK'))    # 상품 ID
    GOAL_ID_FK = db.Column(db.Integer, db.ForeignKey('GOAL_TB.ID_PK'))          # 목표 ID
    START_DATE = db.Column(db.Date)                                             # 가입일
    END_DATE = db.Column(db.Date)                                               # 민기일
    REGULAR_DEPOSIT = db.Column(db.DECIMAL(17, 2))                              # 정기 입금액
    ACCUMULATED_BALANCE = db.Column(db.DECIMAL(17, 2))                          # 누적 입금액
    MATURITY_ST = db.Column(db.CHAR(1))                                         # 만기 여부

    def serialize(self):
        return {
            'ID_PK': self.ID_PK,
            'CUSTOMER_ID_FK': self.CUSTOMER_ID_FK,
            'PRODUCT_ID_FK': self.PRODUCT_ID_FK,
            'GOAL_ID_FK': self.GOAL_ID_FK,
            'START_DATE': self.START_DATE.strftime('%Y-%m-%d') if self.START_DATE else None,
            'END_DATE': self.END_DATE.strftime('%Y-%m-%d') if self.END_DATE else None,
            'REGULAR_DEPOSIT': float(self.REGULAR_DEPOSIT) if self.REGULAR_DEPOSIT is not None else None,
            'ACCUMULATED_BALANCE': float(self.ACCUMULATED_BALANCE) if self.ACCUMULATED_BALANCE is not None else None,
            'MATURITY_ST': self.MATURITY_ST
        }


#PAYMENT_TB
class Payment(db.Model):
    __tablename__ = 'PAYMENT_TB'

    ID_PK = db.Column(db.Integer, primary_key=True, autoincrement=True)         # 소비 ID
    CUSTOMER_ID_FK = db.Column(db.Integer, db.ForeignKey('CUSTOMER_TB.ID_PK'))  # 고객 ID
    CONSUMPTION = db.Column(db.DECIMAL(17, 2))                                  # 소비 금액
    PAYMENT_TYPE = db.Column(db.String(30))                                     # 결제 타입
    PAYMENT_QUARTER = db.Column(db.String(10))                                  # 분기
    CATEGORY = db.Column(db.String(100))                                        # 카테고리명

    def serialize(self):
        return {
            'ID_PK': self.ID_PK,
            'CUSTOMER_ID_FK': self.CUSTOMER_ID_FK,
            'CONSUMPTION': float(self.CONSUMPTION) if self.CONSUMPTION is not None else None,
            'PAYMENT_TYPE': self.PAYMENT_TYPE,
            'PAYMENT_QUARTER': self.PAYMENT_QUARTER,
            'CATEGORY': self.CATEGORY
        }