version=`cat version.py|awk -F \' '{print $2}'`

docker build -t gojuukaze/liteauth:"$version" .
docker push gojuukaze/liteauth:"$version"
