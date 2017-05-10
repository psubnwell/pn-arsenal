import os
import re
import json
import langid
import opencc
import pandas as pd

CHINESE_CONVERT_CONFIG = 'zht2zhs.ini'

def chinese_convert(foo, config=CHINESE_CONVERT_CONFIG):
    if type(foo) == 'str':  # Foo is a string.
        return opencc.convert(foo, config=config)
    else:  # Foo is other data structure, such as list, tuple.
        tmp = json.dumps(foo, ensure_ascii=False)
        tmp = opencc.convert(tmp, config=config)
        return json.loads(tmp)

def extract_language(langlinks_sql, language_code):
    item = re.findall(r'\((\d+),\'(' + language_code + r')\',\'(.*?)\'\)', langlinks_sql)

    item_nonempty = []
    for i in item:
        if i[2] != '':
            item_nonempty.append(i)

    if language_code == 'zh':
        item_nonempty = chinese_convert(item_nonempty)
    return item_nonempty

def extract_id(langlinks_sql, page_id):
    item = re.findall(r'\((' + str(page_id) + r'),\'(.+?)\',\'(.*?)\'\)', langlinks_sql)

    item_nonempty = []
    for i in item:
        if i[2] != '':
            item_nonempty.append(i)

    for i in range(len(item)):
        if item[i][1] == 'zh':
            item[i] = chinese_convert(item[i])
    return item

def extract_title(langlinks_sql, page_title, language_code=None):
    if language_code == None:
        language_code = langid.classify(page_title)[0]
    if language_code == 'zh':
        page_title = chinese_convert(page_title)

    item = extract_language(langlinks_sql, language_code)
    return [i for i in item if i[2] == page_title]

def translate_title(langlinks_sql, title, target_language_code='all'):
    # import langid
    # language_code = langid.classify(title)[0]
    page_id = extract_title(langlinks_sql, title)[0][0]
    item = extract_id(langlinks_sql, page_id)
    if target_language_code == 'all':
        return item
    else:
        return [i for i in item if i[1] == target_language_code]

def id2title(pages_articles_multistream_index_txt, page_id):
    item = re.findall(r'\d+:' + str(page_id) + r':(.*)', 
        pages_articles_multistream_index_txt)
    return item[0]

def title2id(pages_articles_multistream_index_txt, page_title):
    language_code = langid.classify(page_title)[0]
    if language_code == 'zh':
        page_title_zhs = opencc.convert(page_title, config='zht2zhs.ini')
        page_title_zht = opencc.convert(page_title, config='zht2zhs.ini')
        item = re.findall(r'\d+:(\d+):({0}|{1})\n'.format(page_title_zhs, page_title_zht), 
            pages_articles_multistream_index_txt)
    else:
        item = re.findall(r'\d+:(\d+):({0})'.format(page_title), 
            pages_articles_multistream_index_txt)
    return item

def read_wiki(file_path):
    f = open(file_path, errors='ignore').read()
        # The wiki file is not pure UTF-8, so it's better to ignore the error.
    if file_path.split('/')[-1].startswith('zh'):  # Chinese wiki needs convertion.
        f = opencc.convert(f, config='zht2zhs.ini')
    return f




if __name__ == '__main__':
    pd.read_sql_table('langlinks', open('./zhwiki-20170501-langlinks.sql', errors='ignore'))
    # The wiki file is not pure UTF-8, so it's better to ignore the error.
    langlinks_zh = open('./zhwiki-20170501-langlinks.sql', errors='ignore').read()
    index_zh = open('./zhwiki-20170501-pages-articles-multistream-index.txt', 
        errors='ignore').read()

    langlinks_en = open('./enwiki-20170501-langlinks.sql', errors='ignore').read()

    print(extract_language(langlinks_zh, 'en')[:10])
    print(extract_id(langlinks_zh, 7662)[:10])
    print(extract_title(langlinks_en, '哈尔滨工业大学'))
    print(translate_title(langlinks_de, '国立交通大学'))
    print(id2title(index_zh, 425))
    print(title2id(index_zh, '浙江省'))
