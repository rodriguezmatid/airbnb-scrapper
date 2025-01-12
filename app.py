import dash
from src.data.loader import DataLoader
from src.data.processor import DataProcessor
from src.dashboard.layout import create_layout
from src.dashboard.callbacks import register_callbacks

# Inicializar datos
data_loader = DataLoader()
df = data_loader.load_csv("airbnb_data.csv")

if df.empty:
    print("Error: No se pudieron cargar los datos. Verificar la ubicación del archivo CSV.")
    exit(1)

df = DataProcessor.calculate_reviews_per_year(df)

# Configurar Dash
app = dash.Dash(__name__)
server = app.server

# Crear layout
app.layout = create_layout(df)

# Registrar callbacks
register_callbacks(app, df)

if __name__ == "__main__":
    app.run_server(debug=True)
