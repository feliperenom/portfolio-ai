# Usar una imagen base ligera de Python
FROM python:3.9-slim

# Configurar el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos necesarios
COPY requirements.txt .
COPY system_prompt.txt .

# Instalar dependencias
RUN pip install -r requirements.txt

# Copiar el resto del código fuente
COPY . .

# Exponer el puerto 8080 para Cloud Run
EXPOSE 8080

# Comando para iniciar la aplicación con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]