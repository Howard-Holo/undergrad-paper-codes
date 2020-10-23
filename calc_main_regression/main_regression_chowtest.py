import pandas as pd
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

# 拼合数据库，准备统计
db = db.merge(dummy_indus, on=['stock_code', 'year'])
db = db.merge(dummy_year, on=['stock_code', 'year'])
# db = db.merge(dummy_panel, on=['stock_code', 'year'])

db.pop('stock_code'); db.pop('year'); db.pop('INDUS')


# 按照分组依据进行分组回归
group_by = '%s' % X_variable
# group_by = 'ROA'
break_point = 0

db_c1 = db[db['%s' % group_by] < break_point]
db_c2 = db[db['%s' % group_by] >= break_point]

Y_c1 = db_c1['%s' % Y_variable].astype(float)
db_c1.pop('%s' % Y_variable)
X_c1 = db_c1.astype(float)

Y_c2 = db_c2['%s' % Y_variable].astype(float)
db_c2.pop('%s' % Y_variable)
X_c2 = db_c2.astype(float)

Y_all = db['%s' % Y_variable].astype(float)
db.pop('%s' % Y_variable)
X_all = db.astype(float)



# =====================================================================================================================
# 分组、全样本多元线性回归，计算邹检验所需参数
# =====================================================================================================================

X_c1 = st.add_constant(X_c1)
X_c1 = X_c1.astype(float)
model_c1 = st.OLS(Y_c1, X_c1).fit()

X_c2 = st.add_constant(X_c2)
X_c2 = X_c2.astype(float)
model_c2 = st.OLS(Y_c2, X_c2).fit()

X_all = X_all.astype(float)
model_all = st.OLS(Y_all, X_all).fit()

coef_c1 = np.array(model_c1.params)
k_para = len(coef_c1)
ess_all = model_all.mse_resid * model_all.df_resid
ess_c1 = model_c1.mse_resid * model_c1.df_resid
ess_c2 = model_c2.mse_resid * model_c2.df_resid
n_c1 = model_c1.nobs
n_c2 = model_c2.nobs

chow = ((ess_all - (ess_c1 + ess_c2)) / k_para) / ((ess_c1 + ess_c2) / (n_c1 + n_c2 - 2 * k_para))

cp_value = scipy.stats.f.sf(chow, (k_para), (n_c1 + n_c2 - 2 * k_para))
# p_value = scipy.stats.f.sf(0.5588, 6, 985)

print("Chow F:", chow)
print("Prob > F:", cp_value)     # 回头再看一下《横截面》那本书，仔细研究一下邹检验的原假设，以及为啥邹检验不是双尾？


# =====================================================================================================================
# 分组回归的结果输出
# =====================================================================================================================

# 导出结果 Stata-like
coef1 = np.array(model_c1.params);      coef2 = np.array(model_c2.params)
stderr1 = np.array(model_c1.bse);       stderr2 = np.array(model_c2.bse)
p_value1 = np.array(model_c1.pvalues);  p_value2 = np.array(model_c2.pvalues)
t_value1 = np.array(model_c1.tvalues);  t_value2 = np.array(model_c2.tvalues)

# variable summary
r_s1 = model_c1.rsquared;               r_s2 = model_c2.rsquared
r_sa1 = model_c1.rsquared_adj;          r_sa2 = model_c2.rsquared_adj
df_residual1 = model_c1.df_resid;       df_residual2 = model_c2.df_resid
f_statistics1 = model_c1.fvalue;        f_statistics2 = model_c2.fvalue
f_pvalue1 = model_c1.f_pvalue;          f_pvalue2 = model_c2.f_pvalue

# model summary
mse_model1 = model_c1.mse_model;        mse_model2 = model_c2.mse_model
mse_resid1 = model_c1.mse_resid;        mse_resid2 = model_c2.mse_resid
mse_total1 = model_c1.mse_total;        mse_total2 = model_c2.mse_total

df_model1 = model_c1.df_model;          df_model2 = model_c2.df_model
df_resid1 = model_c1.df_resid;          df_resid2 = model_c2.df_resid
df_total1 = df_model1 + df_resid1;      df_total2 = df_model2 + df_resid2

sse_model1 = mse_model1 * df_model1;    sse_model2 = mse_model2 * df_model2
sse_resid1 = mse_resid1 * df_resid1;    sse_resid2 = mse_resid1 * df_resid2
sse_total1 = sse_model1 + sse_resid1;    sse_total2 = sse_model2 + sse_resid2


# print(Y.name)

with open("result_regression_panel.csv", 'w', encoding='utf-8') as w:
    wt = csv.writer(w)
    X_list1 = X_c1.columns
    X_list2 = X_c2.columns

    wt.writerow(["Grouped by:", group_by,"", "Break point:", break_point])
    wt.writerow(["Chow F:", chow])
    wt.writerow(["Prob > F:", cp_value])
    wt.writerows([["F():", k_para, (n_c1 + n_c2 - 2 * k_para)],[]])

    wt.writerow(["Dep. Variable:", Y_c1.name,"","","","","","Dep. Variable:",Y_c2.name])
    wt.writerow(["No. Observations:", len(Y_c1),"","","","","","No. Observations:",len(Y_c2)])
    wt.writerow(["Df Residuals:", df_residual1,"","","","","","Df Residuals:",df_residual2])
    wt.writerow(["R-squared:", r_s1,"","","","","","R-squared:",r_s2])
    wt.writerow(["Adj. R-squared:", r_sa1,"","","","","","Adj. R-squared:",r_sa2])
    wt.writerow(["F-statistic:", f_statistics1,"","","","","","F-statistics:",f_statistics2])
    wt.writerow(["F-p value:", f_pvalue1,"","","","","","F-p value:",f_pvalue2])

    wt.writerows([[], ["Source", "SS", "df", "MS", "","","", "Source", "SS", "df", "MS"]])
    wt.writerow(["Model", sse_model1, df_model1, mse_model1,"","","", "Model", sse_model2, df_model2, mse_model2])
    wt.writerow(["Residual", sse_resid1, df_resid1, mse_resid1,"","","", "Residual", sse_resid2, df_resid2, mse_resid2])
    wt.writerow(["Total", sse_total1, df_total1, mse_total1, "","","", "Total", sse_total2, df_total2, mse_total2])

    wt.writerows([[],["Variable", "coef", "std err", "t", "P>|t|", "", "", "Variable", "coef", "std err", "t", "P>|t|"]])

    for i in range(len(X_list1)):
        wt.writerow([X_list1[i], coef1[i], stderr1[i], t_value1[i], p_value1[i],"", "", X_list2[i], coef2[i], stderr2[i], t_value2[i], p_value2[i]])

