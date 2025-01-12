class StayBATheme:
    """Maneja los estilos y colores de StayBA"""
    COLORS = {
        'primary': '#E85C3F',
        'secondary': '#2c3e50',
        'background': '#FFFFFF',
        'light_gray': '#f8f9fa',
        'text': '#2c3e50',
        'accent': '#FF8B6A'
    }

    @staticmethod
    def get_default_layout():
        return {
            'title': {
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            'hovermode': 'closest',
            'showlegend': False,
            'margin': dict(l=50, r=20, t=70, b=50)
        } 