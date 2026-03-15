FROM python:3.13-slim
ENV TZ="Europe/Berlin"
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y python3 && apt-get install -y python3-pip
RUN pip3 install -r /app/requirements.txt
ENTRYPOINT ["python3"]
CMD ["main.py"]