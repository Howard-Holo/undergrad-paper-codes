/// hausman检验
import delimited /Users/exusiai/PycharmProjects/untitled/regression_input.csv
rename net tone
xtset indus
xtset year
xtreg ncskew_t1 tone ret sigma turnover accm hold lev roa bm size opinion auditor, fe 
esti store FE1
xtreg ncskew_t1 tone ret sigma turnover accm hold lev roa bm size opinion auditor, re 
esti store RE1
hausman FE1 RE1, constant sigmaless


/// 日常复读机操作
import delimited /Users/exusiai/PycharmProjects/untitled/regression_input.csv
encode indus, gen(industry)
xtset industry
xtreg duvol_t1 abtone_fe ret sigma overturn accm hold lev roa bm size opinion auditor i.year, fe vce(cluster industry year) nonest 
summarize duvol_t1 abtone_fe ret sigma overturn accm hold lev roa bm size opinion auditor


/// 存文件, summarize
sysuse auto
asdoc sum, detail
asdoc sum, detail save(Summary stats.doc)

/// 存文件，correlation
asdoc pwcorr tone abtone_fe abtone ncskew_t1 duvol_t1 ret sigma overturn accm hold lev roa bm size opinion auditor, star(all) nonum replace save(test.doc)

/// 存文件，regression
//nest replace, nest append分别是I/O w和a
asdoc xtreg duvol_t1 abtone_fe ret sigma overturn accm hold lev roa bm size opinion auditor i.year, fe vce(cluster industry year) nonest, save(test.doc)

/// Ha
asdoc xtreg ncskew_t1 tone ret sigma overturn accm hold lev roa bm size opinion auditor i.year, fe vce(cluster industry year) nonest, save(test.doc) nest replace
asdoc xtreg duvol_t1 tone ret sigma overturn accm hold lev roa bm size opinion auditor i.year, fe vce(cluster industry year) nonest, save(test.doc) nest append

/// Hb
asdoc xtreg ncskew_t1 tone ret sigma overturn accm hold lev roa bm size opinion auditor i.year if abtone>=0, fe vce(cluster industry year) nonest, save(test.doc) nest replace
asdoc xtreg ncskew_t1 tone ret sigma overturn accm hold lev roa bm size opinion auditor i.year if abtone<0, fe vce(cluster industry year) nonest, save(test.doc) nest append
asdoc xtreg duvol_t1 tone ret sigma overturn accm hold lev roa bm size opinion auditor i.year if abtone>=0, fe vce(cluster industry year) nonest, save(test.doc) nest append
asdoc xtreg duvol_t1 tone ret sigma overturn accm hold lev roa bm size opinion auditor i.year if abtone<0, fe vce(cluster industry year) nonest, save(test.doc) nest append
