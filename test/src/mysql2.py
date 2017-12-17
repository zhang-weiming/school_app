import pymysql

host = 'localhost'
port = 3306
user = 'root'
password = 'keyan123'
database = 'test_db'
charset = 'utf8'

table_article = 'article'
table_key_word_weight = 'key_word_weight'
table_hot_word_for_search = 'hot_word_for_search'

max_word_cnt = 5

def init_db_conn():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
    cursor = conn.cursor()
    return conn, cursor

def close_db_conn(conn, cursor):
    cursor.close()
    conn.close()

# 获取关键词列，以list返回
def load_data():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
    cursor = conn.cursor()
    sql = 'select %s from %s;'
    cursor.execute(sql % ('key_words', table_article))
    conn.commit()
    kw_list = list()
    for res in cursor.fetchall():
        kw_list.extend(res[0].split(','))
    cursor.close()
    conn.close()
    return kw_list

def key_word_counter(kw_list):
    kw_norepeated_list = list(set(kw_list))
    # kw_cnt_list = []
    kw2cnt = dict()
    for kw in kw_norepeated_list:
        kw2cnt[kw] = kw_list.count(kw)
        # kw_cnt_list.append(kw_list.count(kw))
    # return kw_norepeated_list, kw_cnt_list
    return kw2cnt
    
def get_table_key_word_weight():
    word2weight = dict()
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
    cursor = conn.cursor()
    sql = 'select %s from %s;'
    cursor.execute(sql % ('word, weight', table_key_word_weight))
    for res in cursor.fetchall():
        word2weight[res[0]] = res[1]
        # print(res)
    cursor.close()
    conn.close()
    return word2weight

def update_table_key_word_weight(kw_list):
    kw2cnt = key_word_counter(kw_list) # 计算每个关键词的频数
    word2weight = get_table_key_word_weight() # 获取数据库中已保存关键词的频数
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
    cursor = conn.cursor()
    # kw_norepeated_list, kw_cnt_list = key_word_counter(kw_list)
    for kw in kw2cnt.keys():
        if kw in word2weight.keys():
            # word2weight[kw] = word2weight[kw] + kw2cnt[kw]
            sql = 'update %s set weight = %d where word = "%s";' % (table_key_word_weight, word2weight[kw] + kw2cnt[kw], kw)
            print(sql)
            cursor.execute(sql)
        else:
            # word2weight[kw] = kw2cnt[kw]
            sql = 'insert into %s values("%s", %s);' % (table_key_word_weight, kw, kw2cnt[kw])
            print(sql)
            cursor.execute(sql)
        conn.commit()
    cursor.close()
    conn.close()

def show_table_key_word_weight():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
    cursor = conn.cursor()
    sql = 'select * from %s;'
    cursor.execute(sql % table_key_word_weight)
    for res in cursor.fetchall():
        print(res)
    cursor.close()
    conn.close()


if __name__ == '__main__':
    kw_list = load_data()
    # print(kw_list)
    # word2weight = get_table_key_word_weight()
    # for word in word2weight.keys():
    #     print(word, word2weight[word])
    print('Before update:')
    show_table_key_word_weight()
    update_table_key_word_weight(kw_list)
    print('---------------\n')
    print('After update:')
    show_table_key_word_weight()
    print('---------------\n')
    '''
    kw_norepeated_list, kw_cnt_list = key_word_counter(kw_list)
    a = 0
    while a < max_word_cnt and a < len(kw_norepeated_list):
        maxv = max(kw_cnt_list)
        maxi = kw_cnt_list.index(maxv)
        print(kw_norepeated_list[maxi], maxv)
        kw_cnt_list.pop(maxi)
        kw_norepeated_list.pop(maxi)
        a += 1
    '''
