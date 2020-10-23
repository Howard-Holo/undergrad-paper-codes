import csv
import math
import pandas as pd
import numpy as np
import statsmodels.api as st
import time
import scipy.stats
import multiprocessing

Z_ppf = scipy.stats.norm.ppf(0.001)

# 删除array里重复项的函数
def deleteDuplicatedElementFromList(listA):
    # return list(set(listA))
    return sorted(set(listA), key=listA.index)

# 为判定时间先后，对日期str进行重新编码
def change_date_form(da):
    if(da.find("/") != -1):
        sp = da.split("/")
    else:
        sp = da.split("-")
    y, m, d = sp[:3]
    if(len(m) != 2): m = "0" + m
    if(len(d) != 2): d = "0" + d
    return int(y + m + d)

# ====================================================================================================================
# 搭建基础数据库
# ====================================================================================================================
data_csv = pd.read_csv("IAR_Rept_1.csv")
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['Stkcd','Reptyp','Accper','Annodt','Annowk'])
data_csv = data_csv.sort_values(['Stkcd', 'Annodt'], ascending=True)
data_csv.pop('Reptyp')
data_csv.pop('Annowk')
data_csv.pop('Accper')

df_temp = np.array(data_csv)
data_csv = []

# print(df_temp)

# 制作报告期间对照表
df_rept = []

for i in range(len(df_temp)):
    stkcd = df_temp[i][0]
    year = int(df_temp[i][1][:4])
    start_day = change_date_form(df_temp[i][1])
    if(i != len(df_temp) - 1):
        end_day = change_date_form(df_temp[i+1][1]) if(stkcd == df_temp[i+1][0]) else 20201231
    else:
        end_day = 20201231
    df_rept.append([stkcd, year, start_day, end_day])
    # print([stkcd, year, start_day, end_day])

df_rept = pd.DataFrame(df_rept, columns=['Stkcd','year','s_date','e_date'])

# 将分析师文件写入内存
data_csv = pd.read_csv("AF_Bench_1.csv")
data_csv = data_csv.values
data_csv = pd.DataFrame(data_csv, columns=['Stkcd','Rptdt','Fenddt','AnanmID','ForecastAccuracy','ForecastOptimism'])

data_csv2 = pd.read_csv("AF_Bench_2.csv")
data_csv2 = data_csv2.values
data_csv2 = pd.DataFrame(data_csv2, columns=['Stkcd','Rptdt','Fenddt','AnanmID','ForecastAccuracy','ForecastOptimism'])

df_ana = data_csv.append(data_csv2, ignore_index=True)
data_csv, data_csv2 = [], []      # release memory
df_ana = df_ana.sort_values(['Stkcd', 'Rptdt'], ascending=True)

print("=====================================================================================================")
print("Dataframe Initialized.", time.ctime())
print("=====================================================================================================")


# ====================================================================================================================
# 按照证券代码逐个执行
# ====================================================================================================================

def working_program(stk):

    data_out = []

    # 从数据表里获取当前证券的信息
    df_ana_stk = df_ana[(df_ana['Stkcd'] == stk)]
    df_rept_stk = df_rept[df_rept['Stkcd'] == stk]

    # 判定所属的年份
    df_ana1 = np.array(df_ana_stk)
    df_rept_stk = np.array(df_rept_stk)
    year_list = []
    for line in df_ana1:
        rpt = change_date_form(line[1])

        year = int(rpt/10000)
        for l_rept in df_rept_stk:
            if((int(l_rept[2]) <= rpt) and (rpt < int(l_rept[3]))):
                # print(rpt, l_rept[2], l_rept[3])
                year = l_rept[1]
                break
        # print([stk, rpt, year])
        year_list.append(year)
    df_temp = np.array(year_list); df_ana_stk['year'] = df_temp
    df_ana_stk.pop('Rptdt')
    year_list = deleteDuplicatedElementFromList(year_list)
    # print(year_list)

    # 逐年计算当年分析师追踪人数，和平均OPTIMISM数据
    for year in year_list:
        df_ana_stk_yr = df_ana_stk[df_ana_stk['year'] == year]

        # 计算当年全部分析师追踪人数
        df_analy_id = df_ana_stk_yr['AnanmID']
        df_analy_id = list(df_analy_id)
        df_analy_id = deleteDuplicatedElementFromList(df_analy_id)
        ANALYST_t = len(df_analy_id)

        # 计算当年预测的乐观倾向，是FO > 0 占当年的比例
        df_ana_stk_yr = df_ana_stk_yr.dropna(subset=['ForecastOptimism'])
        opt_d = len(df_ana_stk_yr)
        df_temp = df_ana_stk_yr[df_ana_stk_yr['ForecastOptimism'] > 0]
        opt_n = len(df_temp)
        OPTIMISM_t = (opt_n / opt_d) if (opt_d != 0) else None
        data_out.append([stk, year, ANALYST_t, OPTIMISM_t])
        # print(stk, year, ANALYST_t, opt_n, opt_d)


    # 每一个个股数据计算完成，则数据与状态输出，防止串行
    with open("analyst_result.csv", 'a', encoding='utf-8') as rw:
        res_w = csv.writer(rw)
        res_w.writerows(data_out)

    # with open("error_log.csv", 'a', encoding='utf-8') as rw:
    #     wt = csv.writer(rw)
    #     for i in err_log:
    #         wt.writerow([i])

# working_program(1)


# ====================================================================================================================
# 程序主控部分
# ====================================================================================================================

# 制作一个证券代码表，按照证券代码进行计算（以减少查表时间）
stock_list = np.array(df_rept['Stkcd'])
stock_list = list(stock_list)
stock_list = deleteDuplicatedElementFromList(stock_list)

# 给输出部分写数据库关键字
with open("analyst_result.csv", 'w', encoding='utf-8') as rw:
    res_w = csv.writer(rw)
    res_w.writerow(["stock_code", "year", "Analyst", "Optimism"])

# with open("error_log.csv", 'w', encoding='utf-8') as rw:
#     w = csv.writer(rw)

# 执行多少个证券，同时开多少个进程
num_process = int(multiprocessing.cpu_count()/2)   # CPU有几个核就同步作业几个进程。不然就成了"一核有难，八核围观"
num_totaltask = len(stock_list)
# num_totaltask = 100

# 进程调度函数，顺带做了起止时间所属交易周编号判定
def launch_process(x):
    count = 0
    for i in range(x - 1 , num_totaltask , num_process) :
        count += 1
        print("Process No.", x, "On", stock_list[i], count, " / ", int(num_totaltask/num_process), time.ctime())
        working_program(stock_list[i])

# 主程序。开启并行进程。
ts = []
for j in range(1, num_process + 1):
    t = multiprocessing.Process(target=launch_process, args=(j,))  # 创建第j个进程，进程启动函数是launch_process
    # t.daemon = True
    t.start()  # 执行第j个进程
    ts.append(t)  # ts用来防并发撞车
for t in ts:
    t.join()  # 为所有进程进行"防撞车"处理

