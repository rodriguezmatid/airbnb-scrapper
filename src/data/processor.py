import pandas as pd

class DataProcessor:
    """Procesa y transforma los datos"""
    @staticmethod
    def calculate_reviews_per_year(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["reviews_per_year"] = df["reviews"] / df["years_hosting"].replace(0, 1)
        return df

    @staticmethod
    def filter_data(df: pd.DataFrame, **filters) -> pd.DataFrame:
        filtered_df = df.copy()
        for column, value in filters.items():
            if value is not None:
                filtered_df = filtered_df[filtered_df[column] == value]
        return filtered_df 