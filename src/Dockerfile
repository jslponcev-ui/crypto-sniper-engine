# Usamos una imagen ligera de Python
FROM python:3.9-slim

# Directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando para ejecutar el bot
CMD ["python", "main.py"]