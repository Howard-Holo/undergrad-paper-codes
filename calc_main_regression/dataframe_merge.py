import csv
import math
import pandas as pd
import numpy as np
import statsmodels.api as st
from scipy.stats.stats import pearsonr
import time
import scipy.stats
import matplotlib.pyplot as plt

Z_ppf = scipy.stats.norm.ppf(0.001)

w_up = 1
w_down = 100 - w_up
def pearson_aca(df):
    result_corr = []
    result_pvalue = []
    result_tvalue = []
    reslut_tstar = []
    for i in range(df.shape[1]):
        for j in range(df.shape[1]):
            m = pearsonr(df.iloc[:, i], df.iloc[:, j])

            # t-test
            n = df.shape[0]
            r = round(m[0], 10)
            t_star = ""

            if (abs(r) != float(1)):
                tr = abs(r) * math.sqrt(n - 2) / math.sqrt(1 - r * r)
                c_star = 0
                a = [0.1, 0.05, 0.01]
                for ai in a:
                    li = scipy.stats.t.ppf(1 - ai / 2, n - 2)
                    if (tr >= li):
                        c_star += 1
                for k in range(c_star):
                    t_star = t_star + "*"

                result_tvalue.append(round(tr, 2))
            else:
                tr = ""
                result_tvalue.append("")

            result_corr.append(round(r, 4))
            result_pvalue.append(round(m[1], 2))
            reslut_tstar.append(t_star)

    # 制表输出
    # list_out = []
    #
    # list_out_title = [""]
    # for i in list_df: list_out_title.append(i)
    # list_out.append(list_out_title)
    #
    # for i in range(df.shape[1]):
    #     list_out_line = []
    #     # list_out_line.append(list_df[i])
    #     for j in range(df.shape[1]):
    #         k = i * df.shape[1] + j
    #         list_out_line.append(result_corr[k])
    #         # print(list_df[i], "-", list_df[j], ":", result_corr[k], reslut_tstar[k])
    #     # print(list_out_line)
    #     list_out.append(list_out_line)
    #
    # count = 0
    # for i in list_out:
    #     print('%s \t' % list_out_title[count], end="")
    #     for j in i:
    #         # print(j)
    #         print('%s \t' % j, end="")
    #     count += 1
    #     print("")

    with open("result_pearson.csv", 'w', encoding='utf-8') as pr:
        list_df = list(df)
        wt = csv.writer(pr)
        tp = ['', '']
        for i in list_df: tp.append(i)
        wt.writerow(tp)
        list_ins = ["Pearson", "t value", "p value"]
        for i in range(df.shape[1]):
            # 写Pearson相关系数及星星
            tp = []
            tp.append(list_df[i])
            tp.append("Pearson")
            for j in range(df.shape[1]):
                k = i * df.shape[1] + j
                tp.append(str(result_corr[k]) + reslut_tstar[k])
            wt.writerow(tp)

            # 写t值
            tp = []
            tp.append("")
            tp.append("t value")
            for j in range(df.shape[1]):
                k = i * df.shape[1] + j
                tp.append(str(result_tvalue[k]))
            wt.writerow(tp)

            # 写p值
            tp = []
            tp.append("")
            tp.append("p value")
            for j in range(df.shape[1]):
                k = i * df.shape[1] + j
                tp.append(str(result_pvalue[k]))
            wt.writerow(tp)

    with open("result_pearson2.csv", 'w', encoding='utf-8') as pr:
        list_df = list(df)
        wt = csv.writer(pr)
        tp = ['']
        for i in list_df: tp.append(i)
        wt.writerow(tp)
        for i in range(df.shape[1]):
            # 写Pearson相关系数及星星
            tp = []
            tp.append(list_df[i])
            for j in range(df.shape[1]):
                k = i * df.shape[1] + j
                tp.append(str(result_corr[k]) + reslut_tstar[k])
            wt.writerow(tp)

def winsorize_df(index_name, df):
    df_temp = pd.DataFrame(df, columns=['stock_code', 'year', '%s' % index_name])   # 数据库格式一定要整齐！！！！
    # winsorize处理
    v = df_temp['%s' % index_name].dropna()
    v_up, v_down = np.percentile(v, w_up), np.percentile(v, w_down)
    df_temp = df_temp[df_temp['%s' % index_name].between(v_up, v_down)]
    return df_temp

