# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install virtualenv
RUN pip install virtualenv

# Create a virtual environment
RUN virtualenv venv

# Activate the virtual environment and install dependencies
COPY requirements.txt .
RUN . venv/bin/activate && pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["sh", "-c", ". venv/bin/activate && streamlit run streamlit.py --browser.serverAddress $SERVER_NAME --server.port $PORT"]