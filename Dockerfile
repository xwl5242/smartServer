FROM python:3.7.2

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["gunicorn", "server:app", "-c", "./gunicorn.conf.py", "--log-level=debug"]
