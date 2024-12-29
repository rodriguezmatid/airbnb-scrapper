# Usa una imagen base de Python
FROM python:3.9-slim

# Configura el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de tu proyecto al contenedor
COPY . /app

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expón el puerto 8000 (necesario para Dash y Gunicorn)
EXPOSE 8000

# Configura el comando para iniciar la aplicación
CMD ["gunicorn", "app:server", "-b", "0.0.0.0:8000"]
