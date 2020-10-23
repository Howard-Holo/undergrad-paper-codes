import requests                     # requests 用于请求页面信息
from lxml import etree              # etree 用于调用x-path方法获取页面信息
import time                         # 用于暂停当前运行的循环，防止访问过于频繁被网站屏蔽
import csv                          # 用于csv文件的读取和写入
import shutil, os, random

userAgentDic = {
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit %s (KHTML, like Gecko) Chrome" % round(random.uniform(0.,999.99),2),
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/%s (KHTML, like Gecko) Version/5.1 Safari" % round(random.uniform(0.,999.99),2),
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/%s (KHTML, like Gecko) Version/5.1 Safari" % round(random.uniform(0.,999.99),2),
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.%s (KHTML, like Gecko) Chrome/17.0.963.56 Safari",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
    "UCWEB7.0.2.37/28/999",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
    "Openwave/ UCWEB7.0.2.37/28/999",
    "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999"
}


# =====================================================================================================================
# 基础输入：开始、结束年份和
# task list：所有的证券代码；file index：（）；
# start year：开始年份；end year：结束年份（倒回查询）
# =====================================================================================================================

task_list = "stock_list_new.csv"
file_index = "Annual Repo"



# =====================================================================================================================
# 改变储存途径，移动文件至指定地址
# =====================================================================================================================

# 改变储存途径
def mymovefile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        print ("%s not exist!" %(srcfile))
    else:
        fpath,fname = os.path.split(dstfile)    # 分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                # 创建路径
        shutil.move(srcfile, dstfile)      # 复制文件
        # print ("copy %s -> %s"%( srcfile,dstfile))

# 生成季报、中报、年报后移动文件至指定地址
def archive_files (x, y) :
    sss = "/%s.txt" % x
    cwd = os.getcwd()
    cwa = cwd.replace(r"\\", '/')
    datd = "/Annual Repo/%s/" % y
    srcfile = cwa + sss
    dstfile = cwa + datd + sss
    mymovefile(srcfile, dstfile)


# =====================================================================================================================
# 设置url_head
# INPUT: url(http);
# OUTPUT: res_head_xpath
# =====================================================================================================================

def error_log_write(sid):
    elog.write(sid)
    elog.write('\n')
    print(sid, "met problems.", time.ctime())
    time.sleep(30)


def set_urlhead_xpath(url_head):
    # headers设置
    headers = {
        "User-Agent": random.choice(list(userAgentDic)),
        "Connection": "close",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8"
    }

    try:
        res_head = requests.get(url = url_head, headers = headers)
        res_head.encoding = 'utf-8'
        # text_head = res_head.content
        res_head_xpath = etree.HTML(res_head.text)
        return res_head_xpath
    except:
        error_log_write(stock_code)       # 如果出现错误则调取函数记录状态


# =====================================================================================================================
# 获取网页上指定内容的xpath行数
# INPUT: 标签内容；需要用的url(settled)，主页url则是找catalog，申购状况页面url则是找sheet
# OUTPUT: str数字，xpath行数
# =====================================================================================================================

def find_label_xline(target_label, urlsetted_used, bidivert):
    for i in range(200):
        i += 1

        if(bidivert == "catalog"):
            url_temp = urlsetted_used.xpath("//*[@id='nodea%s']/nobr/a" % str(i))  # 寻找catalog url
        elif(bidivert == "sheet"):
            url_temp = urlsetted_used.xpath("/html/body/form/table[1]/tr[2]/td[3]/div[2]/table/tr[%s]/td[1]" % str(i)) # 寻找sheet url

        a = url_temp[0].text
        if (a == target_label):
            return i


# =====================================================================================================================
# 正式执行抓取指定年度之间的年报
# =====================================================================================================================

task_list = []

# 统计list中有多少个代码（任务总数）
# with open('%s' %task_list) as f:
#     sum_total = 0
#     f_csv = csv.reader(f)
#     for row in f_csv:
#         try:
#             a = row[0]
#             sum_total += 1
#         except: continue
#     print(sum_total)


elog = open("error_log.csv", "w", encoding = 'utf-8')
with open("stock_list.csv", "r", encoding = 'utf-8') as fl:    # open the file list.
    stock_list_r = csv.reader(fl)   # get and store the stock list into numpy array.

    # 记录总共的任务数量
    count_task = 0
    for l_row in stock_list_r:
        count_task += 1
    print(count_task)

