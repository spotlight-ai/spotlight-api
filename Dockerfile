FROM python:3.6

COPY . /app

WORKDIR /app

RUN apt-get update -y && apt-get install -y poppler-utils

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["app.py"]