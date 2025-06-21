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
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポートの公開
EXPOSE 8501

# ENTRYPOINTの設定
ENTRYPOINT ["python", "-m","streamlit", "run", "src/streamlit/main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=False", "--server.maxUploadSize=4000", "--server.headless=True", "--server.enableXsrfProtection=False"]
