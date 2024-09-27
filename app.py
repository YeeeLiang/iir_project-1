from flask import Flask, request, jsonify, render_template
import os
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # 確保這個文件夾存在

# 確保上傳文件夾存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 用於解析 XML 的函數
def analyze_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # 提取標題
        title = root.find('.//ArticleTitle').text if root.find('.//ArticleTitle') is not None else "無標題"

        # 提取全文
        text = ''.join([elem.text for elem in root.iter() if elem.text])
        num_chars = len(text)
        num_words = len(text.split())
        num_sentences = text.count('.') + text.count('!') + text.count('?')

        return num_chars, num_words, num_sentences, text, title
    except Exception as e:
        return 0, 0, 0, "", "解析錯誤：" + str(e)

@app.route('/')
def index():
    return render_template('index.html', title='XML 文件上傳')

@app.route('/upload', methods=['POST'])
def upload_files():
    print("接收到文件上傳請求")
    files = request.files.getlist('files')
    results = []

    for file in files:
        print(f"處理文件: {file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        num_chars, num_words, num_sentences, text, title = analyze_xml(file_path)
        results.append({
            'filename': file.filename,
            'num_chars': num_chars,
            'num_words': num_words,
            'num_sentences': num_sentences,
            'text': text,
            'title': title  # 加入標題
        })

    print("文件處理完成")
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
