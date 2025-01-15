FROM python:3.10.8-slim-buster
RUN apt update && apt upgrade -y && apt install git -y && rm -rf /var/lib/apt/lists/*
WORKDIR /Deendayal-botz

COPY requirements.txt .
RUN pip3 install -U pip && pip3 install --no-cache-dir -r requirements.txt

COPY . .


CMD ["python", "bot.py"]

