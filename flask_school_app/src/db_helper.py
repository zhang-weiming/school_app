import pymysql
import threading
from operator import itemgetter

host = 'localhost'
port = 3306
user = 'root'
password = 'keyan123'
database = 'test_db'
charset = 'utf8'

table_article = 'article'
table_key_word_weight = 'key_word_weight'
table_hot_word_for_search = 'hot_word_for_search'

max_hot_words = 20

def init_db_conn():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
    cursor = conn.cursor()
    return conn, cursor

def close_db_conn(conn, cursor):
    cursor.close()
    conn.close()

# 获取表article中的关键词列中的所有词组成的list
def load_data(conn, cursor):
    # conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
    # cursor = conn.cursor()
    sql = 'select %s from %s;'
    cursor.execute(sql % ('key_words', table_article))
    conn.commit()
    kw_list = list()
    for res in cursor.fetchall():
        kw_list.extend(res[0].split(','))
    # cursor.close()
    # conn.close()
    return kw_list

# 统计一个list中的不同词分别出现的次数
def key_word_counter(kw_list):
    kw_norepeated_list = list(set(kw_list))
    kw_cnt_list = []
    # kw2cnt = dict()
    for kw in kw_norepeated_list:
        # kw2cnt[kw] = kw_list.count(kw)
        kw_cnt_list.append( [kw, kw_list.count(kw)] )
    # kw_cnt_list.sort(key = itemgetter(1), reverse=True)
    # print(kw_cnt_list)
    return kw_cnt_list
    # return kw2cnt

# 初始化表key_word_weight
def init_table_key_word_weight():
    conn, cursor = init_db_conn()
    sql = 'drop table if exists %s;' % table_key_word_weight
    sql += 'create table if not exists %s ' % table_key_word_weight
    sql += '(word varchar(20) primary key not null, weight int not null);'
    cursor.execute(sql)
    conn.commit()
    kw_list = load_data(conn, cursor)
    kw_cnt_list = key_word_counter(kw_list)
    for kw in kw_cnt_list:
        sql = 'insert into %s values("%s", %d);' % (table_key_word_weight, kw[0], kw[1])
        # print(sql)
        cursor.execute(sql)
    conn.commit()
    print('[DB] init table [%s] finish.' % table_key_word_weight)
    close_db_conn(conn, cursor)

# 初始化表hot_word_for_search，并设置长度为max_words
def init_table_hot_word_for_search(max_words):
    conn, cursor = init_db_conn()
    sql = 'drop table if exists %s;' % table_hot_word_for_search
    sql += 'create table if not exists %s ' % table_hot_word_for_search
    sql += '(id int primary key not null, word varchar(20) not null, weight int not null);'
    cursor.execute(sql)
    conn.commit()
    hot_word_list = get_hot_words(conn, cursor, max_words)
    a = 1
    for hw in hot_word_list:
        sql = 'insert into %s values(%d, "%s", %d);' % (table_hot_word_for_search, a, hw[0], hw[1])
        print(sql)
        cursor.execute(sql)
        a += 1
    conn.commit()
    print('[DB] init table [%s] finish.' % table_hot_word_for_search)
    close_db_conn(conn, cursor)

# 获取表key_word_weight中的数据
def get_table_key_word_weight(conn, cursor):
    word2weight = dict()
    sql = 'select %s from %s;' % ('word, weight', table_key_word_weight)
    cursor.execute(sql)
    conn.commit()
    for res in cursor.fetchall():
        word2weight[res[0]] = res[1]
    return word2weight

# 获取表hot_word_for_search中的数据
def get_table_hot_word_for_search(conn, cursor):
    hw2weight = dict()
    sql = 'select %s from %s;' % ('word, weight', table_hot_word_for_search)
    cursor.execute(sql)
    conn.commit()
    for res in cursor.fetchall():
        hw2weight[res[0]] = res[1]
    return hw2weight

# 获取热词，外留接口
def get_hottest_words():
    conn, cursor = init_db_conn()
    sql = 'select word from %s;' % table_hot_word_for_search
    cursor.execute(sql)
    conn.commit()
    hw_str = list()
    for res in cursor.fetchall():
        hw_str.append(res[0])
    close_db_conn(conn, cursor)
    return ','.join(hw_str)