# ====================================================================================================================
# dataframe construction
# data required: stock_code, year, indus_code, Tone, crash, analyst, turnover, sigma, ret, asset, bm, lev, roa, accm, hold
# input files: IAR_Rept_1.csv, TRD_Co_1.csv, FS_Combas_2.csv
# output file: disc_accrual_data.csv
# output: stock_code, indus_code, year, ASSET_t, AR_t, PPE_t, CFO_t, SALE_t, NI_t
# ====================================================================================================================


# ====================================================================================================================
# 1. 处理TONE
# ====================================================================================================================
data_csv = pd.read_csv("ar_emotion.csv")
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stock_code','year','pos','neg','all words','all char','title_freq','title_emotion'])
data_csv = data_csv.sort_values(['all char'], ascending=True)

# df = data_csv[data_csv['all words'] == 0]


# 删去字数明显不对的样本（约1000个）
data_csv = data_csv[data_csv['all char'] >= 20000]
data_csv = pd.DataFrame(data_csv, columns = ['stock_code', 'year', 'pos','neg','all words','all char'])

data_csv['NET'] = (data_csv['pos'] - data_csv['neg']) / (data_csv['pos'] + data_csv['neg'])
# data_csv['POSR'] = (data_csv['pos']) / (data_csv['pos'] + data_csv['neg'])
# data_csv['NEGR'] = (data_csv['neg']) / (data_csv['pos'] + data_csv['neg'])
#
data_tone = winsorize_df('NET', data_csv)
data_tone = data_tone.dropna()

# 对TONE进行一些实证操作
# des = data_csv[['NET', 'POSR', "NEGR", "all words", "all char"]]
#
# print(des)
#
# pearson_aca(des)

# print(data_tone.describe())

# a = df_tone['NET'].dropna()
# aa = np.percentile(a, 1)
# ab = np.percentile(a, 99)
# print(aa, ab)
#
#
# ====================================================================================================================
# 2. 处理与股价有关的变量：NCSKEW, DUVOL, CRASH, RET, SIGMA, TURNOVER
# ====================================================================================================================
data_csv = pd.read_csv("price_crash_result.csv")
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stock_code','year','N_week','NCSKEW','DUVOL','CRASH','RET','SIGMA','TURNOVER'])
data_csv = data_csv.dropna()
data_csv = data_csv.sort_values(['N_week'], ascending=True)

# 删除当年交易周少于30周的样本 23784 - 23057
data_csv = data_csv[data_csv['N_week'] >= 30]
# print(data_csv)

df_ncskew = winsorize_df('NCSKEW', data_csv)
df_duvol = winsorize_df('DUVOL', data_csv)
df_ret = winsorize_df('RET', data_csv)
df_sigma = winsorize_df('SIGMA', data_csv)
df_turn = winsorize_df('TURNOVER', data_csv)

# print(df_turn.describe())

# df_ncskew = df_ncskew.sort_values(['stock_code', 'year'], ascending=True)
df_ncskew['year'] = df_ncskew['year'] - 1
df_duvol['year'] = df_duvol['year'] - 1      # year是用来回归编号的
df_ncskew.rename(columns={'NCSKEW':'NCSKEW_t+1'}, inplace=True)
df_duvol.rename(columns={'DUVOL':'DUVOL_t+1'}, inplace=True)



# print(df_ncskew)

# data_price = df_duvol.merge(df_ret, on=['stock_code','year'], how='inner')
data_price = df_ncskew.merge(df_ret, on=['stock_code','year'], how='inner')

data_price = data_price.merge(df_sigma, on=['stock_code','year'], how='inner')
data_price = data_price.merge(df_turn, on=['stock_code','year'], how='inner')
# print(data_price)

# 画个直方图看下数据分布
# a = np.array(df_price['NCSKEW'])
# plt.hist(a, 1000)
# plt.show()


# ====================================================================================================================
# 3. 处理盈余管理变量：ACCM
# ====================================================================================================================
data_csv = pd.read_csv("disc_accrual_result.csv")
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stock_code','year','ACCM'])
data_csv = data_csv.dropna()
data_csv = data_csv.sort_values(['ACCM'], ascending=True)

# winsorize处理
data_da = winsorize_df('ACCM', data_csv)
data_da = data_da.sort_values(['stock_code', 'year'], ascending=True)
# print(data_da.describe())


# ====================================================================================================================
# 4. 处理股东集中度变量：HOLD
# ====================================================================================================================
data_csv = pd.read_csv('HLD_CR_1.csv')
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stock_code', 'Rept', "HOLD", 'Shrcr2','Shrcr3','Shrz'])
data_csv = np.array(data_csv)

