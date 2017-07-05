#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
# @Time    : 2017/7/5 10:57
# @Author  : jeffreysun
# @Site    : 
# @File    : createMarkdownFromSql.py
# @Software: PyCharm
"""

import re
import codecs

import logging.config
logging.config.fileConfig("../conf/logging.ini")


class CreateMarkdownFromSql():
    """
    由数据库导出的sql结构文件生成md文档的说明文件
    """
    _table_temp = """
## %d %s

字段名|字段类型|属性|说明
-------|---------|-----|----
%s

```sql
%s
```

"""

    def __init__(self, input_file_name):
        self._sql_file_path = input_file_name

    def _get_table_item_info(self, table_item):
        logging.debug(table_item)
        item_name = re.search(r'(?<=`)(\w)+', table_item).group(0)
        used_len = len(item_name) + 2
        left_str = table_item[used_len:].strip()
        type_name = re.search(r'(\w)+(\(\d+\))?', left_str).group(0)
        used_len = len(type_name)
        left_str = left_str[used_len:].strip()
        comment_index = left_str.find("COMMENT")
        if comment_index != -1:
            left_str_arr = left_str.split("COMMENT")
            item_property = left_str_arr[0].strip()
            item_comment = left_str_arr[1].strip()[1:-1]
        else:
            item_property = left_str[:-1]
            item_comment = ""

        return item_name,type_name,item_property,item_comment


    def _handle_one_table(self, index, table_sql):
        line_list = table_sql.splitlines()
        table_item = []
        first_line = line_list.pop(0)
        logging.debug(first_line)
        table_name = re.search(r'(?<=`)(\w)+(?=`)',first_line).group(0)
        for i in range(len(line_list)) :
            line_item = line_list[i].strip()
            if re.match(r'`', line_item):
                table_item.append(self._get_table_item_info(line_item))

        def f(x):
            return " | ".join(x)

        table_item = map(f, table_item)

        table_str = self._table_temp.decode('utf-8') % (index, table_name, '\n'.join(table_item), table_sql)
        print table_str
        return table_str





    def run(self):
        with codecs.open(self._sql_file_path,  'r','utf-8') as f:
            sql_content = f.read()
            # 去除块状
            sql_content = re.sub(r'\/\*(\s|.)*?\*\/', "", sql_content)
            sql_content = re.sub(r'((?<=\n)SET(.)*\n)|((?<=\n)--(.)*\n)',"",sql_content)
            sql_content = sql_content.strip()
            tables_list = re.split(r'(\n|^)DROP TABLE(.)*;',sql_content)
            index = 1
            output_str = """[TOC]
# 数据库文档

"""
            output_str = output_str.decode("utf-8")
            for i in range(len(tables_list)):
                table_sql = tables_list[i].strip()
                print table_sql.find("CREATE TABLE")
                print table_sql
                if(table_sql.find("CREATE TABLE") > -1):
                    output_str += self._handle_one_table(index, table_sql)
                    index += 1

            print output_str
            output_path = self._sql_file_path[:-4] +".md"
            with codecs.open(output_path,'w', 'utf-8') as wr:
                wr.write(output_str)



if __name__ == '__main__':
    logging.info("start")
    input_file_name = "../../data/test.sql"
    c_markdown = CreateMarkdownFromSql(input_file_name)
    c_markdown.run()
    logging.info("finnish")

