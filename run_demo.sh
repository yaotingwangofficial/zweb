python - <<'PY'
from fastapi import FastAPI
import uvicorn
app = FastAPI()
@app.get("/ping")
def ping(): return {"pong": True}
uvicorn.run(app, host="0.0.0.0", port=8012)
PY