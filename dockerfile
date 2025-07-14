FROM python:3.12-slim

WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync
COPY app.py .
COPY app.py check_connection.py ./
EXPOSE 8050

CMD ["sh", "-c", "uv run check_connection.py && uv run gunicorn -b 0.0.0.0:8050 app:server"]
# CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:8050", "app:server"]