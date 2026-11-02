FROM python:3.12-alpine

RUN apk add --no-cache git \
    # The mounted repos are owned by the host user, so tell git to trust them
    && git config --system --add safe.directory '*'

WORKDIR /app
COPY server.py .
COPY static ./static

EXPOSE 8043
CMD ["python", "-u", "server.py"]
