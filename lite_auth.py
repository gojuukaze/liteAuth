#!/usr/bin/env python3

import os
import subprocess
import sys
import time

import click

from utils.file import gen_file_from_template

local_py = sys.executable


def echo(s, nl=True):
    click.secho(s, nl=nl)


def line(s='-' * 10):
    click.secho(s)


def error(s, nl=True):
    click.secho('[错误]：' + s, fg='red', nl=nl)
    sys.exit()


def info(s, nl=True):
    click.secho(s, fg='green', nl=nl)


def warning(s, nl=True):
    click.secho(s, fg='yellow', nl=nl)


@click.group(help='Lite Auth')
def cli():
    pass


@cli.command(help='初始化')
@click.option('-s', '--secret_key', help='secret_key，为空将自动生成。若环境变量中有LITE_AUTH_SECRET_KEY，则取环境变量中的值')
def init(secret_key):
    echo('初始化')
    line()
    create_config(secret_key)
    line()

    collect_static()
    line()

    make_migrations()
    line()
    info('初始化完成')


def create_config(secret_key):
    info('创建配置文件')
    config_path = 'config/config.py'
    if os.path.exists(config_path):
        warning('[跳过]已存在config文件')
        return
    secret_key = os.getenv('LITE_AUTH_SECRET_KEY') or secret_key
    if not secret_key:
        from django.core.management.utils import get_random_secret_key
        secret_key = get_random_secret_key()
    gen_file_from_template('tpl/config.py.tpl', config_path, secret_key=secret_key)

    info('[完成]')


def collect_static():
    info('收集静态文件')
    r = subprocess.run([local_py, 'manage.py', 'collectstatic', '--noinput'])

    if r.returncode == 0:
        info('[完成]')
    else:
        error('收集静态文件失败')


def make_migrations():
    info('迁移数据库')
    r1 = subprocess.run([local_py, 'manage.py', 'migrate'])

    r2 = subprocess.run([local_py, 'manage.py', 'createcachetable'])

    if r1.returncode == 0 and r2.returncode == 0:
        info('[完成]')
    else:
        error('迁移数据库失败')


@cli.command(help='生成随机secret_key')
def gen_secret_key():
    from django.core.management.utils import get_random_secret_key
    echo("SECRET_KEY = '%s'" % get_random_secret_key())


@cli.command(help='启动服务')
@click.argument('server', type=click.Choice(['all', 'ldap', 'http'], case_sensitive=False), default='all')
@click.option('-n', '--nodaemon', is_flag=True, default=False, help='以非守护模式启动，带有此参数时需要单独启动http与ldap')
def start(server, nodaemon):
    if nodaemon and server == 'all':
        error('非守护模式下需要单独启动http与ldap')
    if server == 'all':
        server = ['ldap', 'http']
    if 'ldap' in server:
        start_ldap(nodaemon)
        line()
    if 'http' in server:
        start_http(nodaemon)
        line()


def start_ldap(nodaemon):
    twistd = os.path.join(os.path.dirname(local_py), 'twistd')
    info('启动LDAP Server')
    cmd = [twistd,
           '-n' if nodaemon else '',
           '-y', 'twisted_config.py',
           ]
    r = subprocess.run(' '.join(cmd), shell=True)
    if r.returncode == 0:
        info('[完成]')
    else:
        error('启动失败')


def start_http(nodaemon):
    gunicorn = os.path.join(os.path.dirname(local_py), 'gunicorn')
    info('启动HTTP Server')
    cmd = [gunicorn,
           'lite_auth_http.lite_auth_http.wsgi',
           '' if nodaemon else '-D',
           '-c', 'python:gunicorn_config',
           ]
    r = subprocess.run(' '.join(cmd), shell=True)

    if r.returncode == 0:
        info('[完成]')
    else:
        error('启动失败')


@cli.command(help='服务状态')
def status():
    for s, f in [['LDAP Server', 'twistd.pid'], ['HTTP Server', 'gunicorn.pid']]:
        is_running = check_status(f)
        info(s, False)
        info('  [运行]' if is_running else '  [关闭]')
        line()


def get_pid(pid_file):
    with open(pid_file, 'r')as f:
        return int(f.read().strip())


def check_status(pid_file):
    if not os.path.exists(pid_file):
        return False
    pid = get_pid(pid_file)
    try:
        os.kill(pid, 0)
        return True
    except:
        return False


@cli.command(help='服务状态')
@click.argument('server', type=click.Choice(['all', 'ldap', 'http'], case_sensitive=False), default='all')
def stop(server):
    server = [server]
    if 'all' in server:
        server = ['ldap', 'http']
    pid_f = {
        'ldap': 'twistd.pid',
        'http': 'gunicorn.pid'
    }
    pid = {}

    wait_server = []
    for s in server:
        info('关闭%s Server' % s.upper(), False)

        if not check_status(pid_f[s]):
            echo('  服务未启动，跳过')
        else:
            pid[s] = get_pid(pid_f[s])
            os.kill(pid[s], 15)
            wait_server.append(s)
            info('')

        line()
    for s in wait_server:
        info('等待%s Server结束' % s.upper(), False)
        r = wait_stop(pid[s])
        if r:
            info('  [完成]')
        else:
            warning('意外终止，请手动检查服务状态')


def wait_stop(pid):
    while True:
        try:
            os.kill(pid, 0)
            time.sleep(0.1)
        except KeyboardInterrupt:
            return False
        except:
            return True


if __name__ == '__main__':
    cli()
