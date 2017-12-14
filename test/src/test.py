import pynlpir

if __name__ == '__main__':
    pynlpir.open()
    s = '我爱你中国'
    # segment_list = pynlpir.segment(s, pos_tagging=False)
    # for seg in segment_list:
    #     print(seg)

    key_word_list = pynlpir.get_key_words(s, max_words=10, weighted=True)
    for key_word in key_word_list:
        print(key_word[0], '\t', key_word[1])

    pynlpir.close()
