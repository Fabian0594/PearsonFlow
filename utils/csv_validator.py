import pandas as pd

class ValidatorCSV:
    """ Clase para validar un archivo CSV """
    
    def __init__(self, dataframe: pd.DataFrame):
        self._dataframe = dataframe.copy()

    def validate_columns(self, required_columns: list) -> bool:
        """ Valida que el DataFrame contenga las columnas requeridas """
        missing_columns = [col for col in required_columns if col not in self._dataframe.columns]
        if missing_columns:
            raise ValueError(f"Faltan las siguientes columnas requeridas: {missing_columns}")
        return True

    def validate_no_nulls(self) -> bool:
        """ Valida que no haya valores nulos en el DataFrame """
        if self._dataframe.isnull().values.any():
            raise ValueError("El DataFrame contiene valores nulos.")
        return True

    def validate_column_types(self, column_types: dict) -> bool:
        """ Valida que las columnas tengan los tipos de datos esperados """
        for column, expected_type in column_types.items():
            if column in self._dataframe.columns:
                if not pd.api.types.is_dtype_equal(self._dataframe[column].dtype, expected_type):
                    raise ValueError(f"La columna '{column}' no es del tipo esperado: {expected_type}")
        return True