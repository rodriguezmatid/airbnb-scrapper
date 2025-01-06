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

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.RadioItems(
                id="theme-selector",
                options=[
                    {"label": "Light", "value": "plotly_white"},
                    {"label": "Dark", "value": "plotly_dark"}
                ],
                value="plotly_white",
                inline=True,
                style={"float": "left", "marginLeft": "20px", "marginTop": "10px"}
            ),
        ], style={"textAlign": "left"}),
        html.H1("StayBA Scrapper", style={
            "textAlign": "center", 
            "color": "white", 
            "backgroundColor": "#2c3e50", 
            "padding": "20px", 
            "borderRadius": "10px"
        }),
    ], style={"marginBottom": "20px", "position": "relative"}),

    html.Div([
        html.Div([
            html.Div([
                html.Label("Baths", style={"fontSize": "16px", "fontWeight": "bold", "marginBottom": "5px"}),
                dcc.Dropdown(
                    id="bathroom-filter",
                    options=[
                        {"label": f"{i}", "value": i} for i in sorted(df["baths"].dropna().unique())
                    ] if not df.empty else [],
                    placeholder="Select Baths",
                    style={"width": "100%", "marginBottom": "10px"}
                ),
            ], style={"display": "inline-block", "width": "30%", "verticalAlign": "top", "marginRight": "10px"}),

            html.Div([
                html.Label("Bedrooms", style={"fontSize": "16px", "fontWeight": "bold", "marginBottom": "5px"}),
                dcc.Dropdown(
                    id="bedroom-filter",
                    options=[
                        {"label": f"{i}", "value": i} for i in sorted(df["bedrooms"].dropna().unique())
                    ] if not df.empty else [],
                    placeholder="Select Bedrooms",
                    style={"width": "100%", "marginBottom": "10px"}
                ),
            ], style={"display": "inline-block", "width": "30%", "verticalAlign": "top", "marginRight": "10px"}),

            html.Div([
                html.Label("Beds", style={"fontSize": "16px", "fontWeight": "bold", "marginBottom": "5px"}),
                dcc.Dropdown(
                    id="beds-filter",
                    options=[
                        {"label": f"{i}", "value": i} for i in sorted(df["beds"].dropna().unique())
                    ] if not df.empty else [],
                    placeholder="Select Beds",
                    style={"width": "100%", "marginBottom": "10px"}
                ),
            ], style={"display": "inline-block", "width": "30%", "verticalAlign": "top"}),
        ], style={"marginBottom": "20px", "textAlign": "center"}),

        html.Div([
            dcc.Graph(id="reviews-price-chart", style={
                "marginBottom": "40px",
                "border": "1px solid #ccc",
                "borderRadius": "10px",
                "boxShadow": "2px 2px 10px #aaa",
                "backgroundColor": "white"
            }),
            dcc.Graph(id="guests-total-chart", style={
                "marginBottom": "40px",
                "border": "1px solid #ccc",
                "borderRadius": "10px",
                "boxShadow": "2px 2px 10px #aaa",
                "backgroundColor": "white"
            }),
            dcc.Graph(id="rating-total-chart", style={
                "marginBottom": "40px",
                "border": "1px solid #ccc",
                "borderRadius": "10px",
                "boxShadow": "2px 2px 10px #aaa",
                "backgroundColor": "white"
            }),
            dcc.Graph(id="beds-total-chart", style={
                "marginBottom": "40px",
                "border": "1px solid #ccc",
                "borderRadius": "10px",
                "boxShadow": "2px 2px 10px #aaa",
                "backgroundColor": "white"
            }),
            html.Div([
                dcc.Graph(id="years-hosting-rating-chart", style={
                    "display": "inline-block", "width": "49%", "marginRight": "1%",
                    "border": "1px solid #ccc",
                    "borderRadius": "10px",
                    "boxShadow": "2px 2px 10px #aaa",
                    "backgroundColor": "white"
                }),
                dcc.Graph(id="reviews-per-year-chart", style={
                    "display": "inline-block", "width": "49%",
                    "border": "1px solid #ccc",
                    "borderRadius": "10px",
                    "boxShadow": "2px 2px 10px #aaa",
                    "backgroundColor": "white"
                }),
            ], style={"padding": "20px"}),
            html.Div([
                dcc.Graph(id="reviews-per-year-heatmap-years", style={
                    "display": "inline-block", "width": "49%", "marginRight": "1%",
                    "border": "1px solid #ccc",
                    "borderRadius": "10px",
                    "boxShadow": "2px 2px 10px #aaa",
                    "backgroundColor": "white"
                }),
                dcc.Graph(id="reviews-per-year-heatmap-price", style={
                    "display": "inline-block", "width": "49%",
                    "border": "1px solid #ccc",
                    "borderRadius": "10px",
                    "boxShadow": "2px 2px 10px #aaa",
                    "backgroundColor": "white"
                }),
            ], style={"padding": "20px"}),
        ], style={"padding": "20px"}),
    ])
], style={
    "fontFamily": "Arial, sans-serif", 
    "backgroundColor": "#ecf0f1", 
    "padding": "20px",
    "maxWidth": "1200px",
    "margin": "auto",
    "borderRadius": "10px",
    "boxShadow": "2px 2px 15px #aaa"
})

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
        title="Number of Reviews vs Price Per Night",
        labels={"reviews": "Number of Reviews", "price_original": "Price Per Night"},
        template=theme,
        color_continuous_scale="Viridis",
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
