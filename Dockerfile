FROM python:3.10-slim
WORKDIR /app
COPY . .
# Keep container running so user can attach
CMD ["tail", "-f", "/dev/null"]
