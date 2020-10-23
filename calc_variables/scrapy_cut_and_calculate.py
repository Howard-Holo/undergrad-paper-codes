import jieba
import csv
import time
import os, sys
import pandas as pd
import numpy as np
from collections import Counter

csv.field_size_limit(sys.maxsize)


def emotionAnalysis(dict_pyra, text_a):
    # 开始按照金字塔方式找词
    sum_f = 0
    last_head = "一"
    pyra_row = 1  # if pyra_row = 0, not exist in pyramid dict.
    for i in text_a:

        if (i[
            0] == last_head):  # i[0] is the first char of the word, compared with the last_head to determine whether to relocate the row
            if (pyra_row == 0):
                freq = 0  # not exist in pyramid dict...
            else:
                freq = dict_pyra[pyra_row][1:].count(i)  # locate the row by pyra_row, and count the freq of the word in the rest of the row

            sum_f += freq
            # print(i, freq, last_head, pyra_row)

        else:  # different capital char, relocate the row and save variable
            last_head = i[0]

            flag_pyra_row = False  # relocate and find the pyra_row
            try:
                for j in range(1300):
                    if (i[0] == dict_pyra[j][0]):
                        pyra_row = j
                        flag_pyra_row = True
                        break
            except:
                flag_pyra_row = False
            if (flag_pyra_row == False):  # cannot find the capital char in pyramid dict, must not exist.
                pyra_row = 0
                freq = 0
                sum_f += freq
                # print(i, freq, last_head, pyra_row)
                continue
            else:
                freq = dict_pyra[pyra_row][1:].count(i)  # locate the row by pyra_row, and count the freq of the word in the rest of the row
                sum_f += freq
                # print(i, freq, last_head, pyra_row)
    # output
    print(sum_f)
    return sum_f


def work_function(folder_route, task_file_name, task_title):
    # =====================================================================================================================
    # step 1
    # 打开文件，数据清洗
    # =====================================================================================================================

    with open("%s" % os.path.join(folder_route, task_file_name), 'r', encoding='utf-8') as rd:  # 打开Annual Repo里的原始文件
        a = ""
        for i in rd:
            i = i.replace('\n', "").replace('\t', "").replace(" ", "").replace(",", "").replace("'", "").replace("\"", "")
            a = a + str(i)
        # print(a)

    title_freq = a.count(task_title)

    with open("jieba_temp.csv", 'w', encoding='utf-8') as wt:  # step 2 可以用jieba_temp替代
        wt.write("Annual Report Blank-Moved.")
        wt.write('\n')
        for i in a:
            wt.write(i)
            if (i.find("。") != -1 or i.find("；") != -1):
                wt.write('\n')

    # =====================================================================================================================
    # step 2
    # 分析标题是否有语气词。执行分词并转存临时csv
    # =====================================================================================================================

    # 导入术语词典和专有名词词典
    data_csv = pd.read_csv('Dict_Accounting.csv')
    data_csv = data_csv.dropna()  # 滤除缺失数据
    dataset = data_csv.values   # 获得csv的值

    for i in dataset:
        jieba.add_word(i[0])

    # 逐句分词并写为csv
    with open("jieba_temp.csv", 'r', encoding='utf-8') as t:
        jieba_temp = []
        temp_read = csv.reader(t)
        for i in temp_read:
            jieba_temp.append(i)

    with open("jieba_temp.csv", 'w', encoding='utf-8') as t:
        t.write("Annual Report Segmented.")
        t.write('\n')
        for i in jieba_temp[1:]:
            seg_list = jieba.cut(i[0], cut_all=False, HMM=True)
            # print(",".join(seg_list))
            t.write(",".join(seg_list))
            t.write('\n')

    # =====================================================================================================================
    # step 3
    # 利用频率法，高效率分词
    # 原理：总积极词汇 = SUM（第i个词汇词频 * 是否为积极词汇）
    # 使用基数排序加速匹配计算
    # =====================================================================================================================

    with open("jieba_temp.csv", 'r', encoding='utf-8') as t:

        rd = csv.reader(t)
        a = []

        # 筛选词，将中文拿出
        for i in rd:
            # print(i)
            for j in i:
                # print(j)
                if(j == ""):
                    continue
                if(ord(j[0]) < ord("一")):
                    continue
                if(ord(j[0]) >= ord("！")):
                    continue

                a.append(j)

        a = sorted(a)

        # 词数统计、字数统计
        count_word = 0
        count_char = 0
        for i in a:
            count_word += 1
            for j in i:
                count_char += 1
        # print(a)

    pos_f = emotionAnalysis(dict_pos_pyra, a)
    neg_f = emotionAnalysis(dict_neg_pyra, a)
    # tone = (pos_f - neg_f) / (pos_f + neg_f)

    print("Positive:", pos_f, '\t', "Negative:", neg_f, '\t', "Count Word:", count_word, '\t', "Count Char:", count_char)
    print(time.ctime())
    # print("Pure Positive Tone Rate:", tone)

    out_row = []
    out_row.append(s_code)
    out_row.append(file_year)
    out_row.append(pos_f)
    out_row.append(neg_f)
    out_row.append(count_word)
    out_row.append(count_char)
    out_row.append(title_freq)
    return out_row


