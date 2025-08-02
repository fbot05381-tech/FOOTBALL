# Base image
FROM python:3.10-slim

# Disable Rust dependency build
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# Work directory
WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Run bot
CMD ["python", "bot.py"]
