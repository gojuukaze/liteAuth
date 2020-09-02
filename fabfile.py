from fabric import task
import os
import sys

from lite_auth_http.lite_auth_http.settings import M_APPS

os.system('ssh-add -K ~/.ssh/id_rsa')
# 只有本地命令能用
local_py = sys.executable


@task
def flush_db(c):
    """
    重置本地数据库
    fab flush-db

    """
    apps = []
    for f in M_APPS:
        p = f.split('.')[1]
        apps.append(p)
        c.run('rm -rf ' + os.path.join('lite_auth_http',p, 'migrations'))
    c.run('rm db.sqlite3', warn=True)
    c.run(local_py + ' manage.py makemigrations ' + ' '.join(apps))
    c.run(local_py + ' manage.py migrate')
    c.run(local_py + ' manage.py mock')
    c.run(local_py + ' manage.py createcachetable')