def identifyTitle(task_stock):
    for i in stock_name:  # 查找股票代码的简称（本来有个用dict或tuple的自带函数，忘了）
        if (i[0] == task_stock):
            i[1] = i[1].replace("*", "").replace("ST", "").replace("A", "").replace("B", "")
            task_name = i[1]
            break

    t_emotion = 0

    task_name_list = jieba.cut(task_name)       # 判断股票简称里是否有语气词
    task_name_list = ",".join(task_name_list)
    task_name_list = task_name_list.split(",")
    print(task_name_list)

    t_emotion = emotionAnalysis(dict_pos_pyra, task_name_list)
    # print(t_emotion, task_name_list)
    if (t_emotion > 0):
        return t_emotion, task_name
    else:
        t_emotion = - emotionAnalysis(dict_neg_pyra, task_name_list)
        return t_emotion, task_name




# =====================================================================================================================
    # step 4，即主程序
    # 输出为一个csv基础数据
    # 格式：stock code, year, pos, neg, all words, all char, title_freq, title_emotion
# =====================================================================================================================

# 获取该目录下所有文件，存入列表中
path_in = '~~//PycharmProjects/untitled/Annual Repo'
folderList = os.listdir(path_in)
folderList = sorted(folderList)
# print(folderList)

with open("C_positive_pyramid.csv", 'r', encoding='utf-8') as d:
    rd = csv.reader(d)
    dict_pos_pyra = []
    for i in rd:
        dict_pos_pyra.append(i)
    # print(dict_pos_pyra)

with open("C_negative_pyramid.csv", 'r', encoding='utf-8') as d:
    rd = csv.reader(d)
    dict_neg_pyra = []
    for i in rd:
        dict_neg_pyra.append(i)
    # print(dict_neg_pyra)

with open("stock_name.csv", 'r', encoding='utf-8') as w:
    wt = csv.reader(w)
    stock_name = []
    for i in wt:
        stock_name.append(i)

with open("ar_emotion.csv", 'w', encoding='utf-8') as ar_e:
    ar_e_out = csv.writer(ar_e)
    out_row = ["stock code", "year", "pos", "neg", "all words", "all char", "title_freq", "title_emotion"]
    ar_e_out.writerow(out_row)

    sum_count = 0
    for i in folderList:
        sum_count += 1

    count = 0
    for s_code in folderList:       # s_code是股票代码
        count += 1

        print("s_code:", s_code)
        title_emotion, title_name = identifyTitle(s_code)
        # print(title_emotion, title_name)

        folder_on = path_in + "/" + s_code
        print(folder_on)

        fileList = os.listdir(folder_on)
        fileList = sorted(fileList)

        print(fileList)
        for current_task_file in fileList:
            print("================================================================================================")
            print(count, "/", sum_count)

            file_year = current_task_file[10:14]
            print(s_code, file_year)
            if(file_year == "2019"):
                continue

            ar_e_write = work_function(folder_on, current_task_file, title_name)
            ar_e_write.append(title_emotion)      # 输出
            # ar_e_out.append(title_freq)
            ar_e_out.writerow(ar_e_write)


