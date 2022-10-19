# ENSURE YOU RUN THIS IN THE 'cosmos-spaces-automation'

# Used for the https://twitter.com/IBC_Archive website: https://cosmosibc.space/

systemctl start docker
mkdir -p "final"
docker run --name spaces \
    --restart always \
    -v $(pwd)/default.conf:/etc/nginx/conf.d/default.conf \
    -v $(pwd)/final/:/root/ \
    -p 80:80 \
    -d nginx