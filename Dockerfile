# Dockerfile
FROM python:3.11.3-bullseye
# システムの依存関係をインストール（MySQLクライアント関連を追加）
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    libpq-dev \
    graphviz \
    poppler-utils \
    ffmpeg \
    libgdiplus \
    curl \
    fonts-ipafont \
    fonts-ipaexfont \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# rustypipe-botguardのインストール
RUN curl -L -o rustypipe-botguard.tar.xz https://codeberg.org/ThetaDev/rustypipe-botguard/releases/download/v0.1.1/rustypipe-botguard-v0.1.1-x86_64-unknown-linux-gnu.tar.xz \
    && tar -xf rustypipe-botguard.tar.xz \
    && chmod +x rustypipe-botguard \
    && mv rustypipe-botguard /usr/local/bin/ \
    && rm rustypipe-botguard.tar.xz

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係のインストール
COPY requirements.lock .
RUN sed '/^-e file:/d' requirements.lock > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポートの公開
EXPOSE 8501

# ENTRYPOINTの設定
ENTRYPOINT ["python", "-m","streamlit", "run", "src/streamlit/main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=False", "--server.maxUploadSize=4000", "--server.headless=True", "--server.enableXsrfProtection=False"]
