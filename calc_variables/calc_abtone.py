import csv
import math
import pandas as pd
import numpy as np
import statsmodels.api as st
from scipy.stats.stats import pearsonr
import time
import scipy.stats
import matplotlib.pyplot as plt

# 删除array里重复项的函数
def deleteDuplicatedElementFromList(listA):
    # return list(set(listA))
    return sorted(set(listA), key=listA.index)
# ====================================================================================================================
# 1. 计算STD_ROA, AGE
# ====================================================================================================================
data_csv = pd.read_csv("FI_T5_3.csv")
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stock_code','Accper','Typrep','ROA'])

# print(data_csv)

# 换算年份
data_csv = np.array(data_csv)
data_temp = []
for i in data_csv:
    if(i[1].find("12/31") != -1 and i[2] == "A"):
        stk_cd, year, roa = i[0], i[1][:4], i[3]
        data_temp.append([stk_cd, year, roa])

data_csv = pd.DataFrame(data_temp, columns = ['stock_code', 'year', 'ROA'])
data_csv = data_csv.sort_values(['stock_code', 'year'], ascending=True)

stock_list = deleteDuplicatedElementFromList(list(data_csv['stock_code']))
data_stdroa = []
for stkcd in stock_list:
    # print(stkcd)
    df = data_csv[data_csv['stock_code'] == stkcd]

    if(len(df) < 5): continue

    df = np.array(df)
    for count in range(len(df)):
        if(count < 5 - 1): continue

        year = df[count][1]
        roa_list = []
        for i in range(5):
            roa_list.append(df[count - i][2])
        roa_list = np.array(roa_list)
        std_roa = roa_list.std()
        # print(stkcd, year, std_roa)
        data_stdroa.append([stkcd, year, std_roa])

data_stdroa = pd.DataFrame(data_stdroa, columns=['stock_code', 'year', 'std_roa'])

with open("TRD_Co_1.csv", 'r', encoding='gbk') as r:
    rd = csv.reader(r)
    data_temp = []
    count = 0
    for i in rd:
        count += 1
        if(count == 1): continue
        data_temp.append([int(i[0]), int(i[6][:4])])

data_temp = pd.DataFrame(data_temp, columns=['stock_code', 'listyr'])
data_stdroa = data_stdroa.merge(data_temp, on='stock_code', how='left')
data_stdroa['age'] = data_stdroa['year'].astype(float) - data_stdroa['listyr']
data_stdroa.pop('listyr')
data_stdroa = data_stdroa.astype(float)

# print(data_stdroa)

# ====================================================================================================================
# 2. 导入 NI, RET, SIZE, BM, SIGMA, LOSS数据
# ====================================================================================================================

# BM
data_csv = pd.read_csv('FI_T10_2.csv')
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stock_code', 'Rept', 'BM'])

data_csv = np.array(data_csv)
data_temp = []
for i in data_csv:
    if(i[1].find("12/31") != -1):
        stk_cd, year, bm = int(i[0]), int(i[1][:4]), i[2]
        # print(stk_cd, year, indus, lev)
        data_temp.append([stk_cd, year, bm])

data_bm = pd.DataFrame(data_temp, columns=['stock_code', 'year', 'BM'])
# print(data_bm)

# SIGMA, RET
data_csv = pd.read_csv("price_crash_result.csv")
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stock_code','year','N_week','NCSKEW','DUVOL','CRASH','RET','SIGMA','TURNOVER'])
data_csv = data_csv.dropna()
data_csv = data_csv.sort_values(['N_week'], ascending=True)

data_csv = data_csv[data_csv['N_week'] >= 30]   # 删除当年交易周少于30周的样本
data_retsigma = pd.DataFrame(data_csv, columns=['stock_code', 'year', 'RET', 'SIGMA'])
# print(data_retsigma)


# SIZE
data_csv = pd.read_csv('FS_Combas_3.csv')
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stock_code', 'Rept', 'Asset'])

data_csv = np.array(data_csv)
data_temp = []
for i in data_csv:
    if(i[1].find("12/31") != -1 and i[2] > 0):
        stk_cd, year, size = int(i[0]), int(i[1][:4]), math.log(i[2], math.e)
        # print(stk_cd, year, indus, lev)
        data_temp.append([stk_cd, year, size])

data_size = pd.DataFrame(data_temp, columns=['stock_code', 'year', 'SIZE'])
# print(data_size)


# DEARN
data_csv = pd.read_csv('FI_T8_1.csv')
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stkcd', 'Accper', 'DEARN'])
data_csv = data_csv.dropna()

data_csv = np.array(data_csv)
data_temp = []
for i in data_csv:
    if(i[1].find("12/31") != -1):
        stk_cd, year, dearn = int(i[0]), int(i[1][:4]), float(i[2])
        # print(stk_cd, year, indus, lev)
        data_temp.append([stk_cd, year, dearn])

