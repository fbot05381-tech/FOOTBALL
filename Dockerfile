# ✅ Base Image
FROM python:3.10-slim

# ✅ Working Directory
WORKDIR /app

# ✅ Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy Bot Files
COPY . .

# ✅ Start Bot (Polling Mode)
CMD ["python", "bot.py"]
