# -*- coding:utf-8 -*-

workers = 4
worker_class = "gevent"
loglevel = "debug"
accesslog = "/var/logs/gunicorn.access.log"
errorlog = "/var/logs/gunicorn.error.log"
bind = "0.0.0.0:8082"


