import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from os import environ

# Cargar los datos desde el CSV
def cargar_datos():
    try:
        df = pd.read_csv("airbnb_data.csv")  # Ruta actualizada
        df["reviews_per_year"] = df["reviews"] / df["years_hosting"].replace(0, 1)  # Evitar divisiones por cero
        print("Datos cargados correctamente:")
        print(df.head())  # Muestra las primeras filas
        print(df.info())  # Muestra información sobre los datos
        return df
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error

df = cargar_datos()

# Configurar Dash
app = dash.Dash(__name__)
server = app.server  # Esta es la aplicación WSGI que Gunicorn necesita

# Actualizar colores y estilos de StayBA
STAYBA_COLORS = {
    'primary': '#E85C3F',      # Naranja StayBA
    'secondary': '#2c3e50',    # Azul oscuro
    'background': '#FFFFFF',   # Fondo blanco
    'light_gray': '#f8f9fa',  # Gris claro para secciones
    'text': '#2c3e50',        # Color texto principal
    'accent': '#FF8B6A'       # Naranja más claro para acentos
}

app.layout = html.Div([
    # Header con logo y título
    html.Div([
        # Logo y título
        html.Div([
            html.Img(src='assets/stayba-logo.png', 
                    className="h-10 mr-4"),
            html.H1("StayBA Analytics", 
                   className="text-2xl font-bold text-[#E85C3F]")
        ], className="flex items-center"),
        
        # Selector de tema
        html.Div([
            dcc.RadioItems(
                id="theme-selector",
                options=[
                    {"label": "☀️", "value": "plotly_white"},
                    {"label": "🌙", "value": "plotly_dark"}
                ],
                value="plotly_white",
                inline=True,
                className="bg-white bg-opacity-10 px-4 py-2 rounded-full text-white"
            ),
        ])
    ], className="bg-gradient-to-r from-[#E85C3F] to-[#FF8B6A] p-4 rounded-xl shadow-lg flex justify-between items-center mb-6"),

    # Filtros en una fila
    html.Div([
        html.Div([
            html.Label("BAÑOS", className="text-xs font-bold text-gray-600 block mb-2"),
            dcc.Dropdown(
                id="bathroom-filter",
                options=[{"label": f"{i}", "value": i} for i in sorted(df["baths"].dropna().unique())] if not df.empty else [],
                placeholder="Seleccionar",
                className="w-full"
            ),
        ], className="bg-white p-4 rounded-lg shadow-sm"),

        html.Div([
            html.Label("HABITACIONES", className="text-xs font-bold text-gray-600 block mb-2"),
            dcc.Dropdown(
                id="bedroom-filter",
                options=[{"label": f"{i}", "value": i} for i in sorted(df["bedrooms"].dropna().unique())] if not df.empty else [],
                placeholder="Seleccionar",
                className="w-full"
            ),
        ], className="bg-white p-4 rounded-lg shadow-sm"),

        html.Div([
            html.Label("CAMAS", className="text-xs font-bold text-gray-600 block mb-2"),
            dcc.Dropdown(
                id="beds-filter",
                options=[{"label": f"{i}", "value": i} for i in sorted(df["beds"].dropna().unique())] if not df.empty else [],
                placeholder="Seleccionar",
                className="w-full"
            ),
        ], className="bg-white p-4 rounded-lg shadow-sm"),
    ], className="grid grid-cols-3 gap-4 mb-6 bg-gray-100 p-4 rounded-xl"),

    # Grid de gráficos
    html.Div([
        html.Div([
            dcc.Graph(id="reviews-price-chart")
        ], className="bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow"),
        
        html.Div([
            dcc.Graph(id="guests-total-chart")
        ], className="bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow"),
        
        html.Div([
            dcc.Graph(id="rating-total-chart")
        ], className="bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow"),
        
        html.Div([
            dcc.Graph(id="beds-total-chart")
        ], className="bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow"),
        
        html.Div([
            dcc.Graph(id="years-hosting-rating-chart")
        ], className="bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow"),
        
        html.Div([
            dcc.Graph(id="reviews-per-year-chart")
        ], className="bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow"),
        
        html.Div([
            dcc.Graph(id="reviews-per-year-heatmap-years")
        ], className="bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow"),
        
        html.Div([
            dcc.Graph(id="reviews-per-year-heatmap-price")
        ], className="bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow"),
    ], className="grid grid-cols-2 gap-6")

], className="min-h-screen bg-gray-50 p-6")

