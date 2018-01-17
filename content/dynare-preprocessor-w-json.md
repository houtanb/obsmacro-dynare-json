Title: Putting the JSON output of the Dynare Preprocessor to use: an example
Date: 2017-12-23
Category: Dynare
Tags: Dynare, Preprocessor, JSON, Matlab
Slug: dynare-preprocessor-w-json
Authors: Houtan Bastani
Summary: An example of how to use the JSON output from the Dynare Preprocessor
Download: https://www.dynare.org

We have recently added JSON output to the Dynare Preprocessor. In this article, I'd like to briefly discuss the setup of the Dynare Preprocessor, the JSON output it produces, and show an example of how to use the JSON output to estiamte a model via OLS.

** The Dynare Preprocessor **

At the basic level, the Dynare Preprocessor takes as input a Dynare .mod file and outputs the static and dynamic first and second derivatives of the model represented therein as well as a representation of the .mod file. These outputs are provided for use with Matlab, Octave, and C. In the current unstable version of Dynare (the future Dynare 4.6), the same outputs have been created in Julia.

<div align="center">
<img src="./img/preprocessor.png" width=90% />
</div>
*Figure 1: Dynare Preprocessor flow chart

There are 6 major steps in the Dynare Preprocessor. The first step is what we term the Macroprocessor. It uses Dynare Macroprocessing directives to perform text manipulations on the .mod file. The next step is the Parsing pass. This takes the (potentially macroprocessed) .mod file as input and parses it, thereby ensuring that is grammatically and syntactically correct. The parsing step produces as output an internal representation of the .mod file which is used throughout the rest of preprocessing. After parsing, we check the internal validity of the .mod file in the Check Pass. This is where we ensure that there are the same number of endogenous variables as equations in the model block, for example. After having been determined to be internally coherent, we transform the model in the Transform Pass. The main task to be done here is to convert a model with leads and lags greater than one to a model in time t-1, t, and t+1, adding auxiliary variables and equations as needed. Next, we come to the Computing Pass where the symbolic first and second derivatives of the model are calculated. Finally, we write the output in the WriteOutput step, producing either Matlab/Octave, C, or Julia output.

** JSON Output **

JSON is a data interchange format that is easily read and understood by humans and easily parsed by many programming languages. In short, it associates keys with values, like in a dictionary. In JSON, keys are strings whereas values can be strings, numbers, arrays, objects, boolean, or null.

The easiest way to get a sense of what a JSON file looks like is to see it. This declaration of parameters in a .mod file
```
parameters beta $\beta$, rho $\rho$;
```
would produce the following lines in JSON
```
"parameters": [{"name":"beta", "texName":"\\beta", "longName":"beta"}
             , {"name":"rho", "texName":"\\rho", "longName":"rho"}]
```
This tells us that key "parameters" is associated with an array (enclosed by brackets) of objects (enclosed by braces). The array has 2 entries. The first entry in this array is an object where the key "name" is associated with the string "beta", the key "texName" is associated with the string "\\beta", and the string "longName" is associated with the string "beta". The second entry has similar entries with rho replacing beta. As you can see, understanding the contents of a JSON file and seeing how those values are related to the originating .mod file is straitforward. A list of JSON keys created by Dynare can be referenced in the Dynare manual. For more details on JSON visit https://www.json.org.

A JSON representation of the .mod file can be obtained after the Parsing Pass, the Check Pass, The Transform Pass, or the Computing Pass, outlined in the previous section. To obtain JSON output from the Dynare Preprocessor, you must choose where you want that output to be produced by passing the command line option `json=parse|check|transform|compute`. Note that the output provided varies a bit, depending on where you want that output produced. For example, the dynamic and static files will only be produced after the derivatives of the model have been calculated in the Computing Pass.

** An Application: an OLS routine using JSON output from the Dynare Preprocessor **

As an example application of how to use JSON, we will replicate the OLS estimation from Table 1 of Angrist and Fernandez-Val (2013). The data was obtained from http://sites.bu.edu/ivanf/files/2014/03/m_d_806.dta_.zip and was modified according to lines 1-88 of `Tables1&2.do` from http://sites.bu.edu/ivanf/files/2014/03/code.zip.

*** The .mod file ***
The following are the contents of `afv2013table1.mod`:
```
// --+ options: json=compute +--

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
```
The first line of the file tells the Dynare Preprocessor to produce JSON output after the Computing Pass. This creates the files afv2013table1.json, afv2013table1_original.json, afv2013table1_dynamic.json, and afv2013table1_static.json.

