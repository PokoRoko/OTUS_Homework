# OTUServer

## Задание
- Разработать веб-сервер частично реализующий протокол HTTP, архитектуру выбрать самостоятельно.
- Разрешается использовать библиотеки помогающие реализовать асинхронную обработку соединений, запрещается
использовать библиотеки реализующие какую-либо часть обработки HTTP. Работать с сокетами и всем прочим нужно
самостоятельно.
- Провести нагрузочное тестирование, проверку стабильности и корректности работы.
- Если сервер асинхронный, то обязательно использовать epoll (https://github.com/m13253/python-asyncore-epoll)
- Подсказка: некоторые фичи (например, SO_REUSEPORT) могут некорректно работать на Mac и прочих недо-Unix системах.
- Лучше экспериментировать в контейнере с CentOS 7 или тому подобным.  

### Веб-сервер должен уметь:
1) Масштабироваться на несколько worker'ов
2) Число worker'ов задается аргументом командной строки - w
3) Отвечать 200 , 403 или 404 на GET-запросы и HEAD-запросы
4) Отвечать 405 на прочие запросы
5) Возвращать файлы по произвольному пути в DOCUMENT_ROOT.
6) Вызов /file.html должен возвращать содердимое DOCUMENT_ROOT/file.html
7) DOCUMENT_ROOT задается аргументом командной строки - r
8) Возвращать index.html как индекс директории
9) Вызов /directory/ должен возвращать DOCUMENT_ROOT/directory/index.html
10) Отвечать следующими заголовками для успешных GET-запросов: Date, Server, Content-Length, Content-Type, Connection
11) Корректный Content-Type для: .html, .css, .js, .jpg, .jpeg, .png, .gif, .swf
12) Понимать пробелы и %XX в именах файлов  

### Что проверять:
1) Проходят тесты https://github.com/s-stupnikov/http-test-suite
2) http://localhost/httptest/wikipedia_russia.html корректно показывается в браузере
3) Нагрузочное тестирование: запускаем ab -n 50000 -c 100 -r http://localhost:8080/ и смотрим результат
4) Опционально: вместо ab воспользоваться wrk

### Запуск проекта
1) Установка зависимостей не требуется  
2) Запуск `python3 my_log_analyzer.py`

### Результаты нагрузочного тестирования
```
Server Software:        OTUServer
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        0 bytes
```

Concurrency Level:      100
Time taken for tests:   14.914 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      4100000 bytes
HTML transferred:       0 bytes
Requests per second:    3352.49 [#/sec] (mean)
Time per request:       29.829 [ms] (mean)
Time per request:       0.298 [ms] (mean, across all concurrent requests)
Transfer rate:          268.46 [Kbytes/sec] received

#### Connection Times (ms)

|             | min |mean|[+/-sd]|median| max  | 
|-------------|-----|----|-------|------|------| 
| Connect:    | 0   | 0  | 13.6  | 0    | 1025 | 
| Processing: | 2   | 30 | 4.7   | 28   | 234  | 
| Waiting:    | 1   | 29 | 4.7   | 28   | 234  | 
| Total:      | 7   | 30 | 14.9  | 28   | 1244 |


#### Percentage of the requests served within a certain time (ms)

| perc | ms   |
|------|------|
| 50%  | 28   |
| 66%  | 30   |
| 75%  | 31   |
| 80%  | 32   |
| 90%  | 35   |
| 95%  | 39   |
| 98%  | 43   |
| 99%  | 45   |
| 100% | 1244 |
