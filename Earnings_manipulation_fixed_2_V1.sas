
     ********************* 28/01/2023 (Updated 24/06/2026) *********************;
 ********** VARIABLE: EARNINGS MANIPULATION *********;
  *************** MADE BY DOAN TRANG **************;
   ******** Follow Tabassum et al. (2015) ********;

/* =========================================================================
   BƯỚC 1: IMPORT DỮ LIỆU ĐẦU VÀO
   ========================================================================= */

proc import datafile = "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\OCF_upto2024.xlsx"
 out = OCF
 dbms = xlsx
 replace;
run;
proc sort data = OCF NODUPKEYS; by Ticker year; run;
data OCF; set OCF; if OCF = 0 then delete; run;
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


/* =========================================================================
   BƯỚC 2: TÍNH TOÁN BTD (BOOK-TAX DIFFERENCES)
   ========================================================================= */

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

/* SỬA LỖI: Điều kiện JOIN chuẩn hóa (tránh sử dụng so sánh nối tiếp a = b = c) */
proc sql;
create table TA_EBT_TI as 
 select a.*, b.EBT, c.TI
 from TA as a
 join EBT as b on a.firm = b.firm and a.year = b.year
 join TI_1 as c on a.firm = c.firm and a.year = c.year;
Quit;
Run;
Proc sort Data = TA_EBT_TI nodupkeys; BY firm year; run;

data BTD;
 set TA_EBT_TI;
 BTD = (EBT-TI)/TA;
run;

PROC EXPORT DATA= BTD
 OUTFILE= "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\BTD.csv"
 DBMS=csv replace;
RUN;


/* =========================================================================
   BƯỚC 3: HỒI QUY TÍNH TOÁN REM (ABNORMAL CFO) VÀ RESIDUAL BTD
   ========================================================================= */

proc sql;
create table Sales_TA as 
 select a.*, b.TA
 from Sales as a
 join TA as b on a.firm = b.firm and a.year = b.year;
Quit;
Run;
Proc sort Data = Sales_TA nodupkeys; BY firm year; run;

proc sql;
create table REM_B as 
 select a.*, b.OCF
 from Sales_TA as a
 join OCF as b on a.firm = b.Ticker and a.year = b.year;
Quit;
Run;
Proc sort Data = REM_B nodupkeys; BY firm year; run;

/* Tính toán biến trễ và delta cho REM */
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

data REM_B3;
 set REM_B2;
 Y= (OCF*1000000000)/lagTA; /* Quy đổi OCF tỷ đồng sang đồng */
 X1= Sales/lagTA;
 X2= (Sales-lagSales)/lagTA;
run;

/* Chuẩn bị dữ liệu cho hồi quy BTD */
data RES_Data;
 set BTD;
 Y= BTD;
 X1= TA;
run;

/* HỒI QUY 1: Tính phần dư REM (Abnormal CFO) - Lưu vào file Out_REM */
proc reg data= REM_B3 outest=test;
 model Y = X1 X2;
 output out=Out_REM
 residual=r_rem
 predicted=p_rem
 stdr=st_r_rem;
quit;
run;

/* HỒI QUY 2: Tính phần dư BTD (RES) - Lưu vào file Out_BTD */
proc reg data= RES_Data outest=test;
 model Y = X1;
 output out=Out_BTD
 residual=r_btd
 predicted=p_btd
 stdr=st_r_btd;
quit;
run;

/* Tạo tập dữ liệu REM (Abnormal CFO) từ Out_REM */
data REM;
 set Out_REM;
 REM = r_rem*(-1);
 keep firm year REM;
run;
Proc sort Data = REM nodupkeys; BY firm year; run;

/* Tạo tập dữ liệu RESidual từ Out_BTD */
data RESidual;
 set Out_BTD;
 RES = r_btd;
 keep firm year RES;
run;
Proc sort Data = RESidual nodupkeys; BY firm year; run;

/* Xuất kết quả REM ra file CSV */
PROC EXPORT DATA= REM
 OUTFILE= "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\REM.csv"
 DBMS=csv replace;
RUN;


/* =========================================================================
   BƯỚC 4: HỢP NHẤT KẾT QUẢ VÀO FILE MASTER DATA
   ========================================================================= */

proc import datafile = "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\masterdata_w_new.xlsx"
 out = Master
 dbms = xlsx
 replace;
run;
proc sort data = Master NODUPKEYS; by firm year; run;

/* SỬA LỖI: Sử dụng LEFT JOIN để gộp đồng thời các biến BTD, REM, RES vào Master Data
   tránh bị ghi đè mất biến và khắc phục lỗi so sánh nối tiếp */
proc sql;
create table Master_New as 
 select a.*, b.BTD, c.REM, d.RES
 from Master as a
 left join BTD as b on a.firm = b.firm and a.year = b.year
 left join REM as c on a.firm = c.firm and a.year = c.year
 left join RESidual as d on a.firm = d.firm and a.year = d.year;
Quit;
Run;
Proc sort Data = Master_New nodupkeys; BY firm year; run;

/* Xuất kết quả cuối cùng */
PROC EXPORT DATA= Master_New
 OUTFILE= "C:\Users\pThinh\Desktop\Perrrrr\Researchs\NCKHSV 2025\masterdata_w_new2.csv"
 DBMS=csv replace;
RUN;
