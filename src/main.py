from flask import Flask
from flask import request
import pynlpir
import threading
import sys
sys.path.append('/home/zwm/Workplace/SchoolApp/src')
import db_helper

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome, here is GKW!'

@app.route('/get_key_words', methods=['POST', 'GET'])
def get_key_words():
    s = ''
    max_words = 3
    update_hot_word = 'True'
    # get doc
    if request.method == 'POST':
        s = request.form.get('s', type=str, default='')
        update_hot_word = request.form.get('update_hot_word', type=str, default='True') # 是否更新hot_word表
        try:
            max_words = request.form.get('max_words', type=str, default='3')
            # print('\tmax_words=[', type(max_words), ']')
            if (max_words != ''): # 有max_words参数（可能是默认值'3'）
                print('[POST] max_words yes')
                max_words = int(max_words.strip())
                print('\tmax_words =', max_words)
            else:
                max_words = 3
                print('[POST] max_words no')
        except: # max_words参数处理异常，设置默认值3
            max_words = 3
    elif request.method == 'GET':
        s = request.args.get('s')
        max_words = request.args.get('max_words')
        if max_words == None:
            max_words = 3
            print('[GET] max_words no')
        else:
            max_words = int(max_words.strip())
            print('[GET] max_words yes')
            print('\tmax_words =', max_words)
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
        # 新开一个线程，更新数据库
        t = threading.Thread(target=db_helper.update_tables, args=(','.join(key_word_list),))
        t.setDaemon(True)
        t.start()
        return ','.join(key_word_list)

@app.route('/get_hot_words', methods=['POST', 'GET'])
def get_hot_words():
    return db_helper.get_hottest_words()


if __name__ == '__main__':
    app.run(debug=True, port=9090)
