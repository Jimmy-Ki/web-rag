FROM --platform=linux/amd64 python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV ZHIPUAI_API_KEY=f7653bba8321069f8eba10b954cba3bb.gO1IPcZ8E2fffRqu
ENV EMBEDDING_MODEL=embedding-3
ENV CHAT_API_BASE_URL=https://api.deepseek.com/chat/completions
ENV CHAT_MODEL=deepseek-chat
ENV CHAT_API_KEY=sk-054da78fd6a54612afabc9d76e944f31
ENV CHUNK_SIZE=600
ENV CHUNK_COVER=150
ENV SYSTEM_PROMPT="你是伊犁师范大学的人工智能助手小伊，请用中文回答问题，在用户提交的数据中，有问题和部分参考文献，请根据参考文献回答问题，如果参考文献中没有相关信息，请用回答这个问题小伊还不知道呢。"
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5732

EXPOSE 5732

CMD ["flask", "run"]