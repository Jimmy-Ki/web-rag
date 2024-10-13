from flask import Flask, render_template, request, jsonify, Response, url_for, redirect
from flask_cors import CORS
from utils.data_process import ReadSingleFile, Vectordatabase, Zhipuembedding
from utils.GPTstreamer import GPTStreamer as Streamer
import os
from dotenv import load_dotenv
import uuid
import sqlite3

database = sqlite3.connect("test.db", check_same_thread=False)
load_dotenv()


class stdResponse:
    def __init__(self, status, message=None, data=None, error=None, code=None):
        self.status = status
        self.message = message
        self.data = data
        self.error = error
        self.code = code

    def to_dict(self):
        return {
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "code": self.code,
        }


app = Flask(__name__)
CORS(app)


@app.route("/<id>")
def index(id):
    return render_template("chat.html")

@app.route("/")
def ind():
    # 重定向至/knowledge
    return redirect('/knowledge')



@app.route("/api")
def hello():
    return {"Hello": "World"}


# 404页面处理
@app.errorhandler(404)
def not_found(error):
    return stdResponse(404, "Not found", None, "Resource not found", 404).to_dict()


# 400页面处理
@app.errorhandler(400)
def bad_request(error):
    return stdResponse(400, "Bad request", None, "Bad request", 400).to_dict()


# 对话接口
@app.route("/api/chat/completion", methods=["POST"])
def chat_completion():
    model = Streamer(
        gpt_api_key=os.getenv("CHAT_API_KEY"),
        gpt_api_url=os.getenv("CHAT_API_BASE_URL"),
        model=os.getenv("CHAT_MODEL"),
        stream=False,
        system_prompt=os.getenv("CHAT_SYSTEM_PROMPT"),
        temperature=0.9,
    )

    data = request.json
    if "messages" not in data:
        return stdResponse(
            400, "Bad request", None, "Missing 'messages' field in request", 400
        ).to_dict()
    elif len(data["messages"]) == 0:
        return stdResponse(
            400, "Bad request", None, "Empty 'messages' field in request", 400
        ).to_dict()
    elif type(data["messages"]) != list:
        return stdResponse(
            400, "Bad request", None, "Invalid 'messages' field in request", 400
        ).to_dict()
    message = data["messages"]
    stream = data.get("stream", False)  # 默认不使用流式输出

    if stream:
        model.stream = True

        def generate():
            response_generator = model.generate_response(message)
            for chunk in response_generator:
                yield chunk

        return Response(generate(), mimetype="text/event-stream")
    else:
        try:
            response = model.get_response(message)
            return jsonify({"response": response})
        except Exception as e:
            return stdResponse(
                500, "Bad request", None, "Missing 'messages' field in request", 5002
            ).to_dict()

# 知识库展示接口
@app.route("/api/knowledge/show/<dir>", methods=["GET"])
def knowledge_show(dir):
    # 查询chunks表，返回chunks
    cursor = database.cursor()
    cursor.execute(
        "SELECT * FROM `chunks` WHERE `father_uuid`=? AND `status` = 0", (dir,)
    )
    chunks = cursor.fetchall()
    chunks = [
        {"id": chunk[0], "content": chunk[1], "update_time": chunk[4]}
        for chunk in chunks
    ]
    return stdResponse(
        200, "Knowledge base list", chunks, "Knowledge base list", 200
    ).to_dict()

# 知识库展示页面
@app.route("/knowledge/detail/<dir>", methods=["GET"])
def knowledge_detail(dir):
    return render_template("detail.html")

# 知识库目录展示接口
@app.route("/api/knowledge/list", methods=["GET"])
def knowledge_list():
    # 查询dirs表，返回dirs
    cursor = database.cursor()
    cursor.execute("SELECT * FROM `dirs` WHERE `status` = 0")

    dirs = cursor.fetchall()
    dirs = [{"id": dir[0], "name": dir[1], "update_time": dir[3], "nums": cursor.execute("SELECT COUNT(*) FROM `chunks` WHERE `father_uuid` = ?", (dir[0],)).fetchone()[0]} for dir in dirs]

    return stdResponse(
        200, "Knowledge base list", dirs, "Knowledge base list", 200
    ).to_dict()

# 知识库展示页面
@app.route("/knowledge", methods=["GET"])
def knowledge():
    return render_template("knowledge.html")

# 知识库删除接口
@app.route("/api/knowledge/delete/<dir>", methods=["GET"])
def knowledge_delete(dir):
    # 增加删除锁，status = -1
    cursor = database.cursor()
    try:
        cursor.execute("UPDATE `dirs` SET `status` = -1 WHERE `uuid` =?", (dir,))
        database.commit()
        return stdResponse(
            200,
            "Knowledge base deleted successfully",
            None,
            "Knowledge base deleted successfully",
            200,
        ).to_dict()
    except Exception as e:
        return stdResponse(500, "Internal Server Error", None, str(e), 500).to_dict()


