FROM python:3.13-alpine AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.8.13 /uv /bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY app ./app
COPY main.py ./
COPY bin ./bin

FROM python:3.13-alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app/app ./app
COPY --from=builder /app/main.py ./
COPY --from=builder /app/bin ./bin
RUN chmod +x ./bin/yopass
USER appuser
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8080
CMD ["python", "main.py"]