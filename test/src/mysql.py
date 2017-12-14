import pymysql

host = 'localhost'
port = 3306
user = 'root'
password = 'keyan123'
database = 'test_db'
charset = 'utf8'

def load_data():
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)
    cursor = conn.cursor()
    sql = 'select %s from article;'
    cursor.execute(sql % 'key_words')
    kw_list = list()
    for res in cursor.fetchall():
        kw_list.extend(res[0].split(','))
    cursor.close()
    conn.close()
    return kw_list
    

if __name__ == '__main__':
    kw_list = load_data()
    kw_norepeated_list = list(set(kw_list))
    kw_cnt_list = []
    cnt_dict = dict()
    for kw in kw_norepeated_list:
        kw_cnt_list.append(kw_list.count(kw))
    max_cnt = 5
    a = 0
    while a < max_cnt and a < len(kw_norepeated_list):
        maxv = max(kw_cnt_list)
        maxi = kw_cnt_list.index(maxv)
        print(kw_norepeated_list[maxi], maxv)
        kw_cnt_list.pop(maxi)
        kw_norepeated_list.pop(maxi)
        a += 1
