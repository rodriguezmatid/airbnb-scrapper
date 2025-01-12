import plotly.express as px
from .base import BaseChart
import pandas as pd

class DistributionChart(BaseChart):
    """Implementación de gráficos de distribución (BoxPlot, Violin)"""
    def create_boxplot(self, data, x, y, title, subtitle=None, color=None, **kwargs):
        # Crear bins de precio para agrupar
        df = data.copy()
        
        # Calcular los rangos de precio
        price_bins = pd.qcut(df['price_original'], q=5)
        # Crear etiquetas con los rangos de precio reales
        df['price_range'] = price_bins.apply(lambda x: f"${x.left:.0f} - ${x.right:.0f}")
        
        # Ordenar las categorías por precio
        category_order = sorted(df['price_range'].unique(), 
                              key=lambda x: float(x.split(' - ')[0].replace('$', '')))
        
        # Configurar opciones
        plot_kwargs = {
            'data_frame': df,
            'x': 'price_range',
            'y': y,
            'template': self.template,
            'color': 'price_range',
            'category_orders': {'price_range': category_order},
            'color_discrete_sequence': [
                '#E85C3F',  # Rango más bajo
                '#FF8B6A',  # Rango bajo
                '#FFB347',  # Rango medio
                '#98D8AA',  # Rango alto
                '#4CAF50'   # Rango más alto
            ]
        }
        
        # Agregar kwargs adicionales
        plot_kwargs.update(kwargs)
        
        # Crear figura
        fig = px.box(**plot_kwargs)
        
        # Actualizar el layout
        title_text = f"{title}<br><span style='font-size: 14px; color: gray'>{subtitle}</span>" if subtitle else title
        fig.update_layout(
            title={
                'text': title_text,
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            showlegend=False,
            xaxis_title="Rango de Precio por Noche",
            xaxis_tickangle=45  # Rotar las etiquetas para mejor lectura
        )
        
        return self.update_layout(fig, title_text) 

    def create_histogram(self, data, x, title, subtitle=None, **kwargs):
        """Crea un histograma con curva de densidad"""
        df = data.copy()
        
        plot_kwargs = {
            'data_frame': df,
            'x': x,
            'template': self.template,
            'color_discrete_sequence': ['#E85C3F'],
            'marginal': 'violin',  # Agregar curva de densidad
            'nbins': 30,  # Número de barras
            'opacity': 0.7,
            'histnorm': 'probability',  # Usar probabilidad en lugar de porcentaje
        }
        
        # Agregar kwargs adicionales
        plot_kwargs.update(kwargs)
        
        # Crear figura
        fig = px.histogram(**plot_kwargs)
        
        # Actualizar el layout
        title_text = f"{title}<br><span style='font-size: 14px; color: gray'>{subtitle}</span>" if subtitle else title
        fig.update_layout(
            title={
                'text': title_text,
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            showlegend=False,
            bargap=0.1,  # Espacio entre barras
            yaxis_title="Porcentaje de propiedades",
        )
        
        return self.update_layout(fig, title_text) 