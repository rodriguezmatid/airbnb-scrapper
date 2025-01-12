from dash import html, dcc
from ..charts.theme import StayBATheme

def create_layout(df):
    """Crea el layout principal del dashboard"""
    return html.Div([
        create_header(),
        create_filters(df),
        create_stats_cards(),
        create_charts_grid()
    ], className="min-h-screen bg-gray-50 p-6")

def create_header():
    """Crea la sección del header"""
    return html.Div([
        html.Div([
            html.Img(src='assets/stayba-logo.png', 
                    className="h-10 mr-4"),
            html.H1("StayBA Analytics", 
                   className="text-2xl font-bold text-[#E85C3F]")
        ], className="flex items-center"),
        
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
    ], className="bg-gradient-to-r from-[#E85C3F] to-[#FF8B6A] p-4 rounded-xl shadow-lg flex justify-between items-center mb-6")

def create_filters(df):
    """Crea la sección de filtros"""
    return html.Div([
        create_filter("BAÑOS", "bathroom-filter", df["baths"]),
        create_filter("HABITACIONES", "bedroom-filter", df["bedrooms"]),
        create_filter("CAMAS", "beds-filter", df["beds"])
    ], className="grid grid-cols-3 gap-4 mb-6 bg-gray-100 p-4 rounded-xl")

def create_filter(label, id_name, data):
    """Crea un filtro individual"""
    return html.Div([
        html.Label(label, className="text-xs font-bold text-gray-600 block mb-2"),
        dcc.Dropdown(
            id=id_name,
            options=[{"label": f"{i}", "value": i} 
                    for i in sorted(data.dropna().unique())],
            placeholder="Seleccionar",
            className="w-full"
        ),
    ], className="bg-white p-4 rounded-lg shadow-sm")

def create_stats_cards():
    """Crea la sección de estadísticas"""
    return html.Div([
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
    ], className="grid grid-cols-4 gap-4 mb-6")

def create_charts_grid():
    """Crea el grid de gráficos"""
    return html.Div([
        create_chart_container("reviews-price-chart"),
        create_chart_container("guests-total-chart"),
        create_chart_container("rating-total-chart"),
        create_chart_container("beds-total-chart"),
        create_chart_container("years-hosting-rating-chart"),
        create_chart_container("reviews-per-year-chart"),
        create_chart_container("reviews-per-year-heatmap-years"),
        create_chart_container("reviews-per-year-heatmap-price")
    ], className="grid grid-cols-2 gap-6")

def create_chart_container(chart_id):
    """Crea un contenedor para un gráfico"""
    return html.Div([
        dcc.Graph(id=chart_id)
    ], className="bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition-shadow") 