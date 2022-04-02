```commandline
docker-compose run -d --user "$(id -u):$(id -g)" html2reader
```

```commandline
docker-compose build
docker login
docker-compose push
```

```commandline
docker-compose run -v "{path_to_your_reader_dropbox}":/app/results --user "$(id -u):$(id -g)" html2reader https://ru.wikipedia.org/wiki/FictionBook
```