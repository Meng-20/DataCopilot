Couldn't start uvicorn in real env because of the system security mechanism, not allow to use ```pip install``` directely.
1. Virtural env setup

```python3 -m venv .venv```

2. Activate env

```source .venv/bin/activate```

3. Install packages in venv

```pip install fastapi uvicorn pandas python-multipart openpyxl matplotlib numpy scipy```

4. Start uvicorn in virtural env

```python -m uvicorn app:app --reload```

Use the host ip and defined port:

```
python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8888
```

Architecture:

```(.venv)
 ├── python
 ├── pip
 └── uvicorn
 ```
 5. Use SwaggerUI for testing

 ```http://localhost:8000/docs```