# ChatGPT Automation Utils API

## Quick Start

### Manually

Install dependencies:

```bash
pip install -r requirements.txt
```

Run service:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 1
```

### Using Docker

Build image:

```bash
docker-compose build
```

Run service:

```bash
docker-compose up -d
```

Test service:

```bash
curl -X GET "http://localhost:8080"

# Should receive
# {"message":"ChatGPT Automation API"}
```
