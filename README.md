```shell

1. init project

scrapy startproject rsshub

pip freeze > requirements.txt

2. gen spider

scrapy genspider cnbeta cnbeta.com

3. debug spider

scrapy crawl cnbeta

4. build image

make docker

5. start service

docker-compose up -d

6. use scrapyd

curl http://localhost:6800/schedule.json -d project=default -d spider=cnbeta

7. use admin pro

http://localhost:5002


```