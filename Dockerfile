# Playwright's official image already has Chromium + all system libs at a known
# path — pinned to the exact playwright version in requirements.txt so the
# bundled browser matches the client library. That's the whole reason to use it:
# installing Chromium's apt deps by hand is the painful part of hosting this app.
FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent_audit.py webapp.py ./

# Public-demo posture: bind all interfaces and turn the SSRF guard ON.
# PORT is supplied by the host (Render/Railway/Fly) at runtime; webapp.py reads it.
ENV HOST=0.0.0.0 \
    PUBLIC_DEMO=1

EXPOSE 8000
CMD ["python", "webapp.py"]
