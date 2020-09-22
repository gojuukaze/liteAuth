#!/bin/bash

function signal_exit()
{
echo "手动终止"
exit 0
}
trap "signal_exit" TERM INT HUP


mkdir -p /app/liteauth/docker_data/log

if ! service cron start;
then
  echo "启动cron失败"
  exit 1
fi

# 初始化
if ! python lite_auth.py init -d; then
  echo "初始化失败"
  exit 1
fi



if ! python lite_auth.py start; then
  echo "启动失败"
  exit 1
fi

while sleep 2; do
  if ! python lite_auth.py status >/dev/null; then
    echo "服务意外终止"
    exit 1
  fi

done