# 知识库创建接口
@app.route("/api/knowledge/create/<dirname>", methods=["GET"])
def knowledge_create(dirname):
    # 增加创建锁，status = 0
    cursor = database.cursor()
    try:
        u = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO `dirs` (`uuid`, `name`, `status`, `owner`, `groupowner`) VALUES (?,?,?,?,?)",
            (
                u,
                dirname,
                0,
                "user1",
                "group",
            ),
        )
        database.commit()
        # 返回刚插入的数据
        cursor.execute("SELECT * FROM `dirs` WHERE `uuid` =?", (u,))
        dir = cursor.fetchone()
        dir = {"id": dir[0], "name": dir[1], "update_time": dir[3]}
        database.commit()
        return stdResponse(
            200,
            "Knowledge base created successfully",
            dir,
            "Knowledge base created successfully",
            200,
        ).to_dict()
    except Exception as e:
        return stdResponse(500, "Internal Server Error", None, str(e), 500).to_dict()


# upload接口
@app.route("/api/knowledge/upload/<dir>", methods=["POST"])
def knowledge_upload(dir):
    directory = dir
    # 接收参数filename，表示上传的文件名；
    # 存储到./data/<dir>目录下
    if request.method == "POST":
        # 检查文件是否为文本类型
        if "file" not in request.files:
            return stdResponse(400, "Bad request", None, "No file part", 400).to_dict()
        file = request.files["file"]
        if file.filename == "":
            return stdResponse(
                400, "Bad request", None, "No selected file", 400
            ).to_dict()
        if file:
            # 检查文件类型，txt，md，pdf
            if (
                not file.filename.endswith(".txt")
                and not file.filename.endswith(".md")
                and not file.filename.endswith(".pdf")
            ):
                return stdResponse(
                    400, "Bad request", None, "Invalid file type", 400
                ).to_dict()
            # 保存临时文件，没有文件夹就创建随机文件夹
            if not os.path.exists("./data/{dir}".format(dir=directory)):
                os.makedirs("./data/{dir}".format(dir=directory))
            file.save("./data/{dir}/{file}".format(dir=directory, file=file.filename))
            # 读取文件内容，返回json格式，包含id，content，update_time
            filter = ReadSingleFile(
                "./data/{dir}/{file}".format(dir=directory, file=file.filename)
            )
            docs = filter.get_all_chunk_content(600, 150)
            embedding_model = Zhipuembedding()
            database = Vectordatabase(docs)
            database.get_vector(embedding_model)
            database.persist(dir)
            return stdResponse(
                200,
                "File uploaded successfully",
                None,
                "File uploaded successfully",
                200,
            ).to_dict()
    else:
        return stdResponse(
            400, "Bad request", None, "Invalid request method", 400
        ).to_dict()

# 知识库修改接口
@app.route("/api/knowledge/update/<id>", methods=["POST"])
def knowledge_update(id):
    content = request.json["content"]
    print(content)
    v = Vectordatabase([content])
    v.update_content(uuid=id, content=content)
    return stdResponse(
        200,
        "Knowledge updated successfully",
        None,
        "Knowledge updated successfully",
        200,
    ).to_dict()
    pass
    

# 知识库查询接口
@app.route("/api/knowledge/search/<dir>", methods=["GET", "POST"])
def knowledge_search(dir):
    """
    知识搜索函数

    该函数使用嵌入模型和向量数据库来执行知识搜索。它接受一个文本查询和要返回的结果数量，
    然后返回最相关的知识片段。

    参数:
    request (Request): HTTP 请求对象，包含查询参数 'text' 和 'num'。

    返回:
    dict: 包含搜索结果的 JSON 响应，包括状态码、状态信息、结果数据和消息。

    异常:
    Exception: 如果在搜索过程中发生异常，将捕获异常并返回一个包含错误信息的 JSON 响应。
    """
    # 初始化嵌入模型
    embedding_model = Zhipuembedding()
    # 初始化向量数据库
    db = Vectordatabase()
    # 加载向量数据
    db.load_vector("./database/{dir}".format(dir=dir))

    # 判断请求方法是否为 POST
    if request.method == "POST":
        # 从 POST 请求中获取查询文本和数量
        text = request.json.get("text")
        num = request.json.get("num")
    else:
        # 从 GET 请求中获取查询文本和数量
        text = request.args.get("text")
        num = request.args.get("num")

    # 如果文本或数量为空，返回错误响应
    if text is None or num is None:
        return stdResponse(
            400, "Knowledge search failed", None, "Missing required parameters", 400
        ).to_dict()

    try:
        # 执行查询
        database = Vectordatabase()

        path = dir
        database.load_vector(path)

        result = database.query(text, embedding_model, int(num))
        # 返回查询结果
        return stdResponse(200, "Knowledge search success", result, None, 200).to_dict()
    except Exception as e:
        # 返回异常响应
        return stdResponse(
            500, "Knowledge search filed", None, "Internal server error:" + str(e), 5001
        ).to_dict()


# 知识库删除接口
@app.route("/api/knowledge/delete/detail/<id>", methods=["GET"])
def knowledge_delete_detail(id):
    # 增加删除锁，status = -1
    v = Vectordatabase()
    v.delete_content(uuid=id)
    return stdResponse(
        200,
        "Knowledge base deleted successfully",
        None,
        "Knowledge base deleted successfully",
        200,
    ).to_dict()


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST")
    port = os.getenv("FLASK_RUN_PORT")

    app.run(debug=True, host=host, port=port)
