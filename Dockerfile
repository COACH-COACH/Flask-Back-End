# Nginx와 uWSGI를 설정하는 기본 이미지
FROM tiangolo/uwsgi-nginx:python3.10

LABEL maintainer="woorifis.lab37@gmail.com"

# konlpy를 위한 java 설치
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    rm -rf /var/lib/apt/lists/*

# java 환경변수 설정
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk
ENV PATH $JAVA_HOME/bin:$PATH

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y libhdf5-dev

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV STATIC_URL /static
# Absolute path in where the static files wil be
ENV STATIC_PATH /app/test/static

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
# ENV STATIC_INDEX 1
# 우리는 template를 메인으로 사용하므로 0(false)
ENV STATIC_INDEX 0

# Add demo app
# 현재 경로에 있는 모든 파일을 /app에 복사
COPY . /app
WORKDIR /app

# Make /app/* available to be imported by Python globally to better support several use cases like Alembic migrations.
ENV PYTHONPATH=/app

# Move the base entrypoint to reuse it
RUN mv /entrypoint.sh /uwsgi-nginx-entrypoint.sh
# Copy the entrypoint that will generate Nginx additional configs
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Run the start script provided by the parent image tiangolo/uwsgi-nginx.
# It will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Supervisor, which in turn will start Nginx and uWSGI
CMD ["/start.sh"]