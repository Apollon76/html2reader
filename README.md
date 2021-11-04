  docker-compose run -d --user "$(id -u):$(id -g)" html2reader

  docker-compose build
  docker login
  docker-compose push
