import chromadb
from sentence_transformers import SentenceTransformer
import requests
from file_parse import load_pdf, split_text

# 初始化向量库与嵌入模型
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="ai_course_kb")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# 替换成你的大模型API密钥与地址
LLM_API_KEY = "填入你自己的大模型API密钥"
LLM_API_URL = "https://xxx.com/v1/chat/completions"

def add_pdf_to_kb(pdf_path):
    """上传PDF，分块存入向量库"""
    text = load_pdf(pdf_path)
    chunks = split_text(text)
    embeds = embed_model.encode(chunks)
    ids = [f"doc_{i}" for i in range(len(chunks))]
    collection.add(
        documents=chunks,
        embeddings=embeds,
        ids=ids
    )

def search_kb(query, top_k=3):
    """检索知识库相关片段"""
    q_embed = embed_model.encode(query)
    res = collection.query(
        query_embeddings=[q_embed],
        n_results=top_k
    )
    return res["documents"][0]

def llm_answer(query, context):
    """大模型结合课件内容生成回答"""
    prompt = f"""
你是人工智能导论课程助教，只能根据下面提供的课件资料回答用户问题，不能编造内容。
课件资料：{context}
用户问题：{query}
如果资料里没有相关内容，直接回复：当前知识库无相关知识点，请上传对应课件后提问。
"""
    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    resp = requests.post(LLM_API_URL, headers=headers, json=data)
    return resp.json()["choices"][0]["message"]["content"]