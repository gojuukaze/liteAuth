FROM gojuukaze/liteauth_base:1.0.0


ADD requirements.txt .
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

WORKDIR /app/liteauth
ADD . .
RUN mkdir docker_data
RUN touch docker_data/config.py

EXPOSE 8300 
EXPOSE 8389

VOLUME /app/liteauth/docker_data
VOLUME /app/liteauth/custom

CMD ["/bin/bash","entrypoint.sh"]
