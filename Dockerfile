FROM richardchien/cqhttp:latest
ENV CQHTTP_POST_URL=http://127.0.0.1:8080/ \
    CQHTTP_SERVE_DATA_FILES=yes
#设置清华源
# RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
# COPY sources.list /etc/apt/sources.list
#安装python3.6和pip
RUN add-apt-repository ppa:jonathonf/python-3.6 \
    && apt-get update \
    && apt-get install -y python3.6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists \
    && curl https://bootstrap.pypa.io/get-pip.py | python3.6
#安装依赖
COPY requirements.txt /home/user/coolqbot/requirements.txt
# RUN pip3.6 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /home/user/coolqbot/requirements.txt
RUN pip3.6 install -r /home/user/coolqbot/requirements.txt
#复制CoolQBot并运行
COPY src /home/user/coolqbot
RUN chown user:user /home/user/coolqbot/run.py
RUN echo "\n\nsudo -E -Hu user /usr/bin/python3.6 /home/user/coolqbot/run.py &" >> /etc/cont-init.d/110-get-coolq