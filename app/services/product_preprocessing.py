from app.models import Product
from sqlalchemy.sql import func
import pandas as pd
import numpy as np

def product_preprocessing(products: pd.DataFrame):
    # 1) product_name 텍스트 처리
    products["PRODUCT_NAME"] = products["PRODUCT_NAME"].str.replace("\n", "")
    # 2) product_name 은행명 제거
    return products