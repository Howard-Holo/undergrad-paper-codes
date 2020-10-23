# python 3.7 with Anaconda Environment

import pandas as pd
import sklearn
import numpy as np
import math
import statsmodels.api as st
from scipy.stats.stats import pearsonr
from statsmodels.stats.outliers_influence import variance_inflation_factor
import scipy.stats
import csv

# Y_variable = 'DUVOL_t+1'
# Y_variable = 'NCSKEW_t+1'
Y_variable = 'CRASH_t+1'


X_variable = 'ABTONE'
# X_variable = 'ABTONE_FE'
# X_variable = 'NET'


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

            if (abs(r) != 1):
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


def checkVIF(df):
    df['const'] = 1
    df = df.astype(float)
    name = df.columns
    x = np.matrix(df)
    VIF_list = [variance_inflation_factor(x,i) for i in range(x.shape[1])]
    VIF = pd.DataFrame({'feature' : name, "VIF": VIF_list})
    VIF.to_csv("result_VIF.csv")
    # print(VIF)


# =====================================================================================================================
# 数据预处理
# =====================================================================================================================

data_csv = pd.read_csv('regression_input.csv')
data_csv = data_csv.dropna()  # 滤除缺失数据
dataset = data_csv.values   # 获得csv的值

db = pd.DataFrame(dataset, columns = ['stock_code','year','%s' % X_variable,'%s' % Y_variable,'RET','SIGMA','TURNOVER','INDUS','ACCM','HOLD','LEV','ROA','BM','SIZE'])

# 制作行业哑变量
dummy_indus = pd.get_dummies(db['INDUS'], prefix='indus')
dummy_indus['stock_code'] = db['stock_code']
dummy_indus['year'] = db['year']

# 制作年份哑变量
dummy_year = pd.get_dummies(db['year'], prefix='year')
dummy_year['stock_code'] = db['stock_code']
dummy_year['year'] = db['year']

# 制作年报超额语气哑变量（ABTONE > 0?）
dummy_panel = pd.DataFrame(db['stock_code'], columns= ['stock_code'])
dummy_panel['year'] = db['year']
df_temp = []
for i in np.array(db['%s' % X_variable]):
    if(i > 0): df_temp.append(1)
    else: df_temp.append(0)

dummy_panel['pos_abtone'] = df_temp




# 拼合数据库，准备统计
db = db.merge(dummy_indus, on=['stock_code', 'year'])
db = db.merge(dummy_year, on=['stock_code', 'year'])
db = db.merge(dummy_panel, on=['stock_code', 'year'])
# db.pop('%s' % X_variable)
#
#
# 分组
db = db[db['pos_abtone'] == 0]
db.pop('pos_abtone')



for i in db:
    print(i)


# =====================================================================================================================
# 描述统计, Pearson, VIF
# =====================================================================================================================

des = db[['%s' % Y_variable,'%s' % X_variable,'RET','SIGMA','TURNOVER','ACCM','HOLD','LEV','ROA','BM','SIZE']]
# des = db[['%s' % Y_variable,'pos_abtone','RET','SIGMA','TURNOVER','ACCM','HOLD','LEV','ROA','BM','SIZE']]
name_list = des.columns

# v_up, v_down = np.percentile(v, w_up), np.percentile(v, w_down)

# print(name_list)
descript = []
for v in name_list:
    v_list = np.array(des['%s' % v])
    v_n = len(v_list)
    v_mean = v_list.mean()
    v_std = v_list.std()
    v_1p = np.percentile(v_list, 1)
    v_25p = np.percentile(v_list, 25)
    v_50p = np.percentile(v_list, 50)
    v_75p = np.percentile(v_list, 75)
    v_99p = np.percentile(v_list, 99)

    descript.append([v, v_n, v_mean, v_50p, v_std, v_1p, v_25p, v_75p, v_99p])

descript = pd.DataFrame(descript, columns=['Variable', 'Sample Size', 'Mean', 'Middle', 'Std.', '1%', '25%', '75%', '99%'])
descript.to_csv("result_description.csv")

pearson_aca(des)
checkVIF(des)



# print(Y)
# print(X)


# =====================================================================================================================
# 多元线性回归，OLS
# =====================================================================================================================

Y = db['%s' % Y_variable].astype(float)
X = db
X.pop('stock_code'); X.pop('year'); X.pop('INDUS'); X.pop('%s' % Y_variable)
X = st.add_constant(X)
X = X.astype(float)

model = st.OLS(Y, X).fit()
# coef = model.coef()
# t = model.t()
print(model.summary())

# print(dir(model))


# 导出结果 Stata-like
coef = np.array(model.params)
stderr = np.array(model.bse)
p_value = np.array(model.pvalues)
t_value = np.array(model.tvalues)

# variable summary
r_s = model.rsquared
r_sa = model.rsquared_adj
df_residual = model.df_resid
f_statistics = model.fvalue
f_pvalue = model.f_pvalue

# model summary
mse_model = model.mse_model
mse_resid = model.mse_resid
mse_total = model.mse_total

df_model = model.df_model
df_resid = model.df_resid
df_total = df_model + df_resid

sse_model = mse_model * df_model
sse_resid = mse_resid * df_resid
sse_total = sse_model + sse_resid


# print(Y.name)

with open("result_regression.csv", 'w', encoding='utf-8') as w:
    wt = csv.writer(w)
    X_list = X.columns

    wt.writerow(["Dep. Variable:", Y.name])
    wt.writerow(["No. Observations:", len(Y)])
    wt.writerow(["Df Residuals:", df_residual])
    wt.writerow(["R-squared:", r_s])
    wt.writerow(["Adj. R-squared:", r_sa])
    wt.writerow(["F-statistic:", f_statistics])
    wt.writerow(["F-p value:", f_pvalue])

    wt.writerows([[], ["Source", "SS", "df", "MS"]])
    wt.writerow(["Model", sse_model, df_model, mse_model])
    wt.writerow(["Residual", sse_resid, df_resid, mse_resid])
    wt.writerow(["Total", sse_total, df_total, mse_total])

    wt.writerows([[],["Variable", "coef", "std err", "t", "P>|t|"]])

    for i in range(len(X_list)):
        wt.writerow([X_list[i], coef[i], stderr[i], t_value[i], p_value[i]])

