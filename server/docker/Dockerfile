FROM python:3.11-slim

WORKDIR /opt/Paperless

COPY ../requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY .. .
COPY docker_config.json config.json

RUN python configure.py initialize both --clean

CMD ["gunicorn", "app:create_app", "-w", "4", "--bind", "0.0.0.0:8000"]
EXPOSE 8000