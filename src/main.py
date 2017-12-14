from flask import Flask
from flask import request
app = Flask(__name__)
import pynlpir

# def init():
#     pynlpir.open()

# def close():
#     pynlpir.close()

@app.route('/')
def index():
    return 'Welcome, here is GKW!'

@app.route('/get_key_words', methods=['POST', 'GET'])
def get_key_words():
    s = ''
    # get doc
    if request.method == 'POST':
        s = request.form.get('s', type=str, default='')
    else:
        s = request.args.get('s')
    # get key words
    if s == '':
        return 'null'
    else:
        pynlpir.open()
        key_word_list = pynlpir.get_key_words(s, max_words=3, weighted=False)
        # temp_str = ''
        for i in range(len(key_word_list)):
            key_word_list[i] = key_word_list[i]
        pynlpir.close()
        return ','.join(key_word_list)

if __name__ == '__main__':
    app.run(debug=True, port=9090)