with open("stock_list.csv", "r", encoding='utf-8') as fl:  # open the file list.
    stock_list_r = csv.reader(fl)  # get and store the stock list into numpy array.

    pin_task = 1
    for l_row in stock_list_r:

        start_year = 2008
        end_year = 2019


        print("=====================================================================================================================")
        print(pin_task, "/", count_task)
        pin_task += 1

        stock_code = l_row[0].replace(r"['", "").replace(r"']", "").replace('\n', "")
        print(stock_code)

        # print(stock_code, "Process STARTED.", time.ctime(), url_head)

        # 进入个股的主页
        url_head = ("http://gg.cfi.cn/%s.html" % stock_code)  # mainpage of the stock info in cfi.cn
        urlsetted_head = set_urlhead_xpath(url_head)
        if(urlsetted_head == None): continue

        xline = find_label_xline("财报全文", urlsetted_head, "catalog")
        url_repolist_temp = urlsetted_head.xpath("//*[@id='nodea%s']/nobr/a/@href" % xline)  # 寻找"财报全文"url

        # 获取中财网数据库对该股票的编码，用以拼接财务报表页面url
        findid_t = url_repolist_temp[0].find(str(stock_code))
        stock_id = url_repolist_temp[0][:findid_t - 1]
        stockid = stock_id[::-1]
        findid_t = stockid.find('/')
        stockid = stockid[:findid_t]
        stockid = stockid[::-1]

        # 获取该上市公司IPO年份
        try:
            xline = find_label_xline("申购状况", urlsetted_head, "catalog")
            url_listdate_temp = urlsetted_head.xpath("//*[@id='nodea%s']/nobr/a/@href" % xline)  # 寻找"申购状况"url

            url_head_listdate = "http://gg.cfi.cn" + url_listdate_temp[0]
            urlsetted_head_listdate = set_urlhead_xpath(url_head_listdate)
            if(urlsetted_head_listdate == None): continue


            xline = find_label_xline("上市日期", urlsetted_head_listdate, "sheet")
            list_date_temp = urlsetted_head_listdate.xpath(
                "/html/body/form/table[1]/tr[2]/td[3]/div[2]/table/tr[%s]/td[2]" % xline)  # 寻找"上市日期"
            list_date = list_date_temp[0].text
            list_year = list_date[:4]
        except:
            list_year = start_year

        # 按照要求抓取年报
        start_year = max(start_year, int(list_year))
        print("=============================================================================")
        print("STOCK CODE:", stock_code, "STOCK ID:", stockid)
        print("Start: ", start_year, "End: ", end_year, "(listed date: ", list_date, ")")
        print("=============================================================================")


        for i_year in range(start_year, end_year + 1):
            print("NOW START TASK ON DATA OF YEAR", i_year, ".", time.ctime())

            # 开启ar_out用于记录爬取结果
            file_name = "AR-" + stock_code + "-" + str(i_year)
            ar_out = open("%s.txt" % file_name, 'w', encoding='utf-8')

            url_head_repolist = "http://gg.cfi.cn/quote.aspx?stockid=" + str(stockid) + "&contenttype=cbgg&jzrq=" + str(i_year)

            # 获取需要抓取的文件行编码
            a_repo_list = []    # 记录符合要求的url
            for i in range(20):

                # 根据公告类别和主题名称，筛选年度报告并记录url
                try:
                    urlsetted_head_repolist = set_urlhead_xpath(url_head_repolist)
                except: break

                try:
                    index_name_temp = urlsetted_head_repolist.xpath(
                        "/html/body/form/table[1]/tr[2]/td[3]/div[2]/table/tr[%s]/td[2]" % str(i + 3)
                    )
                    repo_title_temp = urlsetted_head_repolist.xpath(
                        "/html/body/form/table[1]/tr[2]/td[3]/div[2]/table/tr[%s]/td[4]/a" % str(i + 3)
                    )
                    url_repo_temp = urlsetted_head_repolist.xpath(
                        "/html/body/form/table[1]/tr[2]/td[3]/div[2]/table/tr[%s]/td[4]/a/@href" % str(i + 3)
                    )
                    index_name = index_name_temp[0].text
                    repo_title = repo_title_temp[0].text
                    url_repo = url_repo_temp[0]

                    if (index_name == "年度报告"):
                        # a_repo_list.append(str(i+3))
                        a_repo_list.append(url_repo)
                        # print(index_name, repo_title, url_repo)
                        if (repo_title.find("更新") != -1 or repo_title.find("修订") != -1):
                            a_repo_list = []
                            # a_repo_list.append(str(i+3))
                            a_repo_list.append(url_repo)
                except: break

            # 获取并保存年报
            for i in a_repo_list:
                urlsetted_head_repo = set_urlhead_xpath(i)
                if(urlsetted_head_repo == None): break
                repo_scrapy_temp = urlsetted_head_repo.xpath("/html/body/table/tr[2]/td/pre/text()[3]")
                print(repo_scrapy_temp)

                repo_scrapy = repo_scrapy_temp[0]
                ar_out.write(repo_scrapy)

            ar_out.close()
            archive_files(file_name, stock_code)

elog.close()
