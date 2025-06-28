# Dockerfile
FROM python:3.11-bookworm

# マルチアーキテクチャ対応のためのARG
ARG TARGETPLATFORM

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
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# rustypipe-botguardのインストール（マルチアーキテクチャ対応）
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        ARCH="aarch64-unknown-linux-gnu"; \
    else \
        ARCH="x86_64-unknown-linux-gnu"; \
    fi && \
    curl -L -o rustypipe-botguard.tar.xz https://codeberg.org/ThetaDev/rustypipe-botguard/releases/download/v0.1.1/rustypipe-botguard-v0.1.1-${ARCH}.tar.xz \
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