# 更新数据库，外留接口
def update_tables(key_word_str, max_hot_words=max_hot_words):
    conn, cursor = init_db_conn() # 初始化数据库连接
    kw_list = key_word_str.split(',')
    kw_cnt_list = key_word_counter(kw_list) # 计算每个关键词的频数
    word2weight = update_table_key_word_weight(conn, cursor, kw_cnt_list) # 更新key_word_weight
    update_table_hot_word_for_search(conn, cursor, word2weight, max_hot_words) # 更新hot_word_for_search
    close_db_conn(conn, cursor) # 关闭数据库连接

def update_table_key_word_weight(conn, cursor, kw_cnt_list):
    word2weight = get_table_key_word_weight(conn, cursor) # 获取数据库中已保存关键词的频数，以dict返回
    # for i in range(len(kw_cnt_list)):
    #     kw = kw_cnt_list[i][0]
    #     if kw in word2weight:
    #         kw_cnt_list[i][1] += word2weight[kw]
    #         sql = 'update %s set weight = %d where word = "%s";' % (table_key_word_weight, kw_cnt_list[i][1], kw)
    #         # print(sql)
    #         cursor.execute(sql)
    #     else:
    #         sql = 'insert into %s values("%s", %d);' % (table_key_word_weight, kw, kw_cnt_list[i][1])
    #         # print(sql)
    #         cursor.execute(sql)
    for kw in kw_cnt_list:
        if kw[0] in word2weight:
            word2weight[kw[0]] += kw[1]
            sql = 'update %s set weight = %d where word = "%s";' % (table_key_word_weight, word2weight[kw[0]], kw[0])
            # print(sql)
            cursor.execute(sql)
        else:
            word2weight[kw[0]] = kw[1]
            sql = 'insert into %s values("%s", %d);' % (table_key_word_weight, kw[0], kw[1])
            # print(sql)
            cursor.execute(sql)
    conn.commit()
    print('[DB] update table [%s] finished.' % table_key_word_weight)
    return word2weight

def update_table_hot_word_for_search(conn, cursor, word2weight, max_words):
    # hw2weight = get_table_hot_word_for_search(conn, cursor) # 获取数据库中原来的数据
    # for kw_cnt in kw_cnt_list:
    #     hw2weight[ kw_cnt[0] ] = kw_cnt[1] # 有，则覆盖；没有，则添加
    # hw_list = [(hw, hw2weight[hw]) for hw in hw2weight]
    # hw_list.sort(key=itemgetter(1), reverse=True)
    hw_list = [(w, word2weight[w]) for w in word2weight]
    hw_list.sort(key=itemgetter(1), reverse=True)

    sql = 'delete from %s where id > 0;' % table_hot_word_for_search # 删除数据库中的旧数据
    cursor.execute(sql)
    conn.commit()
    a = 0
    while a < max_words and a < len(hw_list):
        sql = 'insert into %s values(%d, "%s", %d)' % (table_hot_word_for_search, a + 1, hw_list[a][0], hw_list[a][1])
        cursor.execute(sql)
        a += 1
    conn.commit()
    print('[DB] update table [%s] finished.' % table_hot_word_for_search)


def get_hot_words(conn, cursor, max_words):
    # sql = 'select %s from %s;' % ('word, weight', table_key_word_weight)
    # cursor.execute(sql)
    # conn.commit()
    # word_list = list()
    # weight_list = list()
    # for res in cursor.fetchall():
    #     word_list.append(res[0])
    #     weight_list.append(res[1])
    word2weight = get_table_key_word_weight(conn, cursor)
    hw_list = [(hw, word2weight[hw]) for hw in word2weight]
    hw_list.sort(key=itemgetter(1), reverse=True)
    # kw_list = get_hottest_words(word_list, word2weight, max_words)
    return hw_list[:max_words]

def show_table(conn, cursor, table_name):
    # conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
    # cursor = conn.cursor()
    sql = 'select * from %s;'
    cursor.execute(sql % table_name)
    conn.commit()
    for res in cursor.fetchall():
        print(res)
    # cursor.close()
    # conn.close()


if __name__ == '__main__':
    '''
    conn, cursor = init_db_conn()
    key_word_str = '关键词1,关键词2,关键词3,关键词4,关键词5'
    # kw_list = load_data(conn, cursor)
    print('Before update:')
    show_table(conn, cursor, table_key_word_weight)
    print('---------------')
    show_table(conn, cursor, table_hot_word_for_search)
    print('---------------')
    update_tables(key_word_str)
    print('After update:')
    show_table(conn, cursor, table_key_word_weight)
    print('---------------')
    show_table(conn, cursor, table_hot_word_for_search)
    print('---------------')
    close_db_conn(conn, cursor)
    '''

    init_table_key_word_weight()
    init_table_hot_word_for_search(20)
