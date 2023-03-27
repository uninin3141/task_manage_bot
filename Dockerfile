# ベースイメージの選択
FROM python:3.9-slim

# インストールするシステムパッケージの追加
RUN apt-get update && apt-get install -y fonts-ipaexfont-gothic

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係をインストール
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY app/ .

# 実行コマンドの設定
CMD ["python", "discord.py"]
