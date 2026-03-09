# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

FROM python:3.10-slim

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y git

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

COPY . /app
WORKDIR /app

CMD ["python3","bot.py"]

