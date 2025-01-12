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

    # Stats Cards
    html.Div([
        # Precios
        html.Div([
            html.Div([
                html.H3("Estadísticas de Precios", 
                       className="text-lg font-bold text-[#E85C3F] mb-4"),
                html.Div([
                    html.Div([
                        html.P("Promedio", className="text-sm text-gray-500"),
                        html.P(id="precio-promedio", 
                              className="text-2xl font-bold text-gray-800"),
                    ], className="flex-1"),
                    html.Div([
                        html.P("Mediana", className="text-sm text-gray-500"),
                        html.P(id="precio-mediana", 
                              className="text-2xl font-bold text-gray-800"),
                    ], className="flex-1"),
                    html.Div([
                        html.P("Moda", className="text-sm text-gray-500"),
                        html.P(id="precio-moda", 
                              className="text-2xl font-bold text-gray-800"),
                    ], className="flex-1"),
                    html.Div([
                        html.P("Mínimo", className="text-sm text-gray-500"),
                        html.P(id="precio-minimo", 
                              className="text-2xl font-bold text-gray-800"),
                    ], className="flex-1"),
                    html.Div([
                        html.P("Máximo", className="text-sm text-gray-500"),
                        html.P(id="precio-maximo", 
                              className="text-2xl font-bold text-gray-800"),
                    ], className="flex-1"),
                ], className="flex justify-between gap-4")
            ], className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-300")
        ], className="col-span-4"),

        # Reviews y Ratings
        html.Div([
            html.Div([
                html.H3("Métricas de Reviews", 
                       className="text-lg font-bold text-[#E85C3F] mb-4"),
                html.Div([
                    html.Div([
                        html.P("Rating Promedio", className="text-sm text-gray-500"),
                        html.P(id="rating-promedio", 
                              className="text-2xl font-bold text-gray-800"),
                    ], className="flex-1"),
                    html.Div([
                        html.P("Reviews/Año", className="text-sm text-gray-500"),
                        html.P(id="reviews-por-año", 
                              className="text-2xl font-bold text-gray-800"),
                    ], className="flex-1"),
                    html.Div([
                        html.P("Total Listados", className="text-sm text-gray-500"),
                        html.P(id="total-listados", 
                              className="text-2xl font-bold text-gray-800"),
                    ], className="flex-1"),
                ], className="flex justify-between gap-4")
            ], className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-300")
        ], className="col-span-2"),

        # Métricas de Propiedades
        html.Div([
            html.Div([
                html.H3("Métricas de Propiedades", 
                       className="text-lg font-bold text-[#E85C3F] mb-4"),
                html.Div([
                    html.Div([
                        html.P("Años Promedio Host", className="text-sm text-gray-500"),
                        html.P(id="años-promedio", 
                              className="text-2xl font-bold text-gray-800"),
                    ], className="flex-1"),
                    html.Div([
                        html.P("Ocupación Estimada", className="text-sm text-gray-500"),
                        html.P(id="ocupacion-estimada", 
                              className="text-2xl font-bold text-gray-800"),
                    ], className="flex-1"),
                    html.Div([
                        html.P("Ingreso Mensual Est.", className="text-sm text-gray-500"),
                        html.P(id="ingreso-mensual", 
                              className="text-2xl font-bold text-gray-800"),
                    ], className="flex-1"),
                ], className="flex justify-between gap-4")
            ], className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-300")
        ], className="col-span-2")
    ], className="grid grid-cols-4 gap-4 mb-6"),

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

    # Agrupar datos por años de anfitrión
    avg_ratings = filtered_df.groupby('years_hosting')['rating'].agg([
        'mean',
        'count',
        'std'
    ]).reset_index()
    
    years_hosting_rating_chart = px.scatter(
        avg_ratings,
        x="years_hosting",
        y="mean",
        size="count",  # Tamaño basado en cantidad de propiedades
        error_y="std",  # Barras de error para mostrar la variabilidad
        title="Promedio de Calificaciones por Años de Experiencia",
        labels={
            "years_hosting": "Años como Anfitrión",
            "mean": "Calificación Promedio",
            "count": "Cantidad de Propiedades"
        },
        template=theme,
        color_discrete_sequence=['#E85C3F']
    )

    years_hosting_rating_chart.update_layout(
        title={
            'text': f"Calificación promedio por años de anfitrión<br><sup>Tamaño del punto indica cantidad de propiedades</sup>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        hovermode='closest',
        showlegend=False,
        yaxis=dict(
            range=[4, 5.1],
            dtick=0.2,
            tickformat=".1f",
            title="Calificación Promedio"
        ),
        xaxis=dict(
            title="Años como Anfitrión",
            dtick=1
        )
    )

    years_hosting_rating_chart.update_traces(
        hovertemplate="<br>".join([
            "<b>Años como Anfitrión:</b> %{x}",
            "<b>Calificación Promedio:</b> %{y:.2f}",
            "<b>Cantidad de Propiedades:</b> %{marker.size}",
            "<extra></extra>"
        ])
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

@app.callback(
    [Output("precio-promedio", "children"),
     Output("precio-mediana", "children"),
     Output("precio-moda", "children"),
     Output("precio-minimo", "children"),
     Output("precio-maximo", "children"),
     Output("rating-promedio", "children"),
     Output("reviews-por-año", "children"),
     Output("total-listados", "children"),
     Output("años-promedio", "children"),
     Output("ocupacion-estimada", "children"),
     Output("ingreso-mensual", "children")],
    [Input("bathroom-filter", "value"),
     Input("bedroom-filter", "value"),
     Input("beds-filter", "value")]
)
def update_stats(baths, bedrooms, beds):
    filtered_df = df
    if baths is not None:
        filtered_df = filtered_df[filtered_df["baths"] == baths]
    if bedrooms is not None:
        filtered_df = filtered_df[filtered_df["bedrooms"] == bedrooms]
    if beds is not None:
        filtered_df = filtered_df[filtered_df["beds"] == beds]
    
    # Calcular estadísticas
    precio_moda = filtered_df['price_original'].mode().iloc[0] if not filtered_df.empty else 0
    ocupacion_estimada = min(filtered_df['reviews_per_year'].mean() * 3, 100) if not filtered_df.empty else 0
    precio_promedio = filtered_df['price_original'].mean() if not filtered_df.empty else 0
    ingreso_mensual = (precio_promedio * 30 * (ocupacion_estimada/100))
    
    stats = {
        "precio_promedio": f"${precio_promedio:.0f}",
        "precio_mediana": f"${filtered_df['price_original'].median():.0f}",
        "precio_moda": f"${precio_moda:.0f}",
        "precio_minimo": f"${filtered_df['price_original'].min():.0f}",
        "precio_maximo": f"${filtered_df['price_original'].max():.0f}",
        "rating_promedio": f"{filtered_df['rating'].mean():.1f}",
        "reviews_año": f"{filtered_df['reviews_per_year'].mean():.1f}",
        "total_listados": f"{len(filtered_df)}",
        "años_promedio": f"{filtered_df['years_hosting'].mean():.1f}",
        "ocupacion_estimada": f"{ocupacion_estimada:.0f}%",
        "ingreso_mensual": f"${ingreso_mensual:.0f}"
    }
    
    return [
        stats["precio_promedio"],
        stats["precio_mediana"],
        stats["precio_moda"],
        stats["precio_minimo"],
        stats["precio_maximo"],
        stats["rating_promedio"],
        stats["reviews_año"],
        stats["total_listados"],
        stats["años_promedio"],
        stats["ocupacion_estimada"],
        stats["ingreso_mensual"]
    ]

if __name__ == "__main__":
    app.run_server(debug=True)
