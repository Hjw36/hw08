from flask import Flask, render_template, request, redirect, url_for
import os, asyncio
from speech_core import audio_to_text, text_to_audio
from rag_core import add_pdf_to_kb, search_kb, llm_answer

app = Flask(__name__)
os.makedirs("static/audio", exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", answer="", audio_path=None)

# 上传PDF课件
@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["pdf_file"]
    save_p = "temp.pdf"
    f.save(save_p)
    add_pdf_to_kb(save_p)
    os.remove(save_p)
    return render_template("index.html", answer="课件上传完成，已存入知识库", audio_path=None)

# 接收录音，转文字
@app.route("/voice_rec", methods=["POST"])
def voice_rec():
    audio_file = request.files["audio"]
    audio_path = "temp.wav"
    audio_file.save(audio_path)
    text = audio_to_text(audio_path)
    os.remove(audio_path)
    return text

# 语音提问跳转问答
@app.route("/ask", methods=["GET"])
def ask_voice():
    q = request.args.get("query")
    context = search_kb(q)
    ans = llm_answer(q, context)
    # 生成朗读音频
    audio_save = "static/audio/reply.wav"
    asyncio.run(text_to_audio(ans, audio_save))
    return render_template("index.html", answer=ans, audio_path=audio_save)

# 文字提问接口
@app.route("/ask_text", methods=["POST"])
def ask_text():
    q = request.form["question"]
    context = search_kb(q)
    ans = llm_answer(q, context)
    audio_save = "static/audio/reply.wav"
    asyncio.run(text_to_audio(ans, audio_save))
    return render_template("index.html", answer=ans, audio_path=audio_save)

if __name__ == "__main__":
    app.run(debug=True)