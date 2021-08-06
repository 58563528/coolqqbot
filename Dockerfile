FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV TZ Asia/Shanghai

COPY ./pyproject.toml ./poetry.lock /app/
RUN python3 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
RUN set -ex; \
    python3 -m pip install poetry; \
    poetry config virtualenvs.create false; \
    poetry install --no-root --no-dev; \
    pip install nonebot2==2.0.0a14;

COPY bot.py /app/
COPY src /app/src/
