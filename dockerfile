FROM python:3.12-slim

WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync
COPY app.py .
EXPOSE 8050

CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:8050", "app:server"]