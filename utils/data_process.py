import PyPDF2
from tqdm import tqdm
import json
import tiktoken
import numpy as np
import uuid
import sqlite3
from zhipuai import ZhipuAI
import os
from typing import List    
from dotenv import load_dotenv
load_dotenv()
DATABASE_PATH = 'test.db'
# 用于数据切分时，判断字块的token长度，速度比较快
enc = tiktoken.get_encoding("cl100k_base")

class ReadSingleFile:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = self.read_file_content(file_path)

    def read_file_content(self, file_path: str):
        if file_path.endswith('.pdf'):
            return self.read_pdf_content(file_path)
        elif file_path.endswith('.md'):
            return self.read_md_content(file_path)
        elif file_path.endswith('.txt'):
            return self.read_txt_content(file_path)

    def get_all_chunk_content(self,max_len:int=600,cover_len:int=150):
        return self.chunk_content(self.content,max_len,cover_len)

    def chunk_content(self,content:str,max_len:int=600,cover_len:int=150):
        chunk_text = []
        curr_chunk = ''
        curr_len = 0
        for line in content.split('\n'):
            line_len = len(line)
            if curr_len + line_len + cover_len <= max_len:
                curr_chunk += line + '\n'
                curr_len += line_len + 1
            else:
                chunk_text.append(curr_chunk)
                curr_chunk = line + '\n'
                curr_len = line_len + 1
        chunk_text.append(curr_chunk)
        return chunk_text
    
    def read_pdf_content(self, file_path: str):
        text=""
        with open(file_path, 'rb') as f:
            reader=PyPDF2.PdfReader(f)
            for num_page in range(len(reader.pages)):
                text+=reader.pages[num_page].extract_text()
        return text
    def read_md_content(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    def read_txt_content(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
        
# 第一步，传入文本路径，获取文本内容，返回一个字块列表

class Zhipuembedding:
    def __init__(self):
        client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY")) 
        self.embedding_model=client

    def get_embedding(self,content:str=''):
        response =self.embedding_model.embeddings.create(
            model=os.getenv("EMBEDDING_MODEL"), #填写需要调用的模型名称
            input=content #填写需要计算的文本内容,
        )
        return response.data[0].embedding

    def compare_v(cls, vector1: List[float], vector2: List[float]) -> float:
        dot_product = np.dot(vector1, vector2)
        magnitude = np.linalg.norm(vector1) * np.linalg.norm(vector2)
        if not magnitude:
            return 0
        return dot_product / magnitude

# 第二步，传入字块列表，获取向量列表，返回一个向量列表

class Vectordatabase:
    #初始化方法，传入一个字块列表
    def __init__(self,docs:List=[]) -> None:
        self.docs = docs
    
    #对字块列表进行，批量的embedded编码，传入embedding模型，返回一个向量列表
    def get_vector(self,EmbeddingModel)->List[List[float]]:
        self.vectors = []
        for doc in tqdm(self.docs):
            self.vectors.append(EmbeddingModel.get_embedding(doc))
        return self.vectors
    
    #把向量列表存储到数据库中，sqlite3数据库DATABASE_PATH,返回字块列表、向量列表
    def persist(self,path:str='database')->None:
        db = sqlite3.connect(DATABASE_PATH)
        cursor = db.cursor()
        for i in range(len(self.vectors)):
            cursor.execute('INSERT INTO chunks (uuid, data, vector, status, father_uuid) VALUES (?,?,?,?,?)', (str(uuid.uuid4()), self.docs[i],json.dumps(self.vectors[i]),0,path))
        db.commit()
        db.close()
        return self.vectors,self.docs

    def update_content(self,uuid:str,content:str):
        updated_vector = self.get_embedding(content)
        db = sqlite3.connect(DATABASE_PATH)
        cursor = db.cursor()
        cursor.execute('UPDATE chunks SET data=?,vector=? WHERE uuid=?', (content,str(updated_vector), uuid))
        db.commit()
        db.close()
        # 更新向量
        return True

    def get_embedding(self,content:str=''):
        client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))
        embedding_model=client.embeddings.create(
            model=os.getenv("EMBEDDING_MODEL"), #填写需要调用的模型名称
            input=content #填写需要计算的文本内容,
        )
        return embedding_model.data[0].embedding
    
    def delete_content(self,uuid:str):
        db = sqlite3.connect(DATABASE_PATH)
        cursor = db.cursor()
        cursor.execute('UPDATE chunks SET status=-1 WHERE uuid=?', (uuid,))
        db.commit()
        db.close()
        return True

    #加载json文件中的向量和字块，得到向量列表、字块列表,默认路径为'database'
    def load_vector(self,path:str='database')->None:
        db = sqlite3.connect(DATABASE_PATH)
        cursor = db.cursor()
        cursor.execute('SELECT vector, data FROM chunks WHERE father_uuid=?', (path,))
        result = cursor.fetchall()
        self.document = [row[1] for row in result]
        self.vectors = [json.loads(row[0]) for row in result]
        
        db.close()
        return self.vectors,self.document
    
    #求向量的余弦相似度，传入两个向量和一个embedding模型，返回一个相似度
    def get_similarity(self, vector1: List[float], vector2: List[float],embedding_model) -> float:
        return embedding_model.compare_v(vector1, vector2)
    
    #求一个字符串和向量列表里的所有向量的相似度，表进行排序，返回相似度前k个的子块列表
    def query(self, query: str, EmbeddingModel, k: int = 1) -> List[str]:
        query_vector = EmbeddingModel.get_embedding(query)
        result = np.array([self.get_similarity(query_vector, vector,EmbeddingModel)
                          for vector in self.vectors])
        return np.array(self.document)[result.argsort()[-k:][::-1]].tolist()

# 第三步，传入向量列表，文本内容，存储到数据库

# 测试
if __name__ == '__main__':
    filter=ReadSingleFile('./data/4b2ae956-a20f-43ef-9f82-9e5dec13b4b5/256ca64b-f0ed-419d-894c-2c6c060d8442.md')
    docs=filter.get_all_chunk_content(600,150)
    embedding_model=Zhipuembedding()
    database=Vectordatabase(docs)
    database.get_vector(embedding_model)
    database.persist('know')
    path='know'
    database.load_vector(path)
    print(database.query('大数据',embedding_model))