The first file, `afv2013table1.json`, is the equivalent of the standard `.m` file output by the Dynare Preprocessor only in JSON format. It contains lists of model variables, the model block (transformed into `t-1`, `t`, `t+1` format, a list of Dynare statements, the list of equation cross references, and some general information about the model.

The second file, `afv2013table1_original.json` contains a slightly modified version of the model as written in the model block. It contains no auxiliary variables or auxiliary equations, but it does expand the `diff` and `adl` commands if there are any. This is the file of interest for the OLS routine we will write as we want to maintain the lag information contained in the model block (in this case, all variables appear at time `t`, but if there were any lags or leads, we'd see them here). This file is written when `json=compute` or `json=transform` is passed as an option to the Dynare command.

The final two files, afv2013table1_dynamic.json and afv2013table1_static.json, contain the dynamic and static derivatives of the model. These files are a byproduct of using `json=compute`. Our OLS routine doesn't need them.

*** dyn_ols ***

The OLS routine outlined heren was written in Matlab, but could have just as easily been written in Python, C, or the language of your choice. There are three main steps involved in writing a routine for that makes use of the Dynare JSON output:

1. Parse the JSON file, loading it into some sort of structure
1. Parse this structure for your purposes
1. Do what you want to do, in our case estimation via OLS

**** Step 1: parsing the JSON file ****

The first step is often straitforward. As JSON is widely supported, many programming languages offer routines that read in JSON. Matlab doesn't offer JSON support out of the box, but widely-used and well-tested code is available on the [[Matlab File Exchange][https://fr.mathworks.com/matlabcentral/fileexchange/33381-jsonlab--a-toolbox-to-encode-decode-json-files]]. Downloading this library and adding it to our path allows us to access the model block specified above in just two lines:
```
jsonmodel = loadjson(jsonfile);
jsonmodel = jsonmodel.model;
```
The first line reads the JSON file into a structure while the second line replaces that structure with the contents of the model field. When finished, `jsonmodel` contains the following two cell entries:
```
>> jsonmodel{:}

ans =

  struct with fields:

     lhs: 'weeksm1'
     rhs: 'a0+a1*morekids+a2*agem1+a3*agefstm+a4*boy1st+a5*boy2nd+a6*blackm+a7*hispm+a8*othracem+resa'
    line: 12


ans =

  struct with fields:

     lhs: 'workedm'
     rhs: 'b0+morekids*b1+agem1*b2+agefstm*b3+boy1st*b4+boy2nd*b5+blackm*b6+hispm*b7+othracem*b8+resb'
    line: 13
```
**** Step 2: Parsing the model block ****

Each cell of `jsonmodel` contains information on the left hand side, right hand side, and line number of the model equations in the order they were written in the .mod file.

To set up the regression matrices, we must first parse the `lhs` and `rhs` fields. Depending on what you are trying to do, you may need to set up a more complicated parser than the for loop/if-else statements from line 76-169. That said, for a simple OLS, these lines suffice.

Lines 78-91 find the parameter names on the right hand side and ensure that there are no leads on the variable names. We then (beginning on line 92) loop over the parameter names and find the potential combination of variables that multiply a given parameter. Given that a parameter can multiply a variable from the right (e.g. `var*param`) or from the left (e.g. `param*var`), we have two helper functions that allow us to find what the parameter is multiplying, `getStrMoveLeft.m` and `getStrMoveRight.m`. These functions take as a starting point the multiplication operator and move in the stated direction; it returns the string once it has encountered an additive operator while ensuring that all open parenthesis have been closed. Using the Dynare `dseries` class and the dataset provided in the call to `dyn_ols`, we calculate the entries for the column of regressors associated with this parameter. Looping over all parameters in the equation provides us with the regression matrix X. We construct the vector of observed variables, `Y` by simply evaluating the `lhs` variable.

Thus, by the end of this step, we will have constructed the `Y` vector and the `X` matrix of the standard OLS regression: $Y = X\beta+\epsilon$.


**** Step 3: Estimation via OLS ****

Having obtained our Y vector and X matrix, we are now ready to perform our estimation. Though we know that $\hat{\beta} = (X'X)^{-1}X'Y$, matrix inversion is slow numerically unstable for small values than using the `QR` decomposition. Hence, instead of performing the estimation by simply running the standard OLS Estimation calculation, $\hat{\beta} = R^{-1}Q'Y$.

And that's it! The rest of the code simply takes care of displaying the estimated parameters in a table, assigning them back to `M_.params`, and assigning the ols output to `oo_.ols`.

In the end, the following functions provide OLS support in Dynare using JSON output: dyn_ols, getStrMoveRight, getStrMoveLeft, getRhsToSubFromLhs, dyn_table
