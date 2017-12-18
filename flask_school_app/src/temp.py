import os
import codecs
import pynlpir

NEW_LINE = '\n'
SOURCE_DOC_DIR_PATH = '../test/data/docs/'
SEGMENT_DOC_PATH = '../test/data/segment/'

def load_doc_list():
    pynlpir.open()
    doc_list = os.listdir(SOURCE_DOC_DIR_PATH)
    segment_list = []
    for doc in doc_list:
        fr = codecs.open(SOURCE_DOC_DIR_PATH + doc, 'r', 'utf-8')
        line_list = fr.read()
        fr.close()
        '''
        line_list = line_list.split(NEW_LINE)
        line_list.pop()
        # seg_str = ''
        for i in range(len(line_list)):
            segment = pynlpir.segment(line_list[i], pos_tagging=False)
            seg_str = ''
            for seg in segment:
                seg_str += seg + ' '
            line_list[i] = seg_str.strip()
        # segment_list.append(' '.join(line_list))
        temp_str = ' '.join(line_list)
        '''
        key_word_list = pynlpir.get_key_words(line_list, max_words=10, weighted=True)
        for key_word in key_word_list:
            print(key_word[0], '\t', key_word[1])
        pynlpir.close()
        exit(0)
    # for segment in segment_list:
    #     print(segment)


if __name__ == '__main__':
    load_doc_list()
    # print('OK')
