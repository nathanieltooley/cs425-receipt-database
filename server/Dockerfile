FROM python:3.11-slim

WORKDIR /opt/Paperless

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python tableSetup.py

CMD ["gunicorn", "app:app", "-w", "4", "--bind", "0.0.0.0:8000"]
EXPOSE 8000