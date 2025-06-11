FROM python:3.9-slim

WORKDIR /app

# Copy application files
COPY app.py .
COPY questions/ ./questions/

# Install Flask
RUN pip install flask

# Expose port 8888
EXPOSE 8888

# Run the application
CMD ["python", "app.py"]