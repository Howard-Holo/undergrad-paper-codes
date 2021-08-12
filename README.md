# undergrad-paper-codes
本仓库收录了我的毕业论文所使用的全部代码。
毕业论文题目《年报文本语气能预示股价崩盘风险吗？——基于 A 股上市公司年报的文本挖掘》。已被本科生毕业论文相关文献库收录，因此您可以查阅论文的正文。

论文选取了 2010 年至 2018 年 A 股所有上市公司的年报及市场价格信息为研究样本，并对样本进行了如下的筛选：（1）删除了因爬虫软件提取有误而导致文本长度过短（中文字数少于 20000 个字）的年报样本；（2）删除所有者权益小于等于零的样本；（3）删除年报公布后 1 年内交易周数少于 30 的样本；（4）删除相关数据缺失的样本；（5）删除相关数据无法计算的样本；（6）对所有的样本进行上下 1% 的缩尾。本文最终获得了 18203 个包括了 3350 家上市公司年报的样本作为对假设一进行实证检验的样本集，获得了 11687 个包括了 2375 家上市公司年报的样本作为对假设二的样本集。上述两个样本集样本总数的差异是在对下文中公式（5）进行计算时相关数据缺失导致的。

论文的年报文本数据来源于中财网（ http://www.cfi.cn ）本文运用 python 编程进行爬虫获取该网站上所有可获取的年报文本数据，进行数据清洗格式调整，并只保留其中的中文字符，而后通过 python jieba 库对年报文本信息进行分析。本文的公司财务数据、股票交易数据和年报审计数据等均来自 CSMAR 国泰安数据库。


This repository collects all codes used for my graduation paper, "Can the tone of the annual report predict the risk of stock price collapse? -- text mining based on the annual reports of A-share listed companies." This paper has been stored in relevant academic database of undergraduate graduation paper, so I post the paper for reference. 

This paper selects the annual reports and market price information of all A-share listed companies from 2010 to 2018 as research samples. and the samples are screened as follows: (1) delete the samples of the annual report whose text length is too short (the number of Chinese characters is less than 20000 words) due to the error extracted by scrapy codes; (2) delete the samples whose owner's equity is less than or equal to zero; (3) delete the samples with less than 30 trading weeks in one year after the publication of the annual report. (4) delete the samples with missing relevant data; (5) delete the samples that cannot be calculated by the relevant data; and (6) reduce the tail of all the samples by 1%. 

In this paper, 18203 samples including 3350 listed companies' annual reports are obtained as the sample set for empirical testing of hypothesis 1, and 11687 samples including 2375 listed companies' annual reports are obtained as the sample set for hypothesis 2. The difference in the total number of samples between the two sample sets is caused by the lack of relevant data when calculating formula (5) mentioned in paper. 

The annual report text data of the paper comes from China Finance Info (http://www.cfi.cn). This paper uses python programming to obtain all the available annual report text data on the website, adjusts the data cleaning format, and retains only the Chinese characters, and then analyzes the annual report text information through the python jieba library. 
The company financial data, stock trading data and annual report audit data in this paper are all from CSMAR database (a.k.a. GUO TAI AN).
