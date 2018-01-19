Title: Using the Dynare Preprocessor's JSON output
Date: 2018-01-18
Category: Dynare
Tags: Dynare, Preprocessor, JSON, Matlab
Slug: dynare-preprocessor-w-json
Authors: Houtan Bastani
Summary: An example of how to use the JSON output from the Dynare Preprocessor
Download: https://github.com/houtanb/obsmacro-dynare-json.git

We have recently added an option to produce JSON output from the Dynare Preprocessor. It is available in the [unstable snaphost of Dynare](http://www.dynare.org/snapshot) and will be available in the forthcoming Dynare version 4.6. In this article, I'd like to briefly discuss the setup of the Dynare Preprocessor, the JSON output it produces, and show an example of how to put the JSON output to use by estimating a model via OLS.

## The Dynare Preprocessor ##

At the basic level, the Dynare Preprocessor takes as input a Dynare `.mod` file and outputs the derivatives of the static and dynamic versions of the model in addition to a "driver" file that guides the backend actions to be taken. These outputs are provided for use with Matlab, Octave, C, and, as of the current unstable verion of Dynare, Julia.

In addition to the aforementioned outputs, the unstable version of Dynare provides output in JSON format that represents the `.mod` file at every major preprocessing stage, Parsing, Check Pass, Transform Pass, and Computing Pass. To better understand the type of JSON output that can be obtained, it is helpful to see the Dynare Preprocessor Flow Chart and know in a general sense what is done at each stage:

<div align="center" style="padding-bottom:10px">
<img src="{filename}/images/preprocessor-4.6.png" width="65%" />
</div>

As you can see from the Flow Chart above, there are 6 stages in the preprocessing: Macroprocessing of the model file, Parsing of the macro-expanded model file, Checking of the parsed model, Transformation of the checked model, the internal Computations that are done, and finally the writing of the output files mentioned above.

The macroprocessing stage uses the Dynare Macroprocessing language to perform textual manipulations of the `.mod` file. The output from this stage is a `.mod` file that is ready to be parsed. You can read more about the Dynare Macroprocessin language [here](). The Parsing stage of the preprocessor takes a potentially macro-expanded `.mod` file and parses it, creating an internal representation of the `.mod` file. In doing so, it checks that the `.mod` has valid Dynare Commands and options, that all variables have been declared, and other cursory checks. Once the internal representation of the `.mod` file has been created, the coherence of the `.mod` file is verified during the Check Pass. This is where we ensure that there are the same number of endogenous variables as equations in the model block, for example. After the many checks are performed, the preprocessor Transforms the model, adding auxiliary variables and equations for leaded and lagged variables, thereby transforming the model into time `t-1`, `t`, `t+1` form. Once the transformed model has been created, derivatives of the model are calculated using the symbolic derivative engine in the Computing Pass. Finally, the Matlab, Octave, C, or Julia output is written in the WriteOutput Pass.

## More on JSON  ##

JSON is a data interchange format that is easily read and understood by humans and easily parsed by many programming languages. In short, it associates keys with values like a dictionary. In JSON, keys are strings whereas values can be strings, numbers, arrays, objects, boolean, or null.

The easiest way to get a sense of what a JSON file looks like is to see it. This declaration of parameters in a `.mod` file
```
parameters beta $\beta$ (long_name='discount factor'), rho;
```
would produce the following lines in JSON
```json
"parameters": [{"name":"beta", "texName":"\\beta", "longName":"discount factor"}
             , {"name":"rho", "texName":"rho", "longName":"rho"}]
```
This tells us that key `"parameters"` is associated with an array (enclosed by brackets) of objects (enclosed by braces). The array has two entries. The first entry in this array is an object where the key `"name"` is associated with the string `"beta"`, the key `"texName"` is associated with the string `"\\beta"`, and the string `"longName"` is associated with the string `"discount factor"`. The second entry has similar entries with `rho` replacing `beta`. As you can see, understanding the contents of a JSON file and seeing how those values are related to the originating `.mod` file is straitforward. A list of JSON keys created by Dynare are outlined in the [Dynare manual](http://www.dynare.org/documentation-and-support/manual). For more details on JSON visit [https://www.json.org](https://www.json.org).

A JSON representation of the `.mod` file can be obtained after the Parsing, Check, Transform, and Computation stages outlined above. To obtain JSON output from the Dynare Preprocessor, you must choose where you want that output to be produced by passing the command line option `json=parse|check|transform|compute`. Note that the output provided varies a bit, depending on where you want that output produced. For example, the dynamic and static files will only be produced after the derivatives of the model have been calculated in the Computing Pass. Again, the details of what is produced after every pass is outlined in the [Dynare manual](http://www.dynare.org/documentation-and-support/manual)

## An Example of Putting the JSON output to use: OLS ##

As an example application of how one can use JSON, I will replicate the OLS estimation from Table 1 of Angrist and Fernandez-Val (2013). The data was obtained from [http://sites.bu.edu/ivanf/files/2014/03/m_d_806.dta_.zip](http://sites.bu.edu/ivanf/files/2014/03/m_d_806.dta_.zip) and was modified according to lines 1-88 of `Tables1&2.do` from [http://sites.bu.edu/ivanf/files/2014/03/code.zip](http://sites.bu.edu/ivanf/files/2014/03/code.zip).

I will first show the `.mod` file then show how to call Dynare on this `.mod` file and how to use the JSON output.

### The .mod file ###
The following are the contents of `afv2013table1.mod`:
```
// --+ options: json=compute +--

path(['..' filesep 'ols'], path);

/* Reproduces Table 1 OLS estimate from Angrist and Fernandez-Val (2013)
 * ExtrapoLATE-ing: External Validity and Overidentification in the LATE Framework
 * Data obtained from: http://sites.bu.edu/ivanf/files/2014/03/m_d_806.dta_.zip
 */

var weeksm1, workedm;

varexo resa, resb,
       morekids, agem1, agefstm, boy1st, boy2nd, blackm, hispm, othracem;

parameters a0, a1, a2, a3, a4, a5, a6, a7, a8,
           b0, b1, b2, b3, b4, b5, b6, b7, b8;

model(linear);
    [name='eq1']
    weeksm1 = a0 + a1*morekids + a2*agem1 + a3*agefstm + a4*boy1st + a5*boy2nd + a6*blackm +a7*hispm + a8*othracem + resa;
    [name='eq2']
    workedm = b0 + b1*morekids + b2*agem1 + b3*agefstm + b4*boy1st + b5*boy2nd + b6*blackm +b7*hispm + b8*othracem + resb;
end;

ds = dyn_ols(dseries('Angrist_FernandezVal_2013.csv'));
```
The first line of the file tells the Dynare Preprocessor to produce JSON output after the Computing Pass. This creates the files `afv2013table1.json`, `afv2013table1_original.json`, `afv2013table1_dynamic.json`, and `afv2013table1_static.json`.

The first file, `afv2013table1.json`, is the equivalent of the standard `.m` file output by the Dynare Preprocessor only in JSON format. It contains lists of model variables, the model block (transformed into `t-1`, `t`, `t+1` format), a list of Dynare statements, the list of equation cross references, and some general information about the model.

The second file, `afv2013table1_original.json` contains a slightly modified version of the model as written in the model block. It contains no auxiliary variables or auxiliary equations, but it does expand the `diff` and `adl` commands if there are any. This is the file of interest for the OLS routine as we want to maintain the lag information contained in the model block (in this case, all variables appear at time `t`, but if there were any lags or leads, we'd see them here). This file is written when `json=compute` or `json=transform` is passed as an option to the `dynare` command.

The final two files, `afv2013table1_dynamic.json` and `afv2013table1_static.json`, contain the derivatives of the dynamic and static models. These files are a byproduct of using `json=compute`. Our OLS routine doesn't need them.

### The OLS routine in Matlab: `dyn_ols.m` ###

The OLS routine outlined heren was written in Matlab, but could have just as easily been written in Julia, Python, C, or the language of your choice. There are three main steps involved in writing a routine for that makes use of the Dynare JSON output:

1. Parse the JSON file, loading it into some sort of structure
1. Parse this structure for your purposes
1. Run your computational task, in our case estimation via OLS

#### Step 1: Parsing the JSON file ####

As JSON is widely supported, the first step is often straightforward, regardless of your choice of programming language. In our case, though Matlab doesn't offer JSON support out of the box, there's a widely-used and well-tested toolbox called JSONlab that provides JSON support and is available on the [Matlab File Exchange](https://fr.mathworks.com/matlabcentral/fileexchange/33381-jsonlab--a-toolbox-to-encode-decode-json-files). Downloading JSONlab and adding it to our path allows us to access the model block specified above in just two lines (lines 52-53):
```matlab
jsonmodel = loadjson([M_.fname '_original.json']);
jsonmodel = jsonmodel.model;
```
The first line reads in `afv2013table1_original.json` and loads it into a Matlab structure we call `jsonmodel`. We then select out the `model` field as that is the only one we're interested in and overwrite `jsonmodel` with it. When finished, `jsonmodel` contains the following two cell entries:
```matlab
>> jsonmodel{:}

ans =

  struct with fields:

     lhs: 'weeksm1'
     rhs: 'a0+a1*morekids+a2*agem1+a3*agefstm+a4*boy1st+a5*boy2nd+a6*blackm+a7*hispm+a8*othracem+resa'
    line: 19
    tags: [1x1 struct]


ans =

  struct with fields:

     lhs: 'workedm'
     rhs: 'b0+morekids*b1+agem1*b2+agefstm*b3+boy1st*b4+boy2nd*b5+blackm*b6+hispm*b7+othracem*b8+resb'
    line: 21
    tags: [1x1 struct]
```
As you can see, reading in the JSON code already gives us a lot of information; we have string representaitons of the expressions on the left hand side, right hand side, and equation tag(s) of each equation as well as the line number on which the equation appeared in the `.mod` file. We are now ready to begin parsing each equation in order to contsruct the matrices we will need to run our OLS estimation.

#### Step 2: Parsing the model block ####

Below I will describe the parsing algorithm that I implemented in a draft version of `dyn_ols.m`. There may be speed improvements to be made and it certainly can be made to be more general (we impose, for example, that a parameter can only appear once per equation; a more general parsing algorithm would allow a parameter to appear multiple times and simplify the equation). Though parsing is done in Matlab, one could imagine writing a full parser in Bison and Yacc or PLY to deal with parsing the equations. In short, the correct solution depends on the problem that you are trying to solve, the time you have to implement the solution, and the necessary robustness of the solution.

Our `dyn_ols` routine allows the user to specify equation tags that will be used to select the equations on which to run OLS. This functionality has been split out into `getEquationsByTags.m` which takes the aforementioned `jsonmodel` cell array and the equation tags as arguments and returns `jsonmodel` containing only the equations corresponding to the specified equation tags. The returned cellarray is in the same order as the equation tags argument:
```matlab
function [jsonmodel] = getEquationsByTags(jsonmodel, tagname, tagvalue)
if ischar(tagvalue)
    tagvalue = {tagvalue};
end

idx2keep = [];
for i=1:length(tagvalue)
    found = false;
    for j=1:length(jsonmodel)
        assert(isstruct(jsonmodel{j}), 'Every entry in jsonmodel must be a struct');
        if isfield(jsonmodel{j}, 'tags') && ...
                isfield(jsonmodel{j}.tags, tagname) && ...
                strcmp(jsonmodel{j}.tags.(tagname), tagvalue{i})
            idx2keep = [idx2keep; j];
            found = true;
            break
        end
    end
    if found == false
        warning(['getEquationsByTags: no equation tag found by the name of ''' tagvalue{i} ''''])
    end
end
assert(~isempty(idx2keep), 'getEquationsByTags: no equations selected');
jsonmodel = jsonmodel(unique(idx2keep, 'stable'));
```
Given the pared-down `jsonmodel` variable, I then enter a loop, making one iteration for every equation (first setting a few variables that will be used in the loop) (lines 67-70):
```matlab
M_endo_exo_names_trim = [M_.endo_names; M_.exo_names];
regex = strjoin(M_endo_exo_names_trim(:,1), '|');
mathops = '[\+\*\^\-\/\(\)]';
for i = 1:length(jsonmodel)
```
In our example, we will estimate two equations. I'll expose the parsing and estimation of the first equation (`weeksm1 = a0 + a1*morekids + a2*agem1 + a3*agefstm + a4*boy1st + a5*boy2nd + a6*blackm +a7*hispm + a8*othracem + resa;`), as the process is the same for the second equation.

The first thing we do upon entering the loop is ensure there are no leads in the equation we want to estimate via OLS (lines 72-80):
```matlab
    rhs_ = strsplit(jsonmodel{i}.rhs, {'+','-','*','/','^','log(','exp(','(',')'});
    rhs_(cellfun(@(x) all(isstrprop(x, 'digit')), rhs_)) = [];
    vnames = setdiff(rhs_, M_.param_names);
    if ~isempty(regexp(jsonmodel{i}.rhs, ...
            ['(' strjoin(vnames, '\\(\\d+\\)|') '\\(\\d+\\))'], ...
            'once'))
        error(['dyn_ols: you cannot have leads in equation on line ' ...
            jsonmodel{i}.line ': ' jsonmodel{i}.lhs ' = ' jsonmodel{i}.rhs]);
    end
```
Here, the first line splits the equation by operator, such that `rhs_` is a cellarray of parameter, endogenous, and exogenous names:
```matlab
>> rhs_

rhs_ =

  1x19 cell array

  Columns 1 through 11

    {'a0'}    {'5'}    {'a1'}    {'morekids'}    {'a2'}    {'agem1'}    {'a3'}    {'agefstm'}    {'a4'}    {'boy1st'}    {'a5'}

  Columns 12 through 19

    {'boy2nd'}    {'a6'}    {'blackm'}    {'a7'}    {'hispm'}    {'a8'}    {'othracem'}    {'resa'}
```
The second line removes any constants that may remain in the equation (in our case, there are none). The third line removes the parameter names, leaving us only with endogenous and exogenous variable names:
```matlab
>> vnames

vnames =

  1x9 cell array

    {'agefstm'}    {'agem1'}    {'blackm'}    {'boy1st'}    {'boy2nd'}    {'hispm'}    {'morekids'}    {'othracem'}    {'resa'}
```
Finally, the `regexp` command sees if any of these variables appear in the original equation with a lead. If so, the function ends with an error indicating the equation that contains the lead.

We next initialize a few variables and loop over the parameter names that appear in the right-hand side of the equation at hand (lines 82-86):
```matlab
    pnames = intersect(rhs_, M_.param_names);
    vnames = cell(1, length(pnames));
    splitstrings = cell(length(pnames), 1);
    X = dseries();
    for j = 1:length(pnames)
```
Our goal in this loop is to see which parameters appear in the equation, thereby constructing the `X` matrix of the standard OLS equation $Y=X\beta+\epsilon$. Upon entering the loop, we find the starting and ending index of the parameter in the equation (lines 87-94):
```matlab
        createdvar = false;
        pregex = [...
            mathops pnames{j} mathops ...
            '|^' pnames{j} mathops ...
            '|' mathops pnames{j} '$' ...
            ];
        [startidx, endidx] = regexp(jsonmodel{i}.rhs, pregex, 'start', 'end');
        assert(length(startidx) == 1);
```
Here, the regular expression we create matches the given parameter with mathematical operators appearing before, after, or both. Hence, for the first equation, we have:
```matlab
>> pregex

pregex =

    '[\+\*\^\-\/\(\)]a0[\+\*\^\-\/\(\)]|^a0[\+\*\^\-\/\(\)]|[\+\*\^\-\/\(\)]a0$'

>> jsonmodel{i}.rhs

ans =

    'a0+5*a1*morekids+a2*agem1+a3*agefstm+a4*boy1st+a5*boy2nd+a6*blackm+a7*hispm+a8*othracem+resa'

>> jsonmodel{i}.rhs(startidx:endidx)

ans =

    'a0+'
```
Here we see that for the first parameter, `a0` we find it at the beginning of the right-hand side.

The next block of code deals with the various cases we can fall into, depending on the mathematical operator(s) that are found before, after, or both before and after, the parameter. We impose that parameters be multiply their regressors, and hence take action depending on the location of `*` (in other words, our parsing algorithm does not handnle the case where a parameter divides, or is divided by, a regressor) (lines 95-109):
```matlab
        if jsonmodel{i}.rhs(startidx) == '*' && jsonmodel{i}.rhs(endidx) == '*'
            vnamesl = getStrMoveLeft(jsonmodel{i}.rhs(1:startidx-1));
            vnamesr = getStrMoveRight(jsonmodel{i}.rhs(endidx+1:end));
            vnames{j} = [vnamesl '*' vnamesr];
            splitstrings{j} = [vnamesl '*' pnames{j} '*' vnamesr];
        elseif jsonmodel{i}.rhs(startidx) == '*'
            vnames{j} = getStrMoveLeft(jsonmodel{i}.rhs(1:startidx-1));
            splitstrings{j} = [vnames{j} '*' pnames{j}];
        elseif jsonmodel{i}.rhs(endidx) == '*'
            vnames{j} = getStrMoveRight(jsonmodel{i}.rhs(endidx+1:end));
            splitstrings{j} = [pnames{j} '*' vnames{j}];
            if jsonmodel{i}.rhs(startidx) == '-'
                vnames{j} = ['-' vnames{j}];
                splitstrings{j} = ['-' splitstrings{j}];
            end
```
In our case, given that there is no `*` operator, we deduce that `a0` is the intercept, and we fall into the block on lines 110-123:
```matlab
        elseif jsonmodel{i}.rhs(startidx) == '+' ...
                || jsonmodel{i}.rhs(startidx) == '-' ...
                || jsonmodel{i}.rhs(endidx) == '+' ...
                || jsonmodel{i}.rhs(endidx) == '-'
            % intercept
            createdvar = true;
            if any(strcmp(M_endo_exo_names_trim, 'intercept'))
                [~, vnames{j}] = fileparts(tempname);
                vnames{j} = ['intercept_' vnames{j}];
                assert(~any(strcmp(M_endo_exo_names_trim, vnames{j})));
            else
                vnames{j} = 'intercept';
            end
            splitstrings{j} = vnames{j};
```
We thus create a variable named `intercept` to multiply `a0`. We then continue into the `if` statement on lines 127-133:
```matlab
        if createdvar
            if jsonmodel{i}.rhs(startidx) == '-'
                Xtmp = dseries(-ones(ds.nobs, 1), ds.firstdate, vnames{j});
            else
                Xtmp = dseries(ones(ds.nobs, 1), ds.firstdate, vnames{j});
            end
        else
            Xtmp = eval(regexprep(vnames{j}, regex, 'ds.$&'));
            Xtmp.rename_(vnames{j});
        end
```
Given that we created a new `intercept` variable in the previous block, here we create the associated entries for the `X` matrix, which is just a series of `1`s. Finally, we concatenate `Xtmp` with the other series in `X` on line 137:
```matlab
        X = [X Xtmp];
```
The above loop is repeated for the next parameter in `pnames`, `a1`. This time, the regular expression on line 93 returns the value
```matlab
>> jsonmodel{i}.rhs(startidx:endidx)

ans =

    '+a1*'
```
Here, we see that `a1` is a parameter that multiplies a regressor. We fall into the second `else` block displayed in lines 95-109. Since we know that the regressor is to the right of the `*`, we call a helper function called `getStrMoveRight`, which returns the regressor, in this case `morekids`. As we have not created an `intercept` term here, we find the value of `morekids` from our `dseries` and assign it to `Xtmp` in lines 134-135:
```matlab
            Xtmp = eval(regexprep(vnames{j}, regex, 'ds.$&'));
            Xtmp.rename_(vnames{j});
```
We subsequently concatenate this to our variable `X`. Now, after two loops, we have two columns in `X` associated with a $\beta$ vector of `[a0 a1]`. We continue in this fashion until all parameters in the equation have been treated. When we finish with the loop, `X` has 927,267 observations and 9 columns, implying that $\beta$ is equal to `[a0, a1, a2, a3, a4, a5, a6, a7, a8]`.

Having obtained our `X` matrix, we next move to create the `Y` vector. First we see if there were any regressors on the right-hand side that were not multiplied by a parameter. If this is the case, we create a `dseries` with their values and substract this from the variable(s) that appear on the left-hand side (lines 140-148):
```matlab
    lhssub = getRhsToSubFromLhs(ds, jsonmodel{i}.rhs, regex, [splitstrings; pnames]);
    residuals = setdiff(intersect(rhs_, M_.exo_names), ds.name);
    assert(~isempty(residuals), ['No residuals in equation ' num2str(i)]);
    assert(length(residuals) == 1, ['More than one residual in equation ' num2str(i)]);

    Y = eval(regexprep(jsonmodel{i}.lhs, regex, 'ds.$&'));
    for j = 1:lhssub.vobs
        Y = Y - lhssub{j};
    end
```
By the time we have finished with this block, `Y` is a column vector with 927,267 rows. We next find the first observed period and last observed period in the estimation (lines 150-160):
```matlab
    fp = max(Y.firstobservedperiod, X.firstobservedperiod);
    lp = min(Y.lastobservedperiod, X.lastobservedperiod);
    if isfield(jsonmodel{i}, 'sample') && ~isempty(jsonmodel{i}.sample)
        if fp > jsonmodel{i}.sample(1) || lp < jsonmodel{i}.sample(end)
            warning(['The sample over which you want to estimate contains NaNs. '...
                'Adjusting estimation range to be: ' fp.char ' to ' lp.char])
        else
            fp = jsonmodel{i}.sample(1);
            lp = jsonmodel{i}.sample(end);
        end
    end
```
We allow users to specify the sample range as an equation tag. If this tag exists, we adjust the range to accord with that found in the sample tag. We adjust `X` and `Y` accordingly on lines 162-163:
```matlab
    Y = Y(fp:lp);
    X = X(fp:lp).data;
```
Thus, when parsing is finished, we will have constructed the `Y` vector and the `X` matrix of the standard OLS regression.

#### Step 3: Estimation via OLS ####

Having obtained our Y vector and X matrix, we are now ready to run our estimation. Though we know that $\hat{\beta} = (X'X)^{-1}X'Y$, matrix inversion is slow and numerically unstable for small values. Hence we use the QR decomposition; instead of performing the estimation by simply running the standard OLS Estimation calculation, $\hat{\beta} = R^{-1}Q'Y$ (lines 174-183).
```matlab
    [nobs, nvars] = size(X);
    oo_.ols.(tag).dof = nobs - nvars;

    % Estimated Parameters
    [q, r] = qr(X, 0);
    xpxi = (r'*r)\eye(nvars);
    oo_.ols.(tag).beta = r\(q'*Y.data);
    for j = 1:length(pnames)
        M_.params(strcmp(M_.param_names, pnames{j})) = oo_.ols.(tag).beta(j);
    end
```
After this block, the estimated parameters will be in `oo_.ols.eq1.beta` and will have been asigned to `M_.params`, the Dynare parameter vector that is updated every time an estimation procedure is run.

And that's it! The rest of the code simply takes care of calculating the various statistics and standard errors and displaying the estimated parameters in a table.
