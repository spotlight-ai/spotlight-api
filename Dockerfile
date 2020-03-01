FROM python:3.6

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt
RUN flask db upgrade

ENTRYPOINT ["python"]

CMD ["app.py"]