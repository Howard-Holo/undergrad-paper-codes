# python 3.7 with Anaconda Environment

import pandas as pd
import sklearn
import numpy as np
import math
import statsmodels.api as st
from scipy.stats.stats import pearsonr
import scipy.stats
import csv

# =====================================================================================================================
# 数据预处理
# =====================================================================================================================

data_csv = pd.read_csv('db.csv')
data_csv = data_csv.dropna()  # 滤除缺失数据
dataset = data_csv.values   # 获得csv的值

db = pd.DataFrame(dataset, columns = ['date', 'open', 'high', 'low', 'close'])

db.date = db.date / 1000 / 1000

print(db)

print(db.describe())

print(db.corr(method='pearson'))


# =====================================================================================================================
# 多元线性回归，OLS
# 最好转成numpy进行操作，下一个version不支持pandas
# =====================================================================================================================


# X = np.array(db[['open', 'high', 'low', 'close']])
# X = db[['open', 'high', 'low', 'close']]
# X = st.add_constant(X)
# Y = np.array(db['date'])
# model = st.OLS(Y, X).fit()
# print(model.summary())


# =====================================================================================================================
# 自制Pearson检验，包括Pearson，T-test，P-value
# 不包含数据清洗
# Input: pandas dataframe
# Output: a csv displaying Pearson correlation with academic format
# =====================================================================================================================

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

            if (r != 1):
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
    # for i in range(df.shape[1]):
    #     for j in range(df.shape[1]):
    #         k = i * df.shape[1] + j
    #         print(i, "-", j, ":", result_corr[k], reslut_tstar[k], "t value:", result_tvalue[k], "p value:",
    #               result_pvalue[k])

    with open("Pearson Result.csv", 'w', encoding='utf-8') as pr:
        wt = csv.writer(pr)
        tp = ['', '']
        for i in list(df): tp.append(i)
        wt.writerow(tp)
        list_df = list(df)
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

temp_df = pd.DataFrame(db, columns = ["date", "open"])
pearson_aca(temp_df)

# =====================================================================================================================
# TEST

# for columns in db:
#     print(columns)

# print(db.shape[0], db.shape[1]) # 0:rows 1:columns



# 2SLS
# from statsmodels.sandbox.regression.gmm import IV2SLS
# resultIV = IV2SLS(dietdummy['Log Income'], dietdummy.drop(['Log Income', 'Diabetes']),
# dietdummy.drop(['Log Income', 'Reads Nutri')

