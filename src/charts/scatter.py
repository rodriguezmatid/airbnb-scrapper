import plotly.express as px
from .base import BaseChart
import numpy as np
import pandas as pd

class ScatterChart(BaseChart):
    """Implementación de gráficos de dispersión"""
    def create(self, data, x, y, title, subtitle=None, color=None, size=None, **kwargs):
        # Limpiar datos no numéricos
        df = data.copy()
        if isinstance(x, str) and x in ["guests", "beds", "bedrooms", "baths"]:
            df[x] = pd.to_numeric(df[x], errors='coerce')
            df = df.dropna(subset=[x])

        # Configurar opciones por defecto
        plot_kwargs = {
            'data_frame': df,
            'x': x,
            'y': y,
            'template': self.template,
            'opacity': 0.7,  # Agregar transparencia
        }

        # Agregar color si se especifica
        if color is not None:
            plot_kwargs['color'] = color
            if isinstance(color, str):
                if color == 'rating':
                    plot_kwargs['color_continuous_scale'] = [[0, '#E85C3F'], [0.5, '#FFD700'], [1, '#4CAF50']]
                    plot_kwargs['range_color'] = [4, 5]
                elif color == 'reviews':
                    plot_kwargs['color_continuous_scale'] = [[0, '#E85C3F'], [0.5, '#FFD700'], [1, '#4CAF50']]
                else:
                    plot_kwargs['color_continuous_scale'] = [[0, self.theme.COLORS['primary']], 
                                                           [1, self.theme.COLORS['accent']]]

        # Agregar tamaño si se especifica
        if size is not None:
            plot_kwargs['size'] = size
            plot_kwargs['size_max'] = 20

        # Agregar kwargs adicionales
        plot_kwargs.update(kwargs)

        # Crear figura
        fig = px.scatter(**plot_kwargs)
        
        # Actualizar el layout y marcadores
        fig.update_traces(
            marker=dict(
                line=dict(width=1, color='DarkSlateGrey'),
            ),
            selector=dict(mode='markers')
        )

        # Si la variable x es "rating" o variables enteras, ajustar ejes
        if isinstance(x, str):
            if x == "rating":
                fig.update_xaxes(
                    range=[4.2, 5.1],
                    dtick=0.2,
                    tickformat=".1f"
                )
            elif x in ["guests", "beds", "bedrooms", "baths"]:
                max_val = int(df[x].max())
                min_val = 1 if x == "guests" else 0
                fig.update_xaxes(
                    dtick=1,
                    tick0=min_val,
                    tickmode='linear',
                    range=[min_val - 0.5, max_val + 0.5]
                )

        # Actualizar el layout con título y subtítulo
        title_text = f"{title}<br><span style='font-size: 14px; color: gray'>{subtitle}</span>" if subtitle else title
        fig.update_layout(
            title={
                'text': title_text,
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        # Si es un gráfico de rating, ajustar la barra de color
        if isinstance(color, str) and color == 'rating':
            fig.update_layout(
                coloraxis_colorbar_title="Rating",
                coloraxis_colorbar=dict(
                    title="Rating",
                    tickformat=".1f",
                    dtick=0.2
                )
            )

        return self.update_layout(fig, title_text) 