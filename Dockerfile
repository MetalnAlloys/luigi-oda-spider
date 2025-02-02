FROM python:3.10

ADD . /app

WORKDIR /app

RUN pip install -e .

CMD ["luigi", "GetProducts", "--module=luigi-oda-spider", "--base-url=https://oda.com/no", "--target-name=oda", "--local-scheduler"]
