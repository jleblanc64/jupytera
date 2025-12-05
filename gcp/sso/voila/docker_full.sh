docker build -t app_cars .
docker stop $(docker ps -aq) && docker rm $(docker ps -aq)
docker run -p 8080:8080 app_cars