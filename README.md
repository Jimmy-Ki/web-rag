# Project Overview
This project is a Flask-based web application that facilitates interactive conversations using GPT models, alongside a knowledge base management system. Users can upload, create, delete, and search knowledge entries and interact with the GPT model for chat functionalities.

# Features
Chat Functionality : Engage in conversations using a GPT model.
Knowledge Base Management :
Create and delete knowledge entries.
Upload files in various formats (TXT, MD, PDF).
Search knowledge based on user queries.
User-friendly Interface : Easy navigation through knowledge entries and chat interface.

# Technologies Used
openai==1.13.3
zhipuai==2.0.1
numpy==1.23.5
python-dotenv==1.0.0
torch
torchvision
torchaudio
transformers==4.38.2
tqdm==4.66.1
PyPDF2==3.0.1
markdown==3.6
html2text==2024.2.26
tiktoken==0.5.2
beautifulsoup4==4.12.2
Flask==3.0.3
Flask-Cors==5.0.0

# about
Till now, the application is in the development phase and it is very simple.
such as the user management system is not implemented yet.
but I will implement it in the future.

# Installation

## virual environment setup
I recommended using a virtual environment for Python projects, such as venv or conda. To set up the project, follow these steps:

1. Create a virtual environment (optional but recommended):
```bash
python3 -m venv venv
```
2. Activate the virtual environment:
```bash
source venv/bin/activate  # On Unix/macOS
venv\Scripts\activate  # On Windows
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```
4. Set up the environment variables:
```bash
'''
export ZHIPUAI_API_KEY=<key>
export EMBEDDING_MODEL=<model_name>
export CHAT_API_BASE_URL=<base_url>
export CHAT_MODEL=<your_model>
export CHAT_API_KEY=<your_api_key>
export CHUNK_SIZE=600
export CHUNK_COVER=150
export SYSTEM_PROMPT=<name>
export FLASK_APP=app.py
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5732
'''
```
5. Run the Flask application:
```bash
flask run
```
6. Access the application in your web browser:
```bash
http://127.0.0.1:5732
```


## Docker setup
1. Build the Docker image:
```bash
docker build -t chatbot .
```
2. Run the Docker container:
```bash
docker run -p 5732:5732 chatbot
```
3. Access the application in your web browser:
```bash
http://localhost:5732
```

# Reference
This project is based on the secondary development of [tinyRAG](https://github.com/phbst/tinyRAG), thanks to the contribution of the original author [phbst](https://github.com/phbst).

## update
- Changed the data storage repository from the file system to SQLite.
- Modified the code of the knowledge base management system to better meet actual needs.

# Usage
1. Navigate to the application URL in your web browser.
2. Use the chat interface to interact with the GPT model.
3. Manage your knowledge base by creating, deleting, and searching entries.

# Contributing
Contributions are welcome! Feel free to submit issues, pull requests, or suggest new features.

# License
This project is licensed under the MIT License.


# 中文
# 项目概述
本项目是一个基于Flask的Web应用程序，它使用GPT模型和知识库管理系统来促进交互式对话。用户可以上传、创建、删除和搜索知识条目，并与GPT模型进行聊天交互。

# 功能
聊天功能：使用GPT模型进行对话。
知识库管理系统：
创建和删除知识条目。
上传各种格式的文件（TXT、MD、PDF）。
根据用户查询搜索知识。
用户友好界面：轻松导航知识条目和聊天界面。

# 使用的技术
openai==1.13.3
zhipuai==2.0.1
numpy==1.23.5
python-dotenv==1.0.0
torch
torchvision
torchaudio
transformers==4.38.2
tqdm==4.66.1
PyPDF2==3.0.1
markdown==3.6
html2text==2024.2.26
tiktoken==0.5.2
beautifulsoup4==4.12.2
Flask==3.0.3
Flask-Cors==5.0.0


# 安装

## 虚拟环境设置
我建议使用Python项目（如venv或conda）的虚拟环境。要设置项目，请按照以下步骤操作：
1. 创建虚拟环境（可选但推荐）：
```bash
python3 -m venv venv
```
2. 激活虚拟环境：
```bash
source venv/bin/activate  # 在Unix/macOS上

venv\Scripts\activate  # 在Windows上
```
3. 安装所需的包：
```bash
pip install -r requirements.txt
```
4. 设置环境变量：
```bash
'''
export ZHIPUAI_API_KEY=<key>
export EMBEDDING_MODEL=<model_name>
export CHAT_API_BASE_URL=<base_url>
export CHAT_MODEL=<your_model>
export CHAT_API_KEY=<your_api_key>
export CHUNK_SIZE=600
export CHUNK_COVER=150
export SYSTEM_PROMPT=<name>
export FLASK_APP=app.py
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5732
'''
5. 运行Flask应用程序：
```bash
flask run
```
6. 在Web浏览器中访问应用程序：
```bash
http://127.0.0.1:5732
```

# Docker设置
1. 构建Docker镜像：
```bash
docker build -t chatbot .
```
2. 运行Docker容器：
```bash
docker run -p 5732:5732 chatbot
```
3. 在Web浏览器中访问应用程序：
```bash
http://localhost:5732
```

# 使用方法
1. 在Web浏览器中导航到应用程序URL。
2. 使用聊天界面与GPT模型进行交互。
3. 通过创建、删除和搜索条目来管理您的知识库。

# 项目依据
这个项目是基于 [tinyRAG](https://github.com/phbst/tinyRAG) 的二次开发，感谢原作者 [phbst](https://github.com/phbst) 的贡献。

## 修改内容

- 改用数据存储库SQLite，而不是使用文件系统存储数据。
- 修改了知识库管理系统的部分代码，使其更符合实际需求。

# 贡献
欢迎贡献！请随时提交问题、拉取请求或建议新功能。

# 许可证
本项目根据MIT许可证授权。
