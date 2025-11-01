# Use Python 3.9 slim image
FROM python:3.9-slim

#Set working directory inside container
WORKDIR /app

#Copy files from host to container
COPY . /app

# Install dependencies
RUN pip install pandas matplotlib seaborn

# Default command to run your script
CMD ["python", "data_analysis.py"]
