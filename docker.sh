# ENSURE YOU RUN THIS IN THE 'cosmos-spaces-automation'

# Used for the https://twitter.com/IBC_Archive website: https://cosmosibc.space/

systemctl start docker
mkdir -p "final"

CONTAINERS=$(docker ps -q)
docker kill $CONTAINERS
docker rm $CONTAINERS



# run the website on port 5000
docker run --rm --name=interchain-archive -p 5000:80 -d reecepbcups/interchain-archive

# run the nginx server
docker run --name spaces \
    --restart always \
    -v $(pwd)/default.conf:/etc/nginx/conf.d/default.conf \
    -v $(pwd)/final/:/root/ \
    -p 80:80 \
    -d nginx
