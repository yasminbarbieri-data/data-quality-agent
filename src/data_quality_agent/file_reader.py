
from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}


def load_file(file_path: str | Path) -> pd.DataFrame:
    """
    Carrega um arquivo CSV ou Excel e retorna seus dados.

    O arquivo original não é modificado.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    if not path.is_file():
        raise ValueError(f"O caminho não aponta para um arquivo: {path}")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Formato não suportado: {path.suffix}. "
            "Utilize CSV ou XLSX."
        )

    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)

    return pd.read_excel(path, engine="openpyxl")
