import pandas as pd
import numpy as np
import statsmodels.api as sm
import csv
import multiprocessing

# 删除array里重复项的函数
def deleteDuplicatedElementFromList(listA):
    # return list(set(listA))
    return sorted(set(listA), key=listA.index)

data_csv = pd.read_csv('disc_accrual_data.csv')
dataset = data_csv.values   # 获得csv的值

db = pd.DataFrame(dataset, columns = ['1','stock_code', 'year_t', 'indus_code', 'sale_t', 'ni_t', 'AR_t', 'PPE_t', 'TA_t', 'CFO_t'])
db = db.drop(columns = ['1'])

# 计算TA_t-1, d_AR_t, d_sale_t
da = np.array(db)
# print(len(db))

TA_temp, d_AR_temp, d_sale_temp = [], [], []

# 国泰安的数据还算比较工整，就不做排序了
for line in range(len(da)):
    if(line == len(da) - 1):
        TA_temp.append(None)
        d_AR_temp.append(None)
        d_sale_temp.append(None)
        break
    if(da[line + 1][1] - da[line][1] != -1):
        TA_tn1 = None
        d_AR_t = None
        d_sale_t = None
    else:
        TA_tn1 = da[line + 1][7]
        d_AR_t = da[line][5] - da[line + 1][5]
        d_sale_t = da[line][3] - da[line + 1][3]
    TA_temp.append(TA_tn1)
    d_AR_temp.append(d_AR_t)
    d_sale_temp.append(d_sale_t)

db['TA_t-1'] = TA_temp
db['d_AR_t'] = d_AR_temp
db['d_sale_t'] = d_sale_temp

# db.to_csv("temp.csv", index=True)   # 将df输出到csv文件，输出顺序为dataframe默认的列名顺序


# 逐年逐市场进行回归计算，并保存结果至新dataframe
#
year_list = list(db['year_t'])
year_list = sorted(deleteDuplicatedElementFromList(year_list))
indus_list = list(db['indus_code'])
indus_list = sorted(deleteDuplicatedElementFromList(indus_list))
#
# print(year_list)
# print(indus_list)
#
#
# 'stock_code', 'year_t', 'indus_code', 'sale_t', 'ni_t', 'AR_t', 'PPE_t', 'TA_t', 'CFO_t', TA_t-1, d_AR_t, d_sale_t


with open("disc_accrual_result.csv", 'w', encoding='utf-8') as w:
    wt = csv.writer(w)
    wt.writerow(["stock_code", "year", "ACCM"])

    for year_t in year_list:
        if (year_t == 2009): continue
        for indus_t in indus_list:
            data_out = []  # stkcd, year_t, residual_it

            data_temp = db[db['year_t'] == year_t]
            data_temp = data_temp[data_temp['indus_code'] == indus_t]

            # print(data_temp)

            data_temp = np.array(data_temp)

            data_used = []
            for line in data_temp:
                stkcd = line[0]
                y_t = line[1]
                TACC_t = line[4] - line[8]
                ASSET_tn1 = line[9]
                d_SALE_t = line[11]
                d_REC_t = line[10]
                PPE_t = line[6]

                if (ASSET_tn1 == 0): continue

                X_TACC_t = TACC_t / ASSET_tn1
                X_ASSET_t = 1 / ASSET_tn1
                X_SR_t = (d_SALE_t - d_REC_t) / ASSET_tn1
                X_PPE_t = PPE_t / ASSET_tn1

                data_used.append([stkcd, y_t, X_TACC_t, X_ASSET_t, X_SR_t, X_PPE_t])

            # 查看样本量是否足够，如果不够则退出
            count = 0
            for i in data_used:
                count += 1
            if (count <= 5): continue

            data_used = pd.DataFrame(data_used,
                                     columns=['stkcd', 'year_t', 'X_TACC_t', 'X_ASSET_t', 'X_SR_t', 'X_PPE_t'])
            data_used = data_used.dropna()
            # print(data_used)

            # 多元线性回归，OLS
            X = data_used[['X_ASSET_t', 'X_SR_t', 'X_PPE_t']]
            X = sm.add_constant(X)
            Y = data_used['X_TACC_t']
            model = sm.OLS(Y, X).fit()
            pred = model.predict()  # 使用模型预测

            # print(pred)

            resi = data_used['X_TACC_t'] - pred  # 求残差
            data_used["residual_it"] = resi

            # print(data_used)

            data_used = np.array(data_used)
            count = 0
            for line in data_used:
                data_out.append([int(line[0]), int(line[1]), line[6]])
                count += 1
            print(year_t, indus_t, count)
            wt.writerows(data_out)

