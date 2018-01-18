// --+ options: json=compute +--

path('../ols', path);

/*
 * Reproduces Table 1 OLS estimate from Angrist and Fernandez-Val (2013)
 * ExtrapoLATE-ing: External Validity and Overidentification in the LATE Framework
 * Data obtained from: http://sites.bu.edu/ivanf/files/2014/03/m_d_806.dta_.zip
 *
 */

var weeksm1, workedm;

varexo resa, resb,
       morekids, agem1, agefstm, boy1st, boy2nd, blackm, hispm, othracem;

parameters a0, a1, a2, a3, a4, a5, a6, a7, a8,
           b0, b1, b2, b3, b4, b5, b6, b7, b8;

model(linear);
    weeksm1 = a0 + a1*morekids + a2*agem1 + a3*agefstm + a4*boy1st + a5*boy2nd + a6*blackm +a7*hispm + a8*othracem + resa;
    workedm = b0 + b1*morekids + b2*agem1 + b3*agefstm + b4*boy1st + b5*boy2nd + b6*blackm +b7*hispm + b8*othracem + resb;
end;

dyn_ols(dseries('Angrist_FernandezVal_2013.csv'));
