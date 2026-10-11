
from pathlib import Path
from typing import BinaryIO

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


def load_uploaded_file(
    file_content: BinaryIO,
    file_name: str,
) -> pd.DataFrame:
    """Carrega um CSV ou XLSX enviado por uma interface web.

    A função recebe o conteúdo aberto do arquivo e seu nome separadamente para
    continuar independente de qualquer framework de interface.
    """
    suffix = Path(file_name).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Formato não suportado: {suffix or 'sem extensão'}. "
            "Utilize CSV ou XLSX."
        )

    file_content.seek(0)

    if suffix == ".xlsx":
        return pd.read_excel(file_content, engine="openpyxl")

    try:
        return pd.read_csv(file_content)
    except UnicodeDecodeError:
        # Arquivos exportados por ferramentas administrativas podem usar
        # Latin-1 em vez de UTF-8. O cursor volta ao início antes da tentativa.
        file_content.seek(0)
        return pd.read_csv(file_content, encoding="latin-1")
