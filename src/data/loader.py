import pandas as pd
from pathlib import Path

class DataLoader:
    """Maneja la carga de datos"""
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data")

    def load_csv(self, filename: str) -> pd.DataFrame:
        try:
            filepath = self.data_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"No se encuentra el archivo: {filepath}")
            
            df = pd.read_csv(filepath)
            print(f"Datos cargados exitosamente de {filepath}")
            print(f"Dimensiones del DataFrame: {df.shape}")
            return df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            print("Asegúrate de que el archivo exista en la carpeta 'data/'")
            print("Estructura esperada:")
            print("  airbnb_scrapper/")
            print("  └── data/")
            print("      └── airbnb_data.csv")
            return pd.DataFrame() 