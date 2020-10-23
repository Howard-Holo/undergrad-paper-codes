# -*- coding: utf-8 -*-

#import这五个库来实现不同功能：
from bs4 import  BeautifulSoup      #Beautifulsoup 用来处理文本
import requests                     #requests 用于请求页面信息
from lxml import etree              #etree 用于调用x-path方法获取页面信息
from bs4 import BeautifulSoup
import time                         # 用于暂停当前运行的循环，防止访问过于频繁被网站屏蔽
import csv                          # 用于csv文件的读取和写入
import shutil,os
import random

userAgentDic = {
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit %s (KHTML, like Gecko) Chrome" % round(random.uniform(0,999.99),2),
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/%s (KHTML, like Gecko) Version/5.1 Safari" % round(random.uniform(0,999.99),2),
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/%s (KHTML, like Gecko) Version/5.1 Safari" % round(random.uniform(0,999.99),2),
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

def archive_files (x, y) :
    sss = "/%s.csv" % x
    cwd = os.getcwd()
    cwa = cwd.replace(r"\\", '/')
    datd = "/%s/" % y
    srcfile = cwa + sss
    dstfile = cwa + datd + sss
    mymovefile(srcfile, dstfile)


def set_urlhead_xpath(url_head):
    # headers设置
    headers = {
        "User-Agent": random.choice(list(userAgentDic)),
        "Connection": "close",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8"
    }


    res_head = requests.get(url = url_head, headers = headers)
    res_head.encoding = 'utf-8'
    res_head_xpath = etree.HTML(res_head.content)
    return res_head_xpath
    # except:
    #     error_log_write(stock_code)       # 如果出现错误则调取函数记录状态


def error_log_write(sid, page, line):
    e_write.writerow([sid, page, line])
    time.sleep(30)


# with open("output.csv", 'w', encoding = 'utf-8') as o:
#     wt = csv.writer(o)
#     wt.writerow(["title","href","time","content"])

elog = open("error_log.csv", "w", encoding = 'utf-8')
e_write = csv.writer(elog)
with open('task_list.csv', 'r', encoding = 'utf-8') as f:
    f_csv = csv.reader(f)

    ct = -1
    for row in f_csv:
        ct += 1
        if(ct == 0): continue
        flag_over = False
        count_news = 0

        sina_code = row[0]
        total_page = 200
        print(sina_code)

        with open('%s.csv' % sina_code[2:], 'w', encoding = 'utf-8') as w:
            wt = csv.writer(w)
            wt.writerow(["title", "time", "content"])

            for i in range(int(total_page)):
                c_page = str(i + 1)

                if(flag_over == True): break

                url_list = "https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllNewsStock.php?symbol="
                url_list = url_list + sina_code + "&Page=" + c_page
                print(url_list)
                urlsettled_list = set_urlhead_xpath(url_list)
                # print(urlsettled_list)

                for line in range(50):
                    url_news_temp = urlsettled_list.xpath(
                        "/html/body/div[6]/div[2]/div[2]/table/tr[2]/td/div[1]/ul/a[%s]/@href" % (line + 1))
                    try:
                        url_news = url_news_temp[0]
                    except: break
                    print(url_news)

                    # report 类
                    if(url_news.find("stock.finance") != -1):
                        print("report")
                        urlsettled_news = set_urlhead_xpath(url_news)
                        title_temp = urlsettled_news.xpath("/html/body/div/div[3]/div[1]/div/div/h1")
                        out_title = title_temp[0].text
                        out_title = out_title.replace("　", "").replace("\n", "").replace("\t", "").replace(" ", "").replace(",", "")

                        date_temp = urlsettled_news.xpath("/html/body/div/div[3]/div[1]/div/div/div[1]/span[4]")
                        out_date = date_temp[0].text
                        out_date = out_date[3:]

                        content_temp = urlsettled_news.xpath("/html/body/div/div[3]/div[1]/div/div/div[2]/p/text()")
                        out_content = ""
                        for i in content_temp:
                            a = i.replace("　", "").replace("\n", "").replace("\t", "").replace(" ", "").replace(",", "")
                            a = "".join(a.split())
                            out_content += a

                    # news 类
                    else:
                        print("news")
                        res = requests.get(url_news)
                        res.encoding = 'utf-8'
                        try:
                            soup = BeautifulSoup(res.text, 'html.parser')
                            out_title = soup.select('.main-title')[0].text
                            out_title = out_title.replace("　", "").replace("\n", "").replace("\t", "").replace(" ", "").replace(",", "")
                        except: continue

                        try:
                            date = soup.select('.date')[0].text
                        except: continue
                        y_cut = date.find("年")
                        m_cut = date.find("月")
                        d_cut = date.find("日")
                        out_date = date[:y_cut] + "-" + date[y_cut + 1: m_cut] + "-" + date[m_cut + 1: d_cut]

                        a = soup.select('p[cms-style="font-L align-Justify subpect-abstract"]')
                        b = soup.select('p[cms-style="font-L align-Justify"]')
                        out_content = ""
                        for i in range(100):
                            try:
                                content = a[i].text
                            except:
                                break
                            content = content.replace("　", "").replace("\n", "").replace("\t", "").replace(" ", "").replace(",", "")
                            out_content += content
                        for i in range(100):
                            try:
                                content = b[i].text
                            except:
                                break
                            content = content.replace("　", "").replace("\n", "").replace("\t", "").replace(" ", "")
                            out_content += content
                        if (out_content == ""):
                            out_content = soup.select('.article')[0].text.replace("　", "").replace("\n", "").replace("\t","").replace(" ", "")

                    if(out_date[5: 7] == "04"):
                        flag_over =True
                        break

                    if (out_date[5: 7] == "06"):
                        continue

                    # print([out_title, out_date[:4], out_content])

                    wt.writerow([out_title, out_date, out_content])
                    count_news += 1




                time.sleep(random.uniform(0,1))


        archive_files('%s' % sina_code[2:], 'output')
        time.sleep(random.uniform(0,5))

elog.close()



