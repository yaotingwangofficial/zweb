import requests, sys
base = "http://127.0.0.1:8012"
for path in ["/api/health", "/docs"]:
    url = base + path
    try:
        r = requests.get(url, timeout=3)
        print(path, r.status_code, r.text[:80])
    except Exception as e:
        print(path, "ERROR:", e)
        sys.exit(1)
print("OK")