data_dearn = pd.DataFrame(data_temp, columns=['stock_code', 'year', 'DEARN'])
data_dearn.dropna()
# print(data_dearn)


# LOSS
data_csv = pd.read_csv('FS_Comins_1.csv')
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stkcd', 'Accper', 'EARN'])
data_csv = data_csv.dropna()

data_csv = np.array(data_csv)
data_temp = []
for i in data_csv:
    if(i[1].find("12/31") != -1):
        stk_cd, year, earn = int(i[0]), int(i[1][:4]), float(i[2])
        loss = 1 if(earn <= 0) else 0
        data_temp.append([stk_cd, year, loss])
        # print([stk_cd, year, earn, loss])

data_loss = pd.DataFrame(data_temp, columns=['stock_code', 'year', 'LOSS'])
# print(data_loss)

# EARN
data_csv = pd.read_csv('FI_T5_3.csv')
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stkcd', 'Accper', 'type', 'ROA'])
data_csv = data_csv.dropna()

data_csv = np.array(data_csv)
data_temp = []
for i in data_csv:
    if(i[1].find("12/31") != -1 and i[2] == "A"):
        stk_cd, year, earn = int(i[0]), int(i[1][:4]), float(i[3])
        data_temp.append([stk_cd, year, earn])
        # print([stk_cd, year, earn, loss])

data_earn = pd.DataFrame(data_temp, columns=['stock_code', 'year', 'ROA_t'])
data_earn = data_earn.sort_values(['stock_code', 'year'], ascending=True)
# print(data_earn)

stock_list = deleteDuplicatedElementFromList(list(data_earn['stock_code']))
data_earn_1 = []
for stkcd in stock_list:
    df = data_earn[data_earn['stock_code'] == stkcd]
    df = np.array(df)
    for count in range(len(df) - 1):
        year = df[count][1]
        roa_tp1 = df[count+1][2]
        data_earn_1.append([stkcd, year, roa_tp1])

data_earn_1 = pd.DataFrame(data_earn_1, columns=['stock_code', 'year', 'ROA_t+1'])
# print(data_earn_1)


# TONE
data_csv = pd.read_csv("ar_emotion.csv")
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stock_code','year','pos','neg','all words','all char','title_freq','title_emotion'])
data_csv = data_csv.sort_values(['all char'], ascending=True)

data_csv = data_csv[data_csv['all char'] >= 20000]      # 删去字数明显不对的样本
data_csv = pd.DataFrame(data_csv, columns = ['stock_code', 'year', 'pos','neg','all words','all char'])
data_csv['NET'] = (data_csv['pos'] - data_csv['neg']) / (data_csv['pos'] + data_csv['neg'])
data_tone = pd.DataFrame(data_csv, columns= ['stock_code', 'year', 'NET'])
data_tone = data_tone.astype(float)

# print(data_tone)


# 合并
database = data_tone.merge(data_retsigma, on=['stock_code','year'], how='inner')
database = database.merge(data_size, on=['stock_code','year'], how='inner')
database = database.merge(data_dearn, on=['stock_code','year'], how='inner')
database = database.merge(data_loss, on=['stock_code','year'], how='inner')
database = database.merge(data_earn, on=['stock_code','year'], how='inner')
database = database.merge(data_bm, on=['stock_code','year'], how='inner')
database = database.merge(data_stdroa, on=['stock_code','year'], how='inner')

database_2 = database
database_2 = database.merge(data_earn_1, on=['stock_code','year'], how='inner')

print("=====================================================================================================")
print("Dataframe Initialized.", time.ctime())
print("=====================================================================================================")

# ====================================================================================================================
# 3. 计算 ABTONE
# ====================================================================================================================
database = database.dropna()

# 多元线性回归，OLS
Y = database['NET']
database.pop('NET')
X = database
X = st.add_constant(X)
model = st.OLS(Y, X).fit()

pred = model.predict()
resi = Y - pred  # 求残差
database['ABTONE'] = resi

data_abtone = pd.DataFrame(database, columns=['stock_code', 'year', 'ABTONE'])
data_abtone.to_csv("abtone_result.csv", header=1, index=0)
print(data_abtone)

# ====================================================================================================================
# 3. 计算 ABTONE_FE
# ====================================================================================================================
database_2 = database_2.dropna()

# 多元线性回归，OLS
Y = database_2['NET']
database_2.pop('NET')
X = database_2
X = st.add_constant(X)
model = st.OLS(Y, X).fit()

pred = model.predict()
resi = Y - pred  # 求残差
database_2['ABTONE_FE'] = resi

data_abtonefe = pd.DataFrame(database_2, columns=['stock_code', 'year', 'ABTONE_FE'])
data_abtone.to_csv("abtonefe_result.csv", header=1, index=0)
print(data_abtonefe)

