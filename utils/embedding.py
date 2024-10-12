import numpy as np
from zhipuai import ZhipuAI
import os
from typing import List


class Zhipuembedding:

    def __init__(self, path:str=''):
        	

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
    
    def compare(self, text1: str, text2: str):
        embed1=self.embedding_model.embeddings.create(
            model=os.getenv("EMBEDDING_MODEL"), #填写需要调用的模型名称
            input=text1 #填写需要计算的文本内容,
        ).data[0].embedding

        embed2=self.embedding_model.embeddings.create(
            model=os.getenv("EMBEDDING_MODEL"), #填写需要调用的模型名称
            input=text2 #填写需要计算的文本内容,
        ).data[0].embedding

        return np.dot(embed1, embed2) / (np.linalg.norm(embed1) * np.linalg.norm(embed2))
    
