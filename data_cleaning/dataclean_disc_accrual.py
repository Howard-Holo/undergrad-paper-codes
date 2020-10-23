import csv
import math
import pandas as pd
import numpy as np
import statsmodels.api as st
import time


# ====================================================================================================================
# discretionary accrual measurement - data cleaning
# input files: IAR_Rept_1.csv, TRD_Co_1.csv, FS_Combas_2.csv
# output file: disc_accrual_data.csv
# output: stock_code, indus_code, year, ASSET_t, AR_t, PPE_t, CFO_t, SALE_t, NI_t
# ====================================================================================================================

# step 1. 使用 stock_code 获取 indus_code 参数，存为数组
with open("TRD_Co_1.csv", 'r', encoding='gbk') as r:
    # Stkcd, Stknme, Conme, Nnindcd, Nnindnme, Estbdt, Listdt, Statco, Markettype
    rd = csv.reader(r)

    indus_sheet = []
    count = -1
    for i in rd:
        count += 1
        if (count == 0): continue

        # # 如果是制造业（C）则取两位数字，其他行业取第一位数字。
        # incd = i[3] if (i[3][0] == "C") else i[3][:2]

        # 如果是制造业（C）则取两位字符，其他行业取一位字符。
        incd = i[3][:2] if (i[3][0] == "C") else i[3][0]

        indus_sheet.append([i[0],incd])
#
# for i in indus_sheet:
#     if( == i[0]): print(i[1])

# step 2. 获取利润表里的数据
with open("FS_Comins_2.csv", 'r', encoding='utf-8') as r:
# Stkcd, Accper, Typrep, Revenue, Net Income
    rd = csv.reader(r)
    count = 0

    ins_temp = []
    last_code = '0'
    indu_code = '0'
    for i in rd:
        count += 1

        # 获取行业代码
        if(i[0] != last_code):
            for j in indus_sheet:
                if(i[0] == j[0]): indu_code = j[1]

        if (i[1].find("12/31") != -1):  # 确保拿到的都是年报数据
            sale_t = None if (i[3] == "") else float(i[3])
            ni_t = None if (i[4] == "") else float(i[4])
            year_t = i[1][:4]
            stock_code = i[0]
            ins_temp.append([stock_code, year_t, indu_code, sale_t, ni_t])

        # if (count >= 1000): break
print("Income Statement Finished.", time.ctime())


# step 3. 获取资产负债表里的数据
with open("FS_Combas_2.csv", 'r', encoding='utf-8') as r:
# Stkcd, Accper, Typrep, Account Receivable, PPE, TOTAL ASSET
    rd = csv.reader(r)
    count = 0
    bs_temp = []

    for i in rd:
        count += 1

        if (i[1].find("12/31") != -1):  # 确保拿到的都是年报数据
            AR_t = None if (i[3] == "") else float(i[3])
            PPE_t = None if (i[4] == "") else float(i[4])
            TA_t = None if (i[5] == "") else float(i[5])
            year_t = i[1][:4]
            stock_code = i[0]
            bs_temp.append([stock_code, year_t, AR_t, PPE_t, TA_t])

        # if (count >= 1000): break
print("Balance Sheet Finished.", time.ctime())


# step 4. 获取现金流量表里的数据
with open("FS_Comscfd_2.csv", 'r', encoding='utf-8') as r:
# Stkcd, Accper, Typrep, CFO
    rd = csv.reader(r)
    count = 0
    cfs_temp = []
    for i in rd:
        count += 1

        if (i[1].find("12/31") != -1):  # 确保拿到的都是年报数据
            CFO_t = None if (i[3] == "") else float(i[3])
            year_t = i[1][:4]
            stock_code = i[0]
            cfs_temp.append([stock_code, year_t, CFO_t])
        # if (count >= 1000): break
print("Cash Flow Statement Finished.", time.ctime())


# step 5. 拼接
# bs_temp = np.array(bs_temp)

# print(cfs_temp)
df_ins = pd.DataFrame(ins_temp, columns= ['stock_code', 'year_t', 'indus_code', 'sale_t', 'ni_t'])
df_bs = pd.DataFrame(bs_temp, columns= ['stock_code', 'year_t', 'AR_t', 'PPE_t', 'TA_t'])
df_cfs = pd.DataFrame(cfs_temp, columns= ['stock_code', 'year_t', 'CFO_t'])
# print(df_ins)
# print(df_bs)
# print(df_cfs)

df_temp_1  = pd.merge(df_ins, df_bs, on=['stock_code','year_t'],how='outer')
df_out = pd.merge(df_temp_1, df_cfs, on=['stock_code','year_t'],how='outer')
array_out = np.array(df_out)

# print(array_out)

df_out.to_csv("disc_accrual_data.csv", index=True)   # 将df输出到csv文件，输出顺序为dataframe默认的列名顺序
