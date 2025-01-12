# Airbnb Buenos Aires - Dashboard de Análisis

Dashboard interactivo para analizar datos de propiedades de Airbnb en Buenos Aires. Visualiza métricas clave como precios, ratings, reseñas y características de las propiedades.

## Características

### Visualizaciones Interactivas
- Relación entre reseñas y precios por noche
- Distribución de precios por cantidad de huéspedes
- Análisis de ratings según experiencia del anfitrión
- Distribución de reseñas anuales
- Análisis de precios por cantidad de camas y baños

### Métricas en Tiempo Real
- Precios (promedio, mediana, moda, mínimo, máximo)
- Rating promedio
- Reseñas por año
- Total de listados
- Años promedio como anfitrión
- Ocupación estimada
- Ingreso mensual estimado

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/airbnb-scrapper.git
cd airbnb-scrapper
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate  # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

### Local
```bash
python app.py
```

### Servidor (producción)
```bash
nohup python3 app.py > app.log 2>&1 &
```

El dashboard está disponible en:
```
http://54.232.166.13:8050
```

## Estructura del Proyecto
```
airbnb-scrapper/
├── app.py              # Aplicación Dash
├── main.py            # Script principal
├── render.yaml        # Configuración de despliegue
├── requirements.txt   # Dependencias
└── src/
    ├── charts/
    │   ├── scatter.py      # Gráficos de dispersión
    │   ├── distribution.py # Histogramas y boxplots
    │   └── theme.py        # Configuración de temas
    └── dashboard/
        └── callbacks.py     # Lógica de interactividad
```

## Tecnologías

- Python 3.8+
- Dash & Plotly
- Pandas
- NumPy

## Mantenimiento

Verificar estado del servicio:
```bash
ps aux | grep python
```
Este comando muestra todos los procesos de Python en ejecución, permitiéndote identificar el PID y estado de la aplicación.

Detener el servicio:
```bash
pkill -f "python app.py"
```