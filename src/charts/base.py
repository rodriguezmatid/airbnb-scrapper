from .theme import StayBATheme

class BaseChart:
    """Clase base para todos los gráficos"""
    def __init__(self, template="plotly_white"):
        self.template = template
        self.theme = StayBATheme()

    def update_layout(self, fig, title):
        layout = self.theme.get_default_layout()
        layout['title'] = {'text': title, **layout['title']}
        fig.update_layout(**layout)
        return fig 