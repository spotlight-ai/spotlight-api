FROM python:3.6

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["flask", "db", "init"]
CMD ["flask", "db", "migrate"]
CMD ["flask", "db", "upgrade"]

CMD ["app.py"]