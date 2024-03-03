FROM python:3.9
COPY . /app/
RUN pip --no-cache-dir install -r /app/requirements.txt
WORKDIR /app
CMD ["python3", "main.py"]
