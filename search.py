from utils.embedding import Zhipuembedding
from utils.databases import Vectordatabase
import os


text="大数据"
os.environ["ZHIPUAI_API_KEY"]="f7653bba8321069f8eba10b954cba3bb.gO1IPcZ8E2fffRqu"

embedding_model=Zhipuembedding()
db=Vectordatabase()
db.load_vector()
result=db.query(text,embedding_model,1)
print(result)