data_temp = []
for i in data_csv:
    if(i[1].find("12/31") != -1):
        stk_cd, year, hold = int(i[0]), int(i[1][:4]), i[2] / 100       # 国泰安里的股东集中度变量单位是 %
        data_temp.append([stk_cd, year, hold])

data_temp = np.array(data_temp)
data_hold = pd.DataFrame(data_temp, columns=['stock_code', 'year', 'HOLD'])

# print(data_hold)


# ====================================================================================================================
# 5. 处理资产负债率数据，补充行业代码：LEV, INDUS
# ====================================================================================================================
data_csv = pd.read_csv('FI_T1_1.csv')
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stock_code', 'Rept', "Typrep", 'Indcd','LEV'])

data_csv = np.array(data_csv)
data_temp = []
for i in data_csv:
    if(i[1].find("12/31") != -1 and i[2] == "A"):
        stk_cd, year, indus, lev = int(i[0]), int(i[1][:4]), i[3], i[4]

        if(1/lev - 1 <= 0): continue    # 所有者权益为负的就算了吧 lev = L / A

        indus = indus if (indus[0] == "C") else indus[:2]
        # print(stk_cd, year, indus, lev)
        data_temp.append([stk_cd, year, indus, lev])

data_temp = pd.DataFrame(data_temp, columns=['stock_code', 'year', 'INDUS', 'LEV'])
data_indus = pd.DataFrame(data_temp, columns=['stock_code', 'year', 'INDUS'])
data_lev = winsorize_df('LEV', data_temp)
# print(data_lev)


# ====================================================================================================================
# 6. 处理ROA数据，此处使用资产平均额：ROA
# ====================================================================================================================
data_csv = pd.read_csv('FI_T5_2.csv')
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['stock_code', 'Rept', "Typrep", 'ROA'])

data_csv = np.array(data_csv)
data_temp = []
for i in data_csv:
    if(i[1].find("12/31") != -1 and i[2] == "A"):
        stk_cd, year, roa = int(i[0]), int(i[1][:4]), i[3]
        # print(stk_cd, year, indus, lev)
        data_temp.append([stk_cd, year, roa])

data_temp = pd.DataFrame(data_temp, columns=['stock_code', 'year', 'ROA'])
data_roa = winsorize_df('ROA', data_temp)


# ====================================================================================================================
# 7. 处理账市率(book to market)数据，此处使用A?：BM
# ====================================================================================================================
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

data_temp = pd.DataFrame(data_temp, columns=['stock_code', 'year', 'BM'])
data_bm = winsorize_df('BM', data_temp)

# print(data_bm)


# ====================================================================================================================
# 8. 处理公司规模数据：SIZE
# ====================================================================================================================
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

data_temp = pd.DataFrame(data_temp, columns=['stock_code', 'year', 'SIZE'])
data_size = winsorize_df('SIZE', data_temp)

# print(data_size)


# ====================================================================================================================
# 8. 处理分析师相关数据：OPTIMISM, ANALYST
# ====================================================================================================================
# data_csv = pd.read_csv('analyst_result.csv')
# data_csv = data_csv.values
# data_csv = pd.DataFrame(data_csv, columns=['stock_code','year','Analyst','Optimism'])
#
# # 样本清理，删除当年关注分析师团队少于5的样本
# data_csv = data_csv.dropna()
# data_csv = data_csv[data_csv['Analyst'] >= 5]
# data_csv = data_csv[(data_csv['year'] >= 2010) & (data_csv['year'] <= 2018)]
# data_csv = data_csv.sort_values(['stock_code', 'year'], ascending=True)
# print(data_csv)
#
# print(data_csv.describe())



# ====================================================================================================================
# 9. 合并数据表
# ====================================================================================================================

database = data_tone.merge(data_price, on=['stock_code','year'], how='inner')
database = database.merge(data_indus, on=['stock_code','year'], how='inner')
database = database.merge(data_da, on=['stock_code','year'], how='inner')
database = database.merge(data_hold, on=['stock_code','year'], how='inner')
database = database.merge(data_lev, on=['stock_code','year'], how='inner')
database = database.merge(data_roa, on=['stock_code','year'], how='inner')
database = database.merge(data_bm, on=['stock_code','year'], how='inner')
database = database.merge(data_size, on=['stock_code','year'], how='inner')

database = database.dropna()
database = database.sort_values(['stock_code', 'year'], ascending=True)

print(database)

database.to_csv("regression_input.csv", header=1, index=0)


# print(data_da.describe())