@app.callback(
    [
        Output("reviews-price-chart", "figure"),
        Output("guests-total-chart", "figure"),
        Output("rating-total-chart", "figure"),
        Output("beds-total-chart", "figure"),
        Output("years-hosting-rating-chart", "figure"),
        Output("reviews-per-year-chart", "figure"),
        Output("reviews-per-year-heatmap-years", "figure"),
        Output("reviews-per-year-heatmap-price", "figure")
    ],
    [Input("bathroom-filter", "value"),
     Input("bedroom-filter", "value"),
     Input("beds-filter", "value"),
     Input("theme-selector", "value")]
)
def update_charts(baths, bedrooms, beds, theme):
    if df.empty:
        empty_fig = px.scatter(title="No data available")
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    filtered_df = df
    if baths is not None:
        filtered_df = filtered_df[filtered_df["baths"] == baths]
    if bedrooms is not None:
        filtered_df = filtered_df[filtered_df["bedrooms"] == bedrooms]
    if beds is not None:
        filtered_df = filtered_df[filtered_df["beds"] == beds]

    print(f"Filtrado con baths={baths}, bedrooms={bedrooms}, beds={beds}: {len(filtered_df)} filas")

    reviews_price_fig = px.scatter(
        filtered_df,
        x="reviews",
        y="price_original",
        color="rating",
        size="price_original",
        title="Reseñas vs Precio por Noche",
        labels={"reviews": "Número de Reseñas", "price_original": "Precio por Noche"},
        template=theme,
        color_continuous_scale=[[0, '#E85C3F'], [1, '#FF8B6A']],
        size_max=30
    )

    guests_total_fig = px.scatter(
        filtered_df,
        x="guests",
        y="price_original",
        color="rating",
        size="price_original",
        title="Guests vs Price Per Night",
        labels={"guests": "Number of Guests", "price_original": "Price Per Night"},
        template=theme,
        color_continuous_scale="Plasma",
        size_max=30
    )

    rating_total_fig = px.scatter(
        filtered_df,
        x="rating",
        y="price_original",
        color="reviews",
        size="reviews",
        title="Rating vs Price Per Night",
        labels={"rating": "Rating", "price_original": "Price Per Night"},
        template=theme,
        color_continuous_scale="Cividis",
        size_max=30
    )

    beds_total_fig = px.scatter(
        filtered_df,
        x="beds",
        y="price_original",
        color="rating",
        size="price_original",
        title="Beds vs Price Per Night",
        labels={"beds": "Number of Beds", "price_original": "Price Per Night"},
        template=theme,
        color_continuous_scale="Inferno",
        size_max=30
    )

    years_hosting_rating_chart = px.line(
        filtered_df,
        x="years_hosting",
        y="rating",
        title="Years Hosting vs Rating",
        labels={"years_hosting": "Years Hosting", "rating": "Rating"},
        template=theme,
        markers=True
    )

    reviews_per_year_chart = px.bar(
        filtered_df,
        x=filtered_df.index + 1,  # Usar el índice como eje X
        y="reviews_per_year",
        title="Reviews Per Year Hosting",
        labels={"x": "Index", "reviews_per_year": "Reviews Per Year"},
        template=theme
    )

    reviews_per_year_heatmap_years = px.bar(
        filtered_df,
        x=filtered_df.index + 1,
        y="reviews_per_year",
        color="years_hosting",
        title="Reviews Per Year Hosting (Color by Years Hosting)",
        labels={"x": "Index", "reviews_per_year": "Reviews Per Year"},
        template=theme,
        color_continuous_scale="Viridis"
    )

    reviews_per_year_heatmap_price = px.bar(
        filtered_df,
        x=filtered_df.index + 1,
        y="reviews_per_year",
        color="price_original",
        title="Reviews Per Year Hosting (Color by Price Per Night)",
        labels={"x": "Index", "reviews_per_year": "Reviews Per Year"},
        template=theme,
        color_continuous_scale="Plasma"
    )

    return reviews_price_fig, guests_total_fig, rating_total_fig, beds_total_fig, years_hosting_rating_chart, reviews_per_year_chart, reviews_per_year_heatmap_years, reviews_per_year_heatmap_price

if __name__ == "__main__":
    app.run_server(debug=True)
