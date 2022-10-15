# ENSURE YOU RUN THIS IN THE 'cosmos-spaces-automation'
systemctl start docker
mkdir -p "final"
docker run --name spaces \
    --restart always \
    -v $(pwd)/default.conf:/etc/nginx/conf.d/default.conf \
    -v $(pwd)/final/:/root/ \
    -p 80:80 \
    -d nginx