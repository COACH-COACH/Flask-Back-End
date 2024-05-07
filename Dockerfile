# Nginx와 uWSGI를 설정하는 기본 이미지
FROM tiangolo/uwsgi-nginx:python3.10

LABEL maintainer="woorifis.lab37@gmail.com"

# konlpy를 위한 java 설치
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    rm -rf /var/lib/apt/lists/*

# java 환경변수 설정
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk
ENV PATH $JAVA_HOME/bin:$PATH

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y libhdf5-dev

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 설정 파일 복사
# COPY nginx.conf /etc/nginx/conf.d/nginx.conf
COPY upload.conf /etc/nginx/conf.d/upload.conf

# Add demo app
# 현재 경로에 있는 모든 파일을 /app에 복사
COPY . /app
WORKDIR /app

# Make /app/* available to be imported by Python globally to better support several use cases like Alembic migrations.
ENV PYTHONPATH=/app

# Run the start script provided by the parent image tiangolo/uwsgi-nginx.
# It will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Supervisor, which in turn will start Nginx and uWSGI
CMD ["/start.sh"]


# airflow 이용을 위한 jvm 설치
FROM apache/airflow:2.9.0
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         openjdk-17-jre-headless \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
RUN pip install --no-cache-dir apache-airflow-providers-apache-spark==2.1.3