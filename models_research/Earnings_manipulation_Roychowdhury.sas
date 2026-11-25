********************* 29/10/2024 *********************;
 ********** VARIABLE: EARNINGS MANIPULATION *********;
  *************** MADE BY DOAN TRANG **************;
   ******** Follow Roychowdhury (2006) ********;

*************************************************************************;
*****************************    COGS   *********************************;
*************************************************************************;
proc import datafile = "E:\NGHIENCUUKHOAHOC\NCKHSV_2022\DATA\bs_final.csv"
 out = BS
 dbms = csv;
run;
proc sort data = BS NODUPKEYS; by firm year; run;
proc import datafile = "E:\NGHIENCUUKHOAHOC\NCKHSV_2022\DATA\is_final.csv"
 out = IS
 dbms = csv;
run;
proc sort data = IS NODUPKEYS; by firm year; run;
************ COGS, Sales, Total assets ************;
data TA;
set BS;
TA = A__TOTAL_ASSETS_Consolidated;
keep firm year TA;
run;
data Sales;
set IS;
Sales = _1__Sales_Consolidated;
COGS = _4__Cost_of_sales_Consolidated;
keep firm year Sales COGS;
run;
proc sql;
create table REM_B
as select  a.*, b.TA
from Sales as a,TA as b
where a.firm = b.firm and a.year=b.year;
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
************** COGS/LagTA, Sales/lagTA **************;
data REM_B3;
set REM_B2;
Y= COGS/lagTA;
X1= Sales/lagTA;
run;
*** chay hoi quy lay phan du ***;
proc reg data= REM_B3 outest=test;
model Y = X1;
output out=E
residual=r
predicted=p
stdr=st_r;
quit;
run;
data REM;
set E;
REM = r*(-1);*******Real Earnings Management*******;   /*6986 obs*/;
keep firm year REM;
run;
Proc sort Data = REM nodupkeys; BY firm year; run;
PROC EXPORT DATA= REM
 OUTFILE= "E:\NGHIENCUUKHOAHOC\NCKHSV_2023\RESULT\REM_2_COGS.csv"
 DBMS=csv replace;
RUN;

*************************************************************************;
***************************   DELTA INV    ******************************;
*************************************************************************;
proc import datafile = "E:\NGHIENCUUKHOAHOC\NCKHSV_2022\DATA\bs_final.csv"
 out = BS
 dbms = csv;
run;
proc sort data = BS NODUPKEYS; by firm year; run;
proc import datafile = "E:\NGHIENCUUKHOAHOC\NCKHSV_2022\DATA\is_final.csv"
 out = IS
 dbms = csv;
run;
proc sort data = IS NODUPKEYS; by firm year; run;
************ INV, Sales, Total assets ************;
data TA;
set BS;
TA = A__TOTAL_ASSETS_Consolidated;
INV = _4_1__Inventories_Consolidated;
keep firm year TA INV;
run;
data Sales;
set IS;
Sales = _1__Sales_Consolidated;
keep firm year Sales;
run;
proc sql;
create table REM_B
as select  a.*, b.TA, b.INV
from Sales as a,TA as b
where a.firm = b.firm and a.year=b.year;
Quit;
Run;
Proc sort Data = REM_B nodupkeys; BY firm year; run;
*************** Sale(t-1), TA(t-1) **************;

data REM_B2;
set REM_B;
by firm year;
lagTA = lag(TA);
lagINV = lag(INV);
lagSales = lag(Sales);


if first.firm then lagTA=.;
if first.firm then lagINV=.;
if first.firm then lagSales=.;

if lagTA =. then delete;
if lagINV =. then delete;
if lagSales =. then delete;

run;


data REM_B2;
set REM_B2;
by firm year;
delta_Sales = Sales-lagSales;
run;
data REM_B2;
set REM_B2;
by firm year;
lagdelta_Sales = lag(delta_Sales);
if first.firm then lagdelta_Sales=.;
if lagdelta_Sales =. then delete;
run;

************** deltaINV/LagTA, deltaSales/lagTA, lagdelta(Sales)/lagTA **************;
data REM_B3;
set REM_B2;
Y= (INV-lagINV)/lagTA;
X1= delta_Sales/lagTA;
X2= lagdelta_Sales/lagTA;
run;
*** chay hoi quy lay phan du ***;
proc reg data= REM_B3 outest=test;
model Y = X1 X2;
output out=E
residual=r
predicted=p
stdr=st_r;
quit;
run;
data REM;
set E;
REM = r*(-1);*******Real Earnings Management*******;    *6408 obs*/;
keep firm year REM;
run;
Proc sort Data = REM nodupkeys; BY firm year; run;
PROC EXPORT DATA= REM
 OUTFILE= "E:\NGHIENCUUKHOAHOC\NCKHSV_2023\RESULT\REM_2_deltaINV.csv"
 DBMS=csv replace;
RUN;

*************************************************************************;
*****************************   PROD   **********************************;
*************************************************************************;
proc import datafile = "E:\NGHIENCUUKHOAHOC\NCKHSV_2022\DATA\bs_final.csv"
 out = BS
 dbms = csv;
run;
proc sort data = BS NODUPKEYS; by firm year; run;
proc import datafile = "E:\NGHIENCUUKHOAHOC\NCKHSV_2022\DATA\is_final.csv"
 out = IS
 dbms = csv;
run;
proc sort data = IS NODUPKEYS; by firm year; run;
************ INV, Sales, Total assets ************;
data TA;
set BS;
TA = A__TOTAL_ASSETS_Consolidated;
INV = _4_1__Inventories_Consolidated;
keep firm year TA INV;
run;
data Sales;
set IS;
Sales = _1__Sales_Consolidated;
COGS = _4__Cost_of_sales_Consolidated;
keep firm year Sales COGS;
run;
proc sql;
create table REM_B
as select  a.*, b.TA, b.INV
from Sales as a,TA as b
where a.firm = b.firm and a.year=b.year;
Quit;
Run;
Proc sort Data = REM_B nodupkeys; BY firm year; run;
*************** Sale(t-1), TA(t-1) **************;

data REM_B2;
set REM_B;
by firm year;
lagTA = lag(TA);
lagINV = lag(INV);
lagSales = lag(Sales);


if first.firm then lagTA=.;
if first.firm then lagINV=.;
if first.firm then lagSales=.;

if lagTA =. then delete;
if lagINV =. then delete;
if lagSales =. then delete;

run;


data REM_B2;
set REM_B2;
by firm year;
delta_Sales = Sales-lagSales;
delta_INV = INV-lagINV;
run;
data REM_B2;
set REM_B2;
by firm year;
lagdelta_Sales = lag(delta_Sales);
if first.firm then lagdelta_Sales=.;
if lagdelta_Sales =. then delete;
run;

************** PROD/LagTA, Sales/lagTA, deltaSales/lagTA, lagdeltaSales/lagTA **************;
data REM_B3;
set REM_B2;
Y= (COGS + delta_INV)/lagTA;    /*PROD=COGS+deltaINV*/;
X1= Sales/lagTA;
X2= delta_Sales/lagTA;
X3= lagdelta_Sales/lagTA;
run;
*** chay hoi quy lay phan du ***;
proc reg data= REM_B3 outest=test;
model Y = X1 X2 X3;
output out=E
residual=r
predicted=p
stdr=st_r;
quit;
run;
data REM;
set E;
REM = r;*******Real Earnings Management, ko nhan -1 nhu CFO va DISEXP *******; /*6408 obs*/;
keep firm year REM;
run;
Proc sort Data = REM nodupkeys; BY firm year; run;
PROC EXPORT DATA= REM
 OUTFILE= "E:\NGHIENCUUKHOAHOC\NCKHSV_2023\RESULT\REM_2_PROD.csv"
 DBMS=csv replace;
RUN;

*************************************************************************;
*****************************   DISEXP   **********************************;
*************************************************************************;
proc import datafile = "E:\NGHIENCUUKHOAHOC\NCKHSV_2022\DATA\bs_final.csv"
 out = BS
 dbms = csv;
run;
proc sort data = BS NODUPKEYS; by firm year; run;
proc import datafile = "E:\NGHIENCUUKHOAHOC\NCKHSV_2022\DATA\is_final.csv"
 out = IS
 dbms = csv;
run;
proc sort data = IS NODUPKEYS; by firm year; run;
************  Sales, Total assets ************;
data TA;
set BS;
TA = A__TOTAL_ASSETS_Consolidated;
RD = _1_8__Investment_and_development;
keep firm year TA RD;
run;
data Sales;
set IS;
Sales = _1__Sales_Consolidated;
SGA = _9__Selling_expenses_Consolidate + _10__General_and_admin_expenses_;
keep firm year Sales SGA;
run;
proc sql;
create table REM_B
as select  a.*, b.TA, b.RD
from Sales as a,TA as b
where a.firm = b.firm and a.year=b.year;
Quit;
Run;
Proc sort Data = REM_B nodupkeys; BY firm year; run;

*************** Sale(t-1), TA(t-1) **************;
data REM_B;
set REM_B;
by firm year;
DISEXP = SGA + RD;
run;

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
************** COGS/LagTA, Sales/lagTA **************;
data REM_B3;
set REM_B2;
Y= DISEXP/lagTA;
X1= lagSales/lagTA;
run;
*** chay hoi quy lay phan du ***;
proc reg data= REM_B3 outest=test;
model Y = X1;
output out=E
residual=r
predicted=p
stdr=st_r;
quit;
run;
data REM;
set E;
REM = r*(-1);*******Real Earnings Management*******;   /*6986 obs*/;
keep firm year REM;
run;
Proc sort Data = REM nodupkeys; BY firm year; run;
PROC EXPORT DATA= REM
 OUTFILE= "E:\NGHIENCUUKHOAHOC\NCKHSV_2023\RESULT\REM_2_DISEXP.csv"
 DBMS=csv replace;
RUN;
