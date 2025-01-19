# Gunakan image Python base pake yg slim biar ringan
FROM python:3.11-slim

# Set working directory untuk containernya
WORKDIR /app

# Copy file requirements
COPY requirements.txt .

# Install dependensi yang ada di requirements.txt
RUN pip install -r requirements.txt

# Copy semua file ke container
COPY . .

# Expose port
EXPOSE 8000

# Command untuk menjalankan aplikasi
CMD ["python", "app.py"] 