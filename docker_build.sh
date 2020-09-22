version=$1

docker build -t gojuukaze/liteauth:"$version" .
docker push gojuukaze/liteauth:"$version"
