FROM python:3.8-slim
ADD . /code
WORKDIR /code
COPY scrapyd.conf /etc/scrapyd/
COPY requirements.txt .
COPY gunicorn.conf.py .
EXPOSE 6800
RUN pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD chmod -R 777 /code/logs && gunicorn --config gunicorn.conf.py 'spider_admin_pro.main:app' && scrapyd
