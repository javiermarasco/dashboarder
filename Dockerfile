FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY /src/main.py .
COPY /src/templates ./templates
CMD [ "kopf", "run" , "--liveness=http://0.0.0.0:8080/healthz", "main.py", "-n", "*"] 
