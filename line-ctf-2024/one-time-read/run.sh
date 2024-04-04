#!/bin/bash
echo "Creating .env file"
cp .env.template .env
echo "FLAG=LINECTF{test-flag}" >> .env # set flag here
echo "REDIS_PASSWORD=`openssl rand -hex 16`" >> .env
export $(egrep -v '^#' .env | xargs)

# sudo systemctl restart docker

echo "Shutting down running containers"
sudo docker compose down --remove-orphans
docker network rm one_time_read_network

echo "Starting containers"
docker network create one_time_read_network
sudo docker compose up --build -d

echo "Checking health status of containers"
while :
do
    health_web=$(docker inspect -f {{.State.Health.Status}} one_time_read_web)
    health_bot=$(docker inspect -f {{.State.Health.Status}} one_time_read_bot)
    if [[ "$health_web" == "healthy" ]] && [[ "$health_bot" == "healthy" ]]; then
        break
    fi
done

web_ip=$(docker inspect --format '{{ .NetworkSettings.Networks.one_time_read_network.IPAddress }}' one_time_read_web)
echo "Web IP = ${web_ip}"

bot_ip=$(docker inspect --format '{{ .NetworkSettings.Networks.one_time_read_network.IPAddress }}' one_time_read_bot)
echo "Web IP = ${bot_ip}"

echo "Writing web domain to /etc/hosts of puppeteer"
docker exec one_time_read_puppeteer /bin/bash -c "echo '${web_ip} ${BUSINESS_NAME}${DOMAIN_SUFFIX}' >> /etc/hosts"

echo "Writing bot domain to /etc/hosts of puppeteer"
docker exec one_time_read_puppeteer /bin/bash -c "echo '${bot_ip} ${BOT_NAME}${DOMAIN_SUFFIX}' >> /etc/hosts"