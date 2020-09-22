# Work In Process

--------

# Lite Auth
An tiny LDAP authentication server.  
一个基于LDAP精简的身份认证服务


![dL2jDH.jpg](https://s1.ax1x.com/2020/08/31/dL2jDH.jpg)

# 安装

## 普通安装
> ### 环境要求：  
> * OS: Linux
> * Python 3.6+ (maybe 3.4, 3.5)
> * Nginx/Apache/或其他同类软件
> * git

> ### 建议在开始前创建个虚拟环境
> ```shell script
> # 如果你的python是指向python2环境，使用python3代替
> python -m venv /your_path/liteAuth_env
> source /your_path/liteAuth_env
> ```


1.从仓库拉取代码
```shell script
git clone https://github.com/gojuukaze/liteAuth.git

cd liteAuth
```

2.安装包
```shell script
python -m pip install -r requirements.txt
```

3.初始化
```shell script
./lite_auth.py init
```

> 初始化时会在`config/config.py`中生成一个随机的密钥`SECRET_KEY`，这个请保存这个密钥不要丢失。
> 迁移服务时必须使用相同的密钥。  
> * 你可以在初始化时使用 `-s` 设置秘钥。
> * 运行`./lite_auth.py init --help`可以查看帮助文档
> * 你可以使用`./lite_auth.py gen-secret-key`生成随机的密钥

4.修改配置

修改`config/config.py`，增加下列几项。（完整配置参考 [默认配置](config/lite_auth_config.py)）

```python
HTTP_LISTEN = '0.0.0.0:8300'

# 访问lite auth的站点地址，填ip或域名。
# 部署时需要使用nginx或apache监听此地址，并把请求转发到 HTTP_LISTEN
LITE_AUTH_URL = 'http://127.0.0.1:8080'

# 一定要以 / 结尾
ADMIN_URL = 'admin/'

LDAP_LISTEN = '0.0.0.0:8389'
# http服务的地址，ldap服务会请求这个地址。
# 一般写内网地址
LDAP_API_URL = 'http://127.0.0.1:8080'

# 通知backend，用户发通知给用户
# 此项不是必须的，但强烈建议你配置一个backend
# 更多参考: todo
NOTIFICATION_BACKEND={}
```

5.启动

```shell script
./lite_auth.py start
```

6.代理请求  

这里给出nginx的配置样例。如果只是为了体验可跳过此步，并在配置文件中添加`DEBUG=True`

* nginx配置:
```nginx
server {
    # 如果你修改了配置文件，改为对应的值
    listen       8080;
    server_name  localhost;
    
    # 替换为你的路径
    root /your_path/liteAuth;
    
    location / {
        try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        # we don't want nginx trying to do something clever with
        # redirects, we set the Host: header above already.
        proxy_redirect off;
        # 如果你修改了配置文件，改为对应的值
        proxy_pass http://127.0.0.1:8300;
    }
}
```

7.使用服务

访问http://127.0.0.1:8080 ，或者你的地址

## docker安装

1.拉取镜像
```shell script
docker pull gojuukaze/liteauth:0.1.0
# 或
docker pull gojuukaze/liteauth:0.1.0-nginx
```
* `*-nginx` 镜像自带nginx，你可以不用使用nginx代理

2.创建配置文件  

若在**非生产环境**并且使用nginx镜像可跳过这步
```shell script
mkdir liteauth_data
cd liteauth_data
touch config.py
```

> 配置文件的详细说明参考普通安装的第2步。  
> docker启动你不同添加`HTTP_LISTEN`与`LDAP_LISTEN`

4.启动
```shell script
docker run -d --name=liteauth \
  --restart=always \
  -p 8300:8300 -p 8389:8389 \
  -v /your_path/liteauth_data:/app/liteauth/docker_data \
  gojuukaze/liteauth
```

5.代理请求  
参考普通安装第6步
