# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos necesarios
COPY . /app

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto del servidor
EXPOSE 8000

# Ejecutar el dashboard (asegúrate de que app.py contiene el dashboard)
CMD ["python", "app.py"]
