import jieba
import csv
import pandas as pd
import time

# =====================================================================================================================
# step 1
# 打开文件，数据清洗
# =====================================================================================================================

with open("jieba_step_1.txt", 'r', encoding='utf-8') as rd:
    a = ""
    for i in rd:
        i = i.replace('\n',"").replace(" ","").replace(",","")
        a = a + str(i)

    print(a)

with open("jieba_step_2.txt", 'w', encoding='utf-8') as wt:

    wt.write("Annual Report Blank-Moved.")
    wt.write('\n')

    for i in a:
        wt.write(i)
        if(i.find("。") != -1 or i.find("；" ) != -1):
            wt.write('\n')



# =====================================================================================================================
# step 2
# 执行分词并转存临时csv
# =====================================================================================================================

# 导入术语词典和专有名词词典
data_csv = pd.read_csv('Dict_Accounting.csv')
data_csv = data_csv.dropna()  # 滤除缺失数据
dataset = data_csv.values   # 获得csv的值

for i in dataset:
    jieba.add_word(i[0])

# data_csv = pd.read_csv('C_positive_pock.csv')
# data_csv = data_csv.dropna()  # 滤除缺失数据
# dataset = data_csv.values   # 获得csv的值
#
# for i in dataset:
#     jieba.add_word(i[0])
#
# data_csv = pd.read_csv('C_negative_pock.csv')
# data_csv = data_csv.dropna()  # 滤除缺失数据
# dataset = data_csv.values   # 获得csv的值
#
# for i in dataset:
#     jieba.add_word(i[0])



# 逐句分词并写为csv
data_csv = pd.read_csv('jieba_step_2.txt')
data_csv = data_csv.dropna()  # 滤除缺失数据
dataset = data_csv.values   # 获得csv的值

with open("jieba_temp.csv", 'w', encoding='utf-8') as t:
    t.write("Annual Report Segmented.")
    t.write('\n')
    for i in dataset:
        seg_list = jieba.cut(i[0], cut_all=False, HMM=True)
        # print(",".join(seg_list))
        t.write(",".join(seg_list))
        t.write('\n')



# =====================================================================================================================
# 词频计算
# =====================================================================================================================

# data_csv = pd.read_csv('C_positive_pock.csv')
# data_csv = data_csv.dropna()  # 滤除缺失数据
# dict_pos = data_csv.values   # 获得csv的值
#
# data_csv = pd.read_csv('C_negative_pock.csv')
# data_csv = data_csv.dropna()  # 滤除缺失数据
# dict_neg = data_csv.values   # 获得csv的值
#
# with open("jieba_test.csv", 'r', encoding='utf-8') as t:
#     rd = csv.reader(t)
#     pos = 0
#     neg = 0
#     last_one = ""
#     last_tone = 0
#
#     Count = 0
#
#     # 计个时间
#     start = time.time()
#
#     for every_roll in rd:
#         # if(Count == 10): break
#         # Count += 1
#
#         every_roll = sorted(every_roll)
#         for i in every_roll:
#             if(ord(i[0]) < ord("一")): continue
#             for j in dict_pos:
#                 if(i == j[0] or (i == last_one and last_tone == 1)):
#                     pos += 1
#                     last_one = i
#                     last_tone = 1
#                     # print("Positive",i, j[0], pos)
#                     break
#             for j in dict_neg:
#                 if(i == j[0] or (i == last_one and last_tone == -1)):
#                     neg += 1
#                     last_one = i
#                     last_tone = -1
#                     # print("Negative",i, j[0], neg)
#                     break
#             last_one = ""
#             last_tone = 0
#
#         # print(every_roll)
# print("Jieba Method:")
# tone = (pos - neg) / (pos + neg)
# end = time.time()
# print("Time used:", end - start)
# print("Positive:", pos, '\t', "Negative:", neg)
# print("Tone: ", tone)



# =====================================================================================================================
# 词袋法
# =====================================================================================================================

# data_csv = pd.read_csv('C_positive_pock.csv')
# data_csv = data_csv.dropna()  # 滤除缺失数据
# dict_pos = data_csv.values   # 获得csv的值
#
# with open('111.txt', 'w', encoding='utf-8') as wt:
#     wtc = csv.writer(wt)
#
#     # 计个时间
#     start = time.time()
#
#     pos = 0
#     for i in dict_pos:
#         if(len(i[0])==1):
#             continue
#         c_i = a.count(i[0])
#         wtc.writerow([i[0], c_i, "Positive"])
#         # print(i[0], c_i, len(i[0]))
#         pos += c_i
#
#     data_csv = pd.read_csv('C_negative_pock.csv')
#     data_csv = data_csv.dropna()  # 滤除缺失数据
#     dict_pos = data_csv.values   # 获得csv的值
#
#     neg = 0
#     for i in dict_pos:
#         if(len(i[0])==1):
#             continue
#         c_i = a.count(i[0])
#         wtc.writerow([i[0], c_i, "Negative"])
#         # print(i[0], c_i, len(i[0]))
#         neg += c_i
#
# print("Count Method:")
# tone = (pos - neg) / (pos + neg)
# end = time.time()
# print("Time used:", end - start)
# print("Positive:", pos, '\t', "Negative:", neg)
# print("Tone: ", tone)

# print(b.count(a))

