
FROM python:3.10.8-slim-buster
RUN apt update && apt upgrade -y && apt install git -y
WORKDIR /Princess
RUN pip3 install --no-cache-dir virtualenv
RUN virtualenv venv
RUN /Princess/venv/bin/pip install -U pip
COPY requirements.txt .
RUN /Princess/venv/bin/pip install -r requirements.txt

COPY . .
EXPOSE 8080
CMD ["/Princess/venv/bin/python", "bot.py"]

