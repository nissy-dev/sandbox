FROM python:3.9.7-buster

RUN apt-get update && apt install -y locales && localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9

# 日本語 font のインストール
RUN apt-get install -y fonts-noto-cjk

# python ライブラリのインストール
RUN python -m pip install pandas numpy plotly matplotlib jupyterlab japanize-matplotlib gql[all]
