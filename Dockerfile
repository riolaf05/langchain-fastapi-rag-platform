FROM python:3.10-slim-bullseye
EXPOSE 3000
# Set the working directory
WORKDIR /app

ENV VIRTUAL_ENV=/usr/local

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip=="24.0" && pip install uv=="0.1.29" && uv pip install --no-cache -r requirements.txt

# Copy the project files
COPY main.py ./
COPY api/ ./api/
COPY models/ ./models/
COPY services/ ./services/
COPY config/ ./config/
COPY utils ./utils/
# COPY infrastructure/.env ./infrastructure/
# COPY infrastructure/google_credentials.json ./infrastructure/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]
