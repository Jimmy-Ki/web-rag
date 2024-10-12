from langchain.prompts import PromptTemplate
from utils.embedding import Zhipuembedding
from utils.databases import Vectordatabase
import os
from utils.GPTstreamer import GPTStreamer
import time


class Openai_model:
    def __init__(self, model_name: str, temperature: float, api_url: str, system_prompt: str, stream: bool) -> None:
        # 初始化大模型
        self.model_name = model_name
        self.temperature = temperature
        self.stream = stream
        self.model = GPTStreamer(
            gpt_api_key=os.getenv("CHAT_API_KEY"),
            gpt_api_url=api_url,
            model=self.model_name,
            stream=self.stream,
            system_prompt=system_prompt,
            temperature=self.temperature
        )

        # 加载向量数据库，embedding模型
        self.db = Vectordatabase()
        self.db.load_vector()
        self.embedding_model = Zhipuembedding()

    # 定义chat方法
    def chat(self, question: str):
        # 这里利用输入的问题与向量数据库里的相似度来匹配最相关的信息，填充到输入的提示词中
        template = """
        现在的系统信息：{t} 问题: {question}
        可参考的上下文：
        ···
        {info}
        ···
        请适当根据以上信息回答问题，如果以上信息对问题没有用，请直接回答问题，忽略参考即可。
        """

        info = self.db.query(question, self.embedding_model, 8)

        prompt = PromptTemplate(template=template, input_variables=["question", "info"]).format(
            question=question,
            info=info,
            t="现在是{yy}年{mm}月{dd}日,星期{ww}".format(
                yy=time.strftime("%Y", time.localtime()),
                mm=time.strftime("%m", time.localtime()),
                dd=time.strftime("%d", time.localtime()),
                ww=time.strftime("%w", time.localtime())
            )
        )
        print(prompt)

        return self.model.generate_response(prompt)

    def clear_history(self):
        self.model.clear_history()

# 示例用法
if __name__ == '__main__':
    gpt_api_key = "sk-054da78fd6a54612afabc9d76e944f31"
    gpt_api_url = "https://api.deepseek.com/chat/completions"
    system_prompt = "你是伊犁师范大学的人工智能助手小伊，请用中文回答问题，在用户提交的数据中，有问题和部分参考文献，请根据参考文献回答问题，如果参考文献中没有相关信息，请用回答这个问题小伊还不知道呢。"
    prompt = "中华人民共和国消费者权益保护法什么时候,在哪个会议上通过的？"

    model = Openai_model(model_name='deepseek-chat', temperature=0.9, api_url=gpt_api_url, system_prompt=system_prompt)
    res = model.chat(prompt)
    for chunk in res:
        print(chunk, end='', flush=True)