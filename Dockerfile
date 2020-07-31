FROM tangchen2018/python:3.6-alpine
ENV PYTHONUNBUFFERED 1

COPY . /project/sso

WORKDIR /project/sso

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

RUN apk add --no-cache tzdata build-base libffi-dev openssl-dev python-dev py-pip && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

RUN pip install -i https://pypi.douban.com/simple --upgrade pip \
    && pip install -r requirements.txt -i https://pypi.douban.com/simple \
    && mkdir -p /project/sso/logs \
    && mkdir -p /project/sso/media \
    && mkdir -p /project/sso/static \
    && mkdir -p /var/logs/uwsgi/ \
    && mkdir -p /var/logs/sso \
    && echo "" > /var/logs/uwsgi/run.log \
    && echo "" > /var/logs/sso/cron.log

CMD uwsgi /project/sso/education/wsgi/uwsgi.ini
