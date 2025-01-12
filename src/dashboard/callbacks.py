from dash.dependencies import Input, Output
from src.charts.scatter import ScatterChart
from src.charts.distribution import DistributionChart

def register_callbacks(app, df):
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
        # Filtrar datos
        filtered_df = df.copy()
        if baths is not None:
            filtered_df = filtered_df[filtered_df["baths"] == baths]
        if bedrooms is not None:
            filtered_df = filtered_df[filtered_df["bedrooms"] == bedrooms]
        if beds is not None:
            filtered_df = filtered_df[filtered_df["beds"] == beds]
        
        scatter = ScatterChart(theme)
        
        reviews_price_fig = scatter.create(
            filtered_df,
            x="reviews",
            y="price_original",
            color="rating",
            size="price_original",
            title="Reseñas vs precio por noche",
            subtitle="Muestra la relación entre el número de reseñas y el precio, el tamaño indica el precio y el color el rating",
            labels={
                "reviews": "Número de reseñas",
                "price_original": "Precio por noche"
            }
        )
        
        guests_total_fig = scatter.create(
            filtered_df,
            x="guests",
            y="price_original",
            color="rating",
            size="price_original",
            title="Huéspedes vs precio por noche",
            subtitle="Analiza cómo varía el precio según la capacidad de huéspedes, el color indica el rating",
            labels={
                "guests": "Número de huéspedes",
                "price_original": "Precio por noche"
            }
        )
        
        rating_total_fig = scatter.create(
            filtered_df,
            x="rating",
            y="price_original",
            color="reviews",
            size="reviews",
            title="Rating vs precio por noche",
            subtitle="Relación entre calificación y precio, el tamaño y color indican cantidad de reseñas",
            labels={
                "rating": "Calificación",
                "price_original": "Precio por noche"
            }
        )
        
        beds_total_fig = scatter.create(
            filtered_df,
            x="beds",
            y="price_original",
            color="rating",
            size="price_original",
            title="Camas vs precio por noche",
            subtitle="Muestra cómo el precio varía según el número de camas, el color indica el rating",
            labels={
                "beds": "Número de camas",
                "price_original": "Precio por noche"
            }
        )
        
        # Agrupar datos por años de anfitrión
        avg_ratings = filtered_df.groupby('years_hosting')['rating'].agg([
            'mean',
            'count',
            'std'
        ]).reset_index()
        
        years_hosting_rating_chart = scatter.create(
            avg_ratings,
            x="years_hosting",
            y="mean",
            size="count",
            error_y="std",
            title="Calificación promedio por años de experiencia",
            subtitle="El tamaño indica cantidad de propiedades, las barras muestran la variabilidad",
            labels={
                "years_hosting": "Años como anfitrión",
                "mean": "Calificación promedio",
                "count": "Cantidad de propiedades"
            }
        )
        
        distribution = DistributionChart(theme)
        
        reviews_per_year_chart = distribution.create_histogram(
            filtered_df,
            x="reviews_per_year",
            title="Distribución de reseñas por año",
            subtitle="Muestra qué tan común es cada cantidad de reseñas anuales",
            labels={
                "reviews_per_year": "Reseñas por Año",
            }
        )
        
        # Para el gráfico de reseñas por experiencia
        avg_reviews = filtered_df.groupby('years_hosting').agg({
            'reviews_per_year': ['mean', 'count', 'std']
        }).reset_index()
        avg_reviews.columns = ['years_hosting', 'reviews_mean', 'count', 'std']

        reviews_per_year_heatmap_years = scatter.create(
            avg_reviews,
            x="years_hosting",
            y="reviews_mean",
            size="count",
            color="count",
            error_y="std",
            title="Reseñas por año según experiencia del anfitrión",
            subtitle="Promedio de reseñas anuales agrupado por años de experiencia. El color y tamaño indican cantidad de propiedades",
            labels={
                "years_hosting": "Años como anfitrión",
                "reviews_mean": "Promedio de reseñas por año",
                "count": "# propiedades"
            },
            color_continuous_scale=[[0, '#FED8B1'], [1, '#E85C3F']],  # De naranja claro a oscuro
            # O podríamos usar otras escalas como:
            # color_continuous_scale=[[0, '#FFE5D9'], [1, '#7A0A03']],  # Naranja claro a rojo oscuro
            # color_continuous_scale='Viridis',  # Escala predefinida que va de azul a amarillo
            # color_continuous_scale='RdBu',     # Rojo a azul
        )
        
        distribution = DistributionChart(theme)
        
        reviews_per_year_heatmap_price = distribution.create_boxplot(
            filtered_df,
            x="price_original",
            y="reviews_per_year",
            title="Distribución de Reseñas por Rango de Precio",
            subtitle="Muestra cómo varían las reseñas anuales según el rango de precio de la propiedad",
            labels={
                "price_range": "Rango de Precio",
                "reviews_per_year": "Reseñas por Año"
            }
        )
        
        return (
            reviews_price_fig,
            guests_total_fig,
            rating_total_fig,
            beds_total_fig,
            years_hosting_rating_chart,
            reviews_per_year_chart,
            reviews_per_year_heatmap_years,
            reviews_per_year_heatmap_price
        )

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
        filtered_df = df.copy()
        if baths is not None:
            filtered_df = filtered_df[filtered_df["baths"] == baths]
        if bedrooms is not None:
            filtered_df = filtered_df[filtered_df["bedrooms"] == bedrooms]
        if beds is not None:
            filtered_df = filtered_df[filtered_df["beds"] == beds]

        # Calcular estadísticas
        stats = {
            "precio_promedio": f"${filtered_df['price_original'].mean():.0f}",
            "precio_mediana": f"${filtered_df['price_original'].median():.0f}",
            "precio_moda": f"${filtered_df['price_original'].mode().iloc[0]:.0f}",
            "precio_minimo": f"${filtered_df['price_original'].min():.0f}",
            "precio_maximo": f"${filtered_df['price_original'].max():.0f}",
            "rating_promedio": f"{filtered_df['rating'].mean():.1f}",
            "reviews_año": f"{filtered_df['reviews_per_year'].mean():.1f}",
            "total_listados": f"{len(filtered_df)}",
            "años_promedio": f"{filtered_df['years_hosting'].mean():.1f}",
            "ocupacion_estimada": f"{estimate_occupancy(filtered_df['reviews_per_year'].mean()):.0f}%",
            "ingreso_mensual": f"${filtered_df['price_original'].mean() * 30:.0f}"
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

    # Retornar None al final de register_callbacks
    return None 

def estimate_occupancy(reviews_per_year):
    """
    Estima la ocupación basada en reseñas por año usando un modelo más sofisticado:
    - Asume que solo 30% de los huéspedes dejan reseña
    - Asume un promedio de 3 noches por estadía
    - Limita el resultado a 100%
    """
    review_rate = 0.30  # 30% de huéspedes dejan reseña
    nights_per_stay = 3  # promedio de noches por estadía
    
    # Calcular noches ocupadas
    stays = reviews_per_year / review_rate  # número real de estadías
    nights_occupied = stays * nights_per_stay
    
    # Convertir a porcentaje de ocupación (365 días al año)
    occupancy = (nights_occupied / 365) * 100
    
    return min(occupancy, 100) 