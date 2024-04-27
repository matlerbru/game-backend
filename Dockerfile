FROM python:3.11

WORKDIR /usr/src

COPY . .
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p output

COPY app app

ENTRYPOINT ["python3", "app/server.py"]
