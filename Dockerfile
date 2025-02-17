FROM python:3.10.8

RUN apt update && apt upgrade -y && \
    apt install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt

WORKDIR /Deendayal_botz
COPY . .
CMD ["python", "bot.py"]


