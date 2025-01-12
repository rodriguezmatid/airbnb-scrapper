import pytest
import pandas as pd
from src.data.processor import DataProcessor

def test_calculate_reviews_per_year():
    # Datos de prueba
    test_data = pd.DataFrame({
        'reviews': [10, 20, 30],
        'years_hosting': [2, 4, 0]
    })
    
    # Procesar datos
    processed_df = DataProcessor.calculate_reviews_per_year(test_data)
    
    # Verificar resultados
    expected_reviews_per_year = [5, 5, 30]
    assert all(processed_df['reviews_per_year'] == expected_reviews_per_year) 