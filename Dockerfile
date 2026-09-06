FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json ./package.json
RUN npm install
COPY frontend/ ./
ENV VITE_API_BASE_URL=.
RUN npm run build

FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FACTORYVISION_MODEL_CHECKPOINT=/app/artifacts/model.ckpt \
    FACTORYVISION_DB_PATH=/app/runtime/factoryvision.db \
    FACTORYVISION_FRONTEND_DIST=/app/frontend/dist

COPY requirements.txt requirements-inference.txt ./
RUN pip install --no-cache-dir torch==2.10.0 torchvision==0.25.0 --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements-inference.txt

COPY backend/ ./backend/
COPY scripts/ ./scripts/
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

RUN mkdir -p /app/artifacts /app/runtime

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
