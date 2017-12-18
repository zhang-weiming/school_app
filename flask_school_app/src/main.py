from flask import Flask
from flask import request
import pynlpir
import threading
import sys
sys.path.append('/home/zwm/Workplace/SchoolApp/src')
import db_helper

MAX_WORDS_DEFAULT = 3
MAX_HOT_WORDS_DEFAULT = 20
UPDATE_HOT_WORD_DEFAULT = 'True'
app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome, here is GKW!'

@app.route('/get_key_words', methods=['POST', 'GET'])
def get_key_words():
    s = ''
    max_words = MAX_WORDS_DEFAULT
    max_hot_words = MAX_HOT_WORDS_DEFAULT
    update_hot_word = UPDATE_HOT_WORD_DEFAULT
    # get doc
    if request.method == 'POST':
        s = request.form.get('s', type=str, default='')
        update_hot_word = request.form.get('update_hot_word', type=str, default=UPDATE_HOT_WORD_DEFAULT) # 是否更新hot_word表
        try:
            max_words = request.form.get('max_words', type=str, default=MAX_WORDS_DEFAULT)
            if max_words != '': # 有max_words参数（可能是默认值'3'）
                print('[POST] max_words yes')
                max_words = int(max_words.strip())
                print('\tmax_words =', max_words)
            else:
                max_words = MAX_WORDS_DEFAULT
                print('[POST] max_words no')
        except: # max_words参数处理异常，设置默认值3
            max_words = MAX_WORDS_DEFAULT
        try:
            max_hot_words = request.form.get('max_hot_words', type=str, default=MAX_HOT_WORDS_DEFAULT)
            if max_hot_words != '':
                max_hot_words = int(max_hot_words.strip())
            else:
                max_hot_words = MAX_HOT_WORDS_DEFAULT
        except:
            max_hot_words = MAX_HOT_WORDS_DEFAULT
    elif request.method == 'GET':
        s = request.args.get('s')
        update_hot_word = request.args.get('update_hot_word')
        if update_hot_word != 'False':
            update_hot_word = 'True'
        try:
            max_words = int(request.args.get('max_words').strip())
        except:
            max_words = MAX_WORDS_DEFAULT
        try:
            max_hot_words = int(request.args.get('max_hot_words').strip())
        except:
            max_hot_words = MAX_HOT_WORDS_DEFAULT
    # get key words
    if s == '': # 文章内容为空，不分析
        return 'null'
    else: # 分析关键词
        pynlpir.open()
        key_word_list = pynlpir.get_key_words(s, max_words=max_words, weighted=False)
        # temp_str = ''
        for i in range(len(key_word_list)):
            key_word_list[i] = key_word_list[i]
        pynlpir.close()
        if update_hot_word == 'True':
            # 新开一个线程，更新数据库
            print('[update_hot_word] True')
            t = threading.Thread(target=db_helper.update_tables, args=(','.join(key_word_list), max_hot_words))
            t.setDaemon(True)
            t.start()
        else:
            print('[update_hot_word] False')
        return ','.join(key_word_list)

@app.route('/get_hot_words', methods=['POST', 'GET'])
def get_hot_words():
    return db_helper.get_hottest_words()


if __name__ == '__main__':
    app.run(debug=True, port=9090)
