# DevOps Monitoring Dashboard — MVP

## Backend

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

## Frontend

```bash
streamlit run dashboard/app.py
```

## Tests

```bash
pytest tests/ -v
```

API key par défaut : dev-secret-key
