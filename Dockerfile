FROM --platform=linux/amd64 python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV ZHIPUAI_API_KEY=<key>
ENV EMBEDDING_MODEL=<model_name>
ENV CHAT_API_BASE_URL=<base_url>
ENV CHAT_MODEL=<your_model>
ENV CHAT_API_KEY=<your_api_key>
ENV CHUNK_SIZE=600
ENV CHUNK_COVER=150
ENV SYSTEM_PROMPT=<name>
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5732

EXPOSE 5732

CMD ["flask", "run"]