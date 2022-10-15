# ENSURE YOU RUN THIS IN THE 'cosmos-spaces-automation'
mkdir -p "final"
docker run --name spaces \
    --restart always \
    -v $(pwd)/default.conf:/etc/nginx/conf.d/default.conf \
    -v $(pwd)/final/:/root/ \
    -p 555:555 \
    -d nginx