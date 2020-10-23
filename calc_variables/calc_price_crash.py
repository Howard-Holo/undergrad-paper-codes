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
# df_mkttype: 证券代码，市场类型
# df_wkm：市场类型，交易周编号，周市场收益率（含股利，流通加权）
# df_wkt：证券代码，交易周编号，周开盘日，周收盘日，周个股收益率（含股利，流通加权）
# 全部以交易周编号升序排列
# ====================================================================================================================

# 获取stock_code和market_type参数
data_csv = pd.read_csv('TRD_Co_1.csv')
data_csv = data_csv.dropna()  # 滤除缺失数据
dataset = data_csv.values   # 获得csv的值
df_open = pd.DataFrame(dataset, columns=['Stkcd','Stknme','Conme','Nnindcd','Nnindnme','Estbdt','Listdt','Statco','Markettype'])
df_mkttype = pd.DataFrame(df_open, columns=['Stkcd', 'Markettype'])

# 将所需周市场回报率数据写入内存
# Markettype, Trdwnt, Wretwdeq, Wretmdeq, Wretwdos, Wretmdos, Wretwdtl, Wretmdtl
data_csv = pd.read_csv('TRD_Weekm_1.csv')
data_csv = data_csv.dropna()  # 滤除缺失数据
dataset = data_csv.values   # 获得csv的值
df_open = pd.DataFrame(dataset, columns=['Markettype','Trdwnt','Wretwdeq','Wretmdeq','Wretwdos','Wretmdos','Wretwdtl','Wretmdtl'])
df_wkm = pd.DataFrame(df_open, columns=['Markettype', 'Trdwnt', 'Wretwdos'])
df_wkm = df_wkm.sort_values(['Trdwnt'], ascending=True)

# 将所需个股市场回报率数据写入内存。个股文件原始数据有两个，懒得写os file list的for循环形式了。
# Stkcd, Trdwnt, Opndt, Clsdt, Wnshrtrd, Wnvaltrd, Wsmvosd, Wretwd, Wretnd
data_csv = pd.read_csv('TRD_Week_1.csv')
data_csv = data_csv.dropna()  # 滤除缺失数据
dataset = data_csv.values   # 获得csv的值
df_open = pd.DataFrame(dataset, columns=['Stkcd','Trdwnt','Opndt','Clsdt','Wnshrtrd','Wnvaltrd','Wsmvosd','Wretwd','Wretnd'])
df_wkt1 = pd.DataFrame(df_open, columns=['Stkcd','Trdwnt','Opndt','Clsdt','Wretwd'])

data_csv = pd.read_csv('TRD_Week_2.csv')
data_csv = data_csv.dropna()  # 滤除缺失数据
dataset = data_csv.values   # 获得csv的值
df_open = pd.DataFrame(dataset, columns=['Stkcd','Trdwnt','Opndt','Clsdt','Wnshrtrd','Wnvaltrd','Wsmvosd','Wretwd','Wretnd'])
df_wkt2 = pd.DataFrame(df_open, columns=['Stkcd','Trdwnt','Opndt','Clsdt','Wretwd'])

df_wkt = df_wkt1
df_wkt = df_wkt.append(df_wkt2, ignore_index=True)
df_wkt1, df_wkt2, df_open = [], [], []      # release memory
df_wkt = df_wkt.sort_values(['Stkcd', 'Trdwnt'], ascending=True)

# 将周换手率数据写入内存。
# Stkcd,Trdwnt,W_turnover
data_csv = pd.read_csv('Wturnover_result.csv')
data_csv = data_csv.dropna()  # 滤除缺失数据
dataset = data_csv.values   # 获得csv的值
df_turn = pd.DataFrame(dataset, columns=['Stkcd','Trdwnt','W_turnover'])
df_turn = df_turn.sort_values(['Stkcd', 'Trdwnt'], ascending=True)

# 将年报披露日期写入内存。
# Stkcd, Reptyp, Accper, Annodt, Annowk
data_csv = pd.read_csv('IAR_Rept_1.csv')
data_csv = data_csv.dropna()  # 滤除缺失数据
dataset = data_csv.values   # 获得csv的值
df_open = pd.DataFrame(dataset, columns=['Stkcd', 'Reptyp', 'Accper', 'Annodt', 'Annowk'])
df_rept = pd.DataFrame(df_open, columns=['Stkcd','Reptyp','Annodt'])
df_rept = df_rept.sort_values(['Stkcd', 'Annodt'], ascending=True)
df_open = []            # release memory


print("=====================================================================================================")
print("Dataframe Initialized.", time.ctime())
print("=====================================================================================================")


# ====================================================================================================================
# 程序计算部分
# ====================================================================================================================

def calculate_risk_rev(stkcd, tws, twe):
    # ======================================================================================================
    # step 1 利用stock_code筛选所需数据
    # db_frame_stk: Stkcd, Trdwnt, W_turnover, Wretwd, Wretwdos
    # ======================================================================================================

    # 获取市场类型和市场周收益率数据
    db_mkt = df_mkttype[df_mkttype['Stkcd'] == stkcd]
    db_mkt = np.array(db_mkt)
    mkt = db_mkt[0][1]
    db_wkm = df_wkm[df_wkm['Markettype'] == mkt]
    db_wkm.pop('Markettype')

    # 从数据表里获取当前证券的信息
    db_wkt = df_wkt[df_wkt['Stkcd'] == stkcd]
    db_wkt.pop('Stkcd'), db_wkt.pop('Opndt'), db_wkt.pop('Clsdt')   # 删除不需要的列（卸磨杀阿米驴）
    db_turn = df_turn[df_turn['Stkcd'] == stkcd]

    # print("db_wkm")
    # print(db_wkm)
    # print("db_wkt")
    # print(db_wkt)
    # print("db_turn")
    # print(db_turn)

    db_frame = db_turn.merge(db_wkt, left_on="Trdwnt", right_on="Trdwnt", how='left')
    db_frame = db_frame.merge(db_wkm, left_on="Trdwnt", right_on="Trdwnt", how='left')
    # print(db_frame)

    db_frame = np.array(db_frame)

    db_mkt, db_wkt, db_wkm, db_turn = [], [], [], []        # release memory

    # ======================================================================================================
    # 在数表里寻找起始周和结束周对应的行数
    # ======================================================================================================
    count = len(db_frame)
    start_line = 0
    endline = 0
    for line in db_frame:
        if (line[1] == tws): start_line = endline
        if (line[1] == twe): break
        endline += 1

    # print(tws, twe, count, start_line, endline)

    if (start_line == 0): return None, None, None, None, None, None, None  # 之前已经用同样的数表判断过了，如果还没找到只可能是缺省值。
    if (endline == count):  # 如果计量区间末端处在股票停牌区间，则顺延到下一开盘周，如果顺延的开盘周跨年则删除该样本。
        alternative_line = 0
        for line in db_frame:
            if (int(line[1][:4]) == int(tws[:4]) + 1):
                endline = alternative_line
                break
            alternative_line += 1
        # if(alternative_line == count - 1): return None, None, None
        if (endline == count - 1):
            endline -= 1

    if (endline - start_line < 10): return None, None, None, None, None, None, None  # 如果计量区间内交易周数过少也不能算入。

    if (endline >= count - 1):
        endline = count - 2

    # print(count, start_line, endline)

    # ======================================================================================================
    # 制作回归使用的dataframe，准备进行回归。
    # R_it, R_mt-2, R_mt-1, R_mt, R_mt+1, R_mt+2, Wtnr_it
    # ======================================================================================================

    db_forcalc = []
    for line in range(start_line, endline + 1):
        wk_it = db_frame[line][1]
        Wtnr_it = db_frame[line][2]
        R_it = db_frame[line][3]
        R_mt_n2 = db_frame[line - 2][4]
        R_mt_n1 = db_frame[line - 1][4]
        R_mt_n  = db_frame[line    ][4]
        R_mt_p1 = db_frame[line - 1][4]
        R_mt_p2 = db_frame[line - 2][4]

        # print(wk_it, R_it, R_mt_n2, R_mt_n1, R_mt_n, R_mt_p1, R_mt_p2, Wtnr_it)
        db_forcalc.append([R_it, R_mt_n2, R_mt_n1, R_mt_n, R_mt_p1, R_mt_p2, Wtnr_it])

    N_week = len(db_forcalc)
    db_forcalc = pd.DataFrame(db_forcalc, columns=['R_it', 'R_mt-2', 'R_mt-1', 'R_mt', 'R_mt+1', 'R_mt+2', 'Wtnr_it'])
    db_forcalc = db_forcalc.dropna()
    # print(db_forcalc)

    TURN_it = db_forcalc['Wtnr_it'].mean()   # 个股年平均周换手率即可算出
    RE_it = db_forcalc['R_it'].mean()        # 个股年平均持有收益率
    SIGMA_it = db_forcalc['R_it'].std()      # 个股年平均持有收益率的标准差

    # ======================================================================================================
    # 多元线性回归，OLS，计算W_it
    # ======================================================================================================
    X = np.array(db_forcalc[['R_mt-2', 'R_mt-1', 'R_mt', 'R_mt+1', 'R_mt+2']])
    X = st.add_constant(X)          # 需要常数项
    Y = np.array(db_forcalc['R_it'])
    model = st.OLS(Y, X).fit()
    # coef = model.params     # 参数
    pred = model.predict()          # 使用模型预测

    resi = db_forcalc['R_it'] - pred        # 求残差
    db_forcalc["residual_it"] = resi
    db_forcalc["W_it"] = 0
    db_forcalc["RE_it"] = RE_it

    # print(db_forcalc)

    # 计算W_it
    db_forcalc = np.array(db_forcalc)  # 'R_it', 'R_mt-2', 'R_mt-1', 'R_mt', 'R_mt+1', 'R_mt+2', 'Wtnr_it', 'residual_it', 'W_it', 'RE_it'
    for db_line in db_forcalc:
        # print(db_line)
        try:
            db_line[8] = math.log(db_line[7] + 1, math.e)
        except: return None, None, None, None, None, None, None

    # ======================================================================================================
    # step 3 计算NCSKEW，DUVOL, CRASH哑变量
    # ======================================================================================================

    N_week = endline - start_line
    ncsk_2 = 0
    ncsk_3 = 0
    N_up = 0
    N_down = 0
    duv_up = 0
    duv_down = 0

    W_for_dum = []
    for db_line in db_forcalc:
        W_it = db_line[8]
        W_for_dum.append(W_it)

        ncsk_2 += math.pow(W_it, 2)
        ncsk_3 += math.pow(W_it, 3)

        if (db_line[0] >= db_line[9]):
            N_up += 1
            duv_up += math.pow(W_it, 2)
        else:
            N_down += 1
            duv_down += math.pow(W_it, 2)

    NCSKEW_iT = - (N_week * math.pow(N_week - 1, 3 / 2) * ncsk_3) / (
                (N_week - 1) * (N_week - 2) * math.pow(ncsk_2, 3 / 2))
    duvol = ((N_up - 1) * duv_down) / (
            (N_down - 1) * duv_up)
    DUVOL_iT = math.log(duvol, math.e)

    W_for_dum = np.array(W_for_dum)
    mean_W = W_for_dum.mean()
    std_W = W_for_dum.std()
    CRASH_iT = 0
    for W_i in W_for_dum:
        if (W_i <= mean_W + Z_ppf * std_W):
            CRASH_iT = 1
            break

    # return N_week, RE_it, SIGMA_it, TURN_it
    return N_week, NCSKEW_iT, DUVOL_iT, CRASH_iT, RE_it, SIGMA_it, TURN_it


# ====================================================================================================================
# 按年度判断起止时间所属交易周编号判定，并调动计算函数
# ====================================================================================================================

def working_program(stk):
    # 从数据表里获取当前证券的信息
    df_caledr = df_wkt[(df_wkt['Stkcd'] == stk)]
    df_caledr = np.array(df_caledr)
    df_rept_stk = df_rept[df_rept['Stkcd'] == stk]
    df_rept_stk = np.array(df_rept_stk)

    data_out = []
    err_log = []

    for rept_line in df_rept_stk:
        year_t = rept_line[2][:4]
        anno_date_s = change_date_form(rept_line[2])
        anno_date_e = anno_date_s + 10000
        anno_date = [anno_date_s, anno_date_e]

        # 计算起始日和结束日所对应的交易周编号
        if (anno_date_s >= 20190101): continue  # 2019年的数据是需要2019～2020年的行情，显然现在搞不到
        # print(stk, anno_date_s, anno_date_e)

        trade_week = ["", ""]
        for ic in range(2):  # 0是寻找起始日所在周的代码，1是寻找结束日所在周的代码
            trade_week_last, w_end_last = "2000-00", 20000101  # 缺省数据

            for cale_line in df_caledr:
                w_start = change_date_form(cale_line[2])
                w_end = change_date_form(cale_line[3])

                flag = 0
                if (w_start <= anno_date[ic] and anno_date[ic] <= w_end):
                    flag = 1
                    continue
                if (flag == 1):  # 因为这里计算的是年报披露之后1年滚动时间内的数据。因此时间指针要顺移一位（结束周就比较随意）
                    trade_week[ic] = cale_line[1]
                    break

                if (w_end_last < anno_date[ic] and anno_date[ic] < w_start):  # 如果没有找到，则是在交易周之间
                    if (w_start - w_end_last >= 10000):  # 如果这一条记录与上一条跨年了，上一条可能是停牌前最后一个交易日
                        trade_week[ic] = trade_week_last
                    else:  # 正常情况，则从下周开始
                        trade_week[ic] = cale_line[1]
                    break

                w_end_last = w_end
                trade_week_last = cale_line[1]

        trade_week_s, trade_week_e = trade_week
        # print(trade_week_s, trade_week_e)

        # 调取计算函数

        try:
            # print(calculate_risk_rev(stk, trade_week_s, trade_week_e))
            n_wk, nc, du, cr, re, sig, tr = calculate_risk_rev(stk, trade_week_s, trade_week_e)  # 计算股价崩盘指标，和个股收益率指标
            data_out.append([stk, year_t, n_wk, nc, du, cr, re, sig, tr])

        except:
            err_log.append(stk)
            continue
        #
        # break
        #

    # 每一个个股数据计算完成，则数据与状态输出，防止串行
    with open("price_crash_result.csv", 'a', encoding='utf-8') as rw:
        res_w = csv.writer(rw)
        res_w.writerows(data_out)

    with open("error_log.csv", 'a', encoding='utf-8') as rw:
        wt = csv.writer(rw)
        for i in err_log:
            wt.writerow([i])











# ====================================================================================================================
# 程序主控部分
# ====================================================================================================================

# 制作一个证券代码表，按照证券代码进行计算（以减少查表时间）
stock_list = np.array(df_rept['Stkcd'])
stock_list = list(stock_list)
stock_list = deleteDuplicatedElementFromList(stock_list)

# 给输出部分写数据库关键字
with open("price_crash_result.csv", 'w', encoding='utf-8') as rw:
    res_w = csv.writer(rw)
    res_w.writerow(["stock_code", "Year", "N_week", "NCSKEW", "DUVOL", "CRASH", "RE", "SIGMA", "TURNOVER"])

with open("error_log.csv", 'w', encoding='utf-8') as rw:
    w = csv.writer(rw)

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
