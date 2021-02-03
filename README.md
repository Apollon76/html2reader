# html2reader
A tool for saving any web page in fb2 format.
## Typical usage example
```
docker-compose run -v "{path_to_your_reader_dropbox}":/app/results --user "$(id -u):$(id -g)" html2reader https://ru.wikipedia.org/wiki/FictionBook
```
