# Consulta Miembro de Mesa - ONPE
FROM python:3.11-slim

LABEL maintainer="jfarfan@tecsup.edu.pe"
LABEL description="Consulta Miembro de Mesa - ONPE"

WORKDIR /app

# Instalar Chrome para Selenium
RUN apt-get update && apt-get install -y wget gnupg curl && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]