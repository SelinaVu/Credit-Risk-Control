
     ********************* 28/01/2023 *********************;
 ********** VARIABLE: EARNINGS MANIPULATION *********;
  *************** MADE BY DOAN TRANG **************;
   ******** Follow Tabassum et al. (2015) ********;

proc import datafile = "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\OCF_upto2024.xlsx"
 out = OCF
 dbms = xlsx
replace;
run;
proc sort data = OCF NODUPKEYS; by Ticker year; run;
data OCF; set OCF; if OCF =0 then delete; run;
proc sort data = OCF NODUPKEYS; by Ticker year; run;
proc import datafile = "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\BSupto2023_final.csv"
 out = BS
 dbms = csv
replace;
run;
proc sort data = BS NODUPKEYS; by firm year; run;
proc import datafile = "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\ISupto2023_final.csv"
 out = IS
 dbms = csv
replace;
run;
proc sort data = IS NODUPKEYS; by firm year; run;
************ OCF, Sales, Total assets ************;
data TA;
set BS;
TA = A__TOTAL_ASSETS_Consolidated;
keep firm year TA;
run;
data Sales;
set IS;
Sales = _1__Sales_Consolidated;
keep firm year Sales;
run;
data EBT;
set IS;
EBT = _16__Net_accounting_profit__loss;
keep firm year EBT;
run;
data TI;
set IS;
TI = _17__Business_income_tax_expense;
keep firm year TI;
run;
data TI_1;
set TI;
TI = (TI/-0.2);
keep firm year TI;
run;

proc sql;
create table TA_EBT_TI
as select  a.*, b.EBT, c.TI
from TA as a,EBT as b, TI_1 as c
where a.firm = b.firm = c.firm and a.year = b.year = c.year;
Quit;
Run;
Proc sort Data = TA_EBT_TI nodupkeys; BY firm year; run;

*** BTD ***;
data BTD;
set TA_EBT_TI;
BTD = (EBT-TI)/TA;
run;
PROC EXPORT DATA= BTD
 OUTFILE= "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\BTD.csv"
 DBMS=csv replace;
RUN;

************************;
proc import datafile = "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\masterdata_w_new.xlsx"
 out = Master
 dbms = xlsx
replace;
run;
proc sort data = Master NODUPKEYS; by firm year; run;
proc import datafile = "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\REM.csv"
 out = REM
 dbms = csv
replace;
run;
proc sort data = REM NODUPKEYS; by firm year; run;

proc sql;
create table Master_New
as select  a.*, b.BTD, c.REM
from Master as a,BTD as b, REM as c
where a.firm = b.firm = c.firm and a.year = b.year = c.year;
Quit;
Run;
Proc sort Data = Master_New nodupkeys; BY firm year; run;
proc sql;
create table Master_New
as select  a.*, b.RES
from Master as a,Residual as b
where a.firm = b.firm and a.year = b.year;
Quit;
Run;
Proc sort Data = Master_New nodupkeys; BY firm year; run;
PROC EXPORT DATA= Master_new
 OUTFILE= "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\masterdata_w_new2.csv"
 DBMS=csv replace;
RUN;

************************;

proc sql;
create table Sales_TA
as select  a.*, b.TA
from Sales as a,TA as b
where a.firm = b.firm and a.year=b.year;
Quit;
Run;
Proc sort Data = Sales_TA nodupkeys; BY firm year; run;
proc sql;
create table REM_B
as select  a.*, b.OCF
from Sales_TA as a, OCF as b
where a.firm = b.Ticker and a.year=b.year;
Quit;
Run;
Proc sort Data = REM_B nodupkeys; BY firm year; run;
*************** Sale(t-1), TA(t-1) **************;
data REM_B2;
set REM_B;
by firm year;
lagTA = lag(TA);
lagSales = lag(Sales);
if first.firm then lagTA=.;
if first.firm then lagSales=.;

if lagTA =. then delete;
if lagSales =. then delete;
run;
************** CFO/LagTA, Sales/lagTA, delta(Sales)/lagTA **************;
data REM_B3;
set REM_B2;
Y= (OCF*1000000000)/lagTA; *******OCF dang don vi la ty dong nen nhan 1 ty de dua ve dong********;
X1= Sales/lagTA;
X2= (Sales-lagSales)/lagTA;
run;

************** CFO/LagTA, Sales/lagTA, delta(Sales)/lagTA **************;
data RES;
set btd;
Y= BTD;
X1= TA;
run;
*** chay hoi quy lay phan du REM***;
proc reg data= REM_B3 outest=test;
model Y = X1 X2;
output out=E
residual=r
predicted=p
stdr=st_r;
quit;
run;
*** chay hoi quy lay phan du BTD***;
proc reg data= RES outest=test;
model Y = X1;
output out=E
residual=r
predicted=p
stdr=st_r;
quit;
run;
data REM;
set E;
REM = r*(-1);*******Real Earnings Management*******; /*6403 obs*/;
keep firm year REM;
run;
Proc sort Data = REM nodupkeys; BY firm year; run;  *******REM_2 la xoa OCF = 0 roi ******;

data RESidual;
set E;
RES = r;
keep firm year RES;
run;
Proc sort Data = RESidual nodupkeys; BY firm year; run;

*********************** REM_2_fixed_2 add them nam 2011 vao file OCF *************************;
PROC EXPORT DATA= REM
 OUTFILE= "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\REM.csv"
 DBMS=csv replace;
RUN;
