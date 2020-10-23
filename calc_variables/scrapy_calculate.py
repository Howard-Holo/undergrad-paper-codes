import csv
import pandas as pd
import numpy as np
import time
import jieba
from collections import Counter

def deleteDuplicatedElementFromList(listA):
    # return list(set(listA))
    return sorted(set(listA), key=listA.index)

# =====================================================================================================================
# 做"金字塔"结构字典（基数排序）
# 示例： ['一','一专多能','一丝不差',....]
# =====================================================================================================================

data_csv = pd.read_csv('C_positive_pock.csv')
data_csv = data_csv.dropna()  # 滤除缺失数据
dict_pos = data_csv.values   # 获得csv的值
dict_pos = list(dict_pos)   # 转化为list方便调用count函数
dict_pos = sorted(dict_pos)

head_pos = []
for i in dict_pos:
    head_pos.append(i[0][0])
head_pos = deleteDuplicatedElementFromList(head_pos)
# print(len(head_pos))

with open("C_positive_pyramid.csv", 'w', encoding='utf-8') as wt:
    w = csv.writer(wt)
    wt.write("Positive")
    wt.write('\n')
    head_p = '一'
    row_print = ['一']
    for i in dict_pos:
        if(i[0][0] == head_p):
            row_print.append(i[0])
        else:
            # print(row_print)
            w.writerow(row_print)
            head_p = i[0][0]
            row_print = []
            row_print.append(head_p)
            row_print.append(i[0])

data_csv = pd.read_csv('C_negative_pock.csv')
data_csv = data_csv.dropna()  # 滤除缺失数据
dict_neg = data_csv.values   # 获得csv的值
dict_neg = list(dict_neg)   # 转化为list方便调用count函数
dict_neg = sorted(dict_neg)

head_neg = []
for i in dict_neg:
    head_neg.append(i[0][0])
head_neg = deleteDuplicatedElementFromList(head_neg)
# print(len(head_neg))

with open("C_negative_pyramid.csv", 'w', encoding='utf-8') as wt:
    w = csv.writer(wt)
    wt.write("Negative")
    wt.write('\n')
    head_p = '一'
    row_print = ['一']
    for i in dict_neg:
        if(i[0][0] == head_p):
            row_print.append(i[0])
        else:
            # print(row_print)
            w.writerow(row_print)
            head_p = i[0][0]
            row_print = []
            row_print.append(head_p)
            row_print.append(i[0])

# =====================================================================================================================
# 清洗特殊词
# =====================================================================================================================

# temp = []
# with open("111.csv", 'w', encoding='utf-8') as wt:
#     for i in dict_pos:
#         if(len(i[0])==1):
#             temp.append(i[0])
#             continue
#         if(i[0].find("地") != -1):
#             temp.append(i[0])
#             continue
#
#         wt.write(i[0])
#         wt.write('\n')

# =====================================================================================================================
# 查重
# =====================================================================================================================

# def search_and_append():
#     for j in temp :
#         # print("R:",i ,", I:", j)
#         if str(i[0]) == str(j[0]):
#             return
#
#     temp.append(i[0])
#     wt.write(i[0])
#     wt.write('\n')
#
# temp = []
# with open("111.csv", 'w', encoding='utf-8') as wt:
#     for i in dict_pos:
#         if temp == []:
#             temp.append(i[0])
#             wt.write(i[0])
#             wt.write('\n')
#             continue
#         search_and_append()


# =====================================================================================================================
# 利用频率法，高效率分词
# 原理：总积极词汇 = SUM（第i个词汇词频 * 是否为积极词汇）
# 使用基数排序加速匹配计算
# =====================================================================================================================

def emotionAnalysis(dict_pyra, text_a):
    # 开始按照金字塔方式找词
    sum_f = 0
    last_head = "一"
    pyra_row = 1  # if pyra_row = 0, not exist in pyramid dict.
    for i in text_a:

        if (i[0] == last_head):  # i[0] is the first char of the word, compared with the last_head to determine whether to relocate the row
            if (pyra_row == 0):
                freq = 0  # not exist in pyramid dict...
            else:
                freq = dict_pyra[pyra_row][1:].count(
                    i)  # locate the row by pyra_row, and count the freq of the word in the rest of the row

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
                freq = dict_pyra[pyra_row][1:].count(
                    i)  # locate the row by pyra_row, and count the freq of the word in the rest of the row
                sum_f += freq
                # print(i, freq, last_head, pyra_row)
    # output
    print(sum_f)
    return sum_f


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

with open("jieba_temp.csv", 'r', encoding='utf-8') as t:
    rd = csv.reader(t)

    a = []

    for i in rd:
        for j in i:
            if(ord(j[0]) < ord("一")):
                continue
            a.append(j)

    a = sorted(a)
    # print(a)

pos_f = emotionAnalysis(dict_pos_pyra, a)
neg_f = emotionAnalysis(dict_neg_pyra, a)
tone = (pos_f - neg_f) / (pos_f + neg_f)

print("Positive:", pos_f, '\t', "Negative:", neg_f)
print("Pure Positive Tone Rate:", tone)





#
#     for i in b:
#         print(i, a.count(i))
#         print(i, a.count(i), dict_pos.count(i), dict_neg.count(i))





# =====================================================================================================================
# 生成词频统计表
# =====================================================================================================================


#     for i in a:
#         print(i, last_one, last_tone)
#         if (ord(i[0]) < ord("一")): continue
#
#         if (i == last_one):
#             if(last_tone == 1):
#                 pos += 1
#                 continue
#             elif(last_tone == 0):
#                 continue
#             elif(last_tone == -1):
#                 neg += 1
#                 continue
#
#         this_tone = 0
#         for j in dict_pos:
#             if (i == j[0] or (i == last_one and last_tone == 1)):
#                 pos += 1
#                 last_one = i
#                 last_tone = 1
#                 this_tone = 1
#                 # print("Positive",i, j[0], pos)
#                 break
#         if(this_tone == 1): continue
#
#
#         for j in dict_neg:
#             if (i == j[0] or (i == last_one and last_tone == -1)):
#                 neg += 1
#                 last_one = i
#                 last_tone = -1
#                 # print("Negative",i, j[0], neg)
#                 break
#
#         last_one = ""
#         last_tone = 0
#
# print("Jieba Method:")
# tone = (pos - neg) / (pos + neg)
# end = time.time()
# # print("Time used:", end - start)
# print("Positive:", pos, '\t', "Negative:", neg)
# print("Tone: ", tone)
