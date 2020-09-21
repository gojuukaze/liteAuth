FROM ubuntu:20.04

WORKDIR /app/liteauth
ADD . .

EXPOSE 8300 
EXPOSE 8389

