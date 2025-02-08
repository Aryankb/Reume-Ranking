# Use the official Python image as base
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy necessary files
COPY requirements.txt .
COPY resume.py .
COPY .env .
COPY extract .
COPY resume .
COPY v2 .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Streamlit port
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "resume.py", "--server.port=8501", "--server.address=0.0.0.0"]
