# Comece por aqui

1. Abra esta pasta no VS Code. Confira se `app.py` e `pyproject.toml` aparecem no Explorer.
2. Vá a **Terminal → Novo Terminal**.
3. Execute, uma linha por vez:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
streamlit run app.py
```

Se o PowerShell bloquear `Activate.ps1`, abra um terminal `cmd` e execute `.venv\Scripts\activate.bat`; depois rode os comandos de instalação e inicialização.

4. O navegador deve abrir o app em `http://localhost:8501`.
5. Para testar a demonstração, carregue `data/samples/products_with_issues.csv`. Ela contém 8 ocorrências intencionais; a cópia tratada registra 2 ajustes seguros e mantém 7 ocorrências para revisão humana.
6. Para validar o projeto, pare o app com `Ctrl+C` no terminal e execute `python -m pytest -v`.

**Importante:** o aplicativo não exige chave de API nem envia dados a serviços externos. As orientações são locais, e o projeto nunca sobrescreve o arquivo enviado.
