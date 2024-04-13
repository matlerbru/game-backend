FROM python:3.11

WORKDIR /usr/src/app

COPY . .
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p output

COPY src .

ENTRYPOINT ["python3", "/usr/src/app/src/server.py"]