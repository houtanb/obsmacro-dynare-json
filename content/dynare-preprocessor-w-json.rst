Using the Dynare Preprocessor’s JSON Output
###########################################

:date: 2018-02-21
:tags: Dynare, Preprocessor, JSON, Matlab
:category: Dynare
:slug: dynare-preprocessor-w-json
:authors: Houtan Bastani
:summary: An example of how to use the JSON output from the Dynare Preprocessor
:download: https://github.com/houtanb/obsmacro-dynare-json.git
:status: draft

We have recently added an option to produce JSON output from the Dynare
Preprocessor. It is available in the `unstable snaphost of
Dynare <http://www.dynare.org/snapshot>`__ and will be available in the
forthcoming Dynare version 4.6. In this article, I’d like to briefly
discuss the setup of the Dynare Preprocessor, the JSON output it
produces, and show an example of how to put the JSON output to use by
estimating a model via OLS.

The Dynare Preprocessor
-----------------------

At the basic level, the Dynare Preprocessor takes as input a Dynare
``.mod`` file and outputs the derivatives of the static and dynamic
versions of the model in addition to a “driver” file that guides the
backend actions to be taken. These outputs are provided for use with
Matlab, Octave, C, and, as of the current unstable version of Dynare,
Julia.

In addition to the aforementioned outputs, the unstable version of
Dynare provides output in JSON format that represents the ``.mod`` file
at every major preprocessing stage, Parsing, Check Pass, Transform Pass,
and Computing Pass. To better understand the type of JSON output that
can be obtained, it is helpful to see the Dynare Preprocessor Flow Chart
and know in a general sense what is done at each stage:

.. image:: {filename}/images/preprocessor-4.6.png
   :width: 65%
   :alt: Dynare Flow Chart
   :align: center

As you can see from the Flow Chart above, there are 6 preprocessing
stages:

1. Macroprocessor: the Dynare Macroprocessing language is used to
   perform textual manipulations of the ``.mod`` file. The output from
   this stage is a ``.mod`` file that is ready to be parsed. You can
   read more about the Dynare Macroprocessing language
   `here <http://www.dynare.org/summerschool/2017/sebastien/macroprocessor.pdf>`__.
2. Parsing: takes a potentially macro-expanded ``.mod`` file and parses
   it, creating an internal representation of the ``.mod`` file. In
   doing so, among other cursory checks, it verifies that the ``.mod``
   has valid Dynare commands and options, that all variables have been
   declared.
3. Check Pass: verifies the coherence of the ``.mod`` file. For example,
   this is where we ensure that there are the same number of endogenous
   variables as equations in the model block.
4. Transform Pass: among other transformations, adds auxiliary variables
   and equations for leaded and lagged variables, thereby transforming
   the model into ``t-1``, ``t``, ``t+1`` form.
5. Computing Pass: calculates the derivatives of the transformed static
   and dynamic models using the symbolic derivative engine.
6. Write Output: writes Matlab, Octave, C, or Julia files

More on JSON
------------

JSON is a data interchange format that is easily read and understood by
humans and easily parsed by many programming languages. In short, it
associates keys with values like a dictionary. In JSON, keys are strings
whereas values can be strings, numbers, arrays, objects, boolean, or
null.

The easiest way to get a sense of what a JSON file looks like is to see
it. This declaration of parameters in a ``.mod`` file

::

    parameters beta $\beta$ (long_name='discount factor'), rho;

would produce the following lines in JSON

.. code:: json

    "parameters": [{"name":"beta", "texName":"\\beta", "longName":"discount factor"}
                 , {"name":"rho", "texName":"rho", "longName":"rho"}]

This tells us that key ``"parameters"`` is associated with an array
(enclosed by brackets) of objects (enclosed by braces). The array has
two entries. The first entry in this array is an object where the key
``"name"`` is associated with the string ``"beta"``, the key
``"texName"`` is associated with the string ``"\\beta"``, and the string
``"longName"`` is associated with the string ``"discount factor"``. The
second entry has similar keys but, for the case of ``rho``, no specific
:math:`\LaTeX` name or long name was declared, so those keys take the
default values. As you can see, understanding the contents of a JSON
file and seeing how those values are related to the originating ``.mod``
file is straitforward. A list of JSON keys created by Dynare are
outlined in the `Dynare
manual <http://www.dynare.org/documentation-and-support/manual>`__. For
more details on JSON visit https://www.json.org.

A JSON representation of the ``.mod`` file can be obtained after
Parsing, the Check Pass, the Transform Pass, and the Computing Pass
stages outlined above. To obtain JSON output from the Dynare
Preprocessor, you must choose where you want that output to be produced
by passing the command line option
``json=parse|check|transform|compute``. Note that the output provided
varies a bit, depending on where you want that output produced. For
example, the JSON representation of the derivatives of the dynamic and
static models will only be produced after the derivatives of the model
have been calculated in the Computing Pass. Again, the details of what
is produced after every pass is outlined in the `Dynare
manual <http://www.dynare.org/documentation-and-support/manual>`__.

An Example of Putting the JSON output to use: Ordinary Least Squares
--------------------------------------------------------------------

As an example application of how one can use the Dynare JSON output, I will
replicate the OLS estimation from Table 1 of Angrist and Fernandez-Val
(2013). The data was obtained from
`http://sites.bu.edu/ivanf/files/2014/03/m_d_806.dta_.zip
<http://sites.bu.edu/ivanf/files/2014/03/m_d_806.dta_.zip>`_ and was modified
according to lines 1-88 of ``Tables1&2.do`` from
http://sites.bu.edu/ivanf/files/2014/03/code.zip.

Below, I show the ``.mod`` file and how to write a Matlab routine that uses the
JSON representation of said ``.mod`` file to run OLS.

The .mod file
~~~~~~~~~~~~~

The following are the contents of ``afv2013table1.mod``:

.. code-block:: dynare
    :linenos: inline

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

The first line of the file tells the Dynare Preprocessor to produce JSON
output after the Computing Pass. This creates the files
``afv2013table1.json``, ``afv2013table1_original.json``,
``afv2013table1_dynamic.json``, and ``afv2013table1_static.json``.

The first file, ``afv2013table1.json``, is the equivalent of the
standard ``.m`` file output by the Dynare Preprocessor only in JSON
format. It contains lists of model variables, the model block
(transformed into ``t-1``, ``t``, ``t+1`` format), a list of Dynare
statements, the list of equation cross references, and some general
information about the model.

The second file, ``afv2013table1_original.json`` contains a slightly
modified version of the model as written in the model block. It contains
no auxiliary variables or auxiliary equations, but it does expand the
``diff`` and ``adl`` commands if there are any:

.. code-block:: json

    {
    "model":
    [
      {"lhs": "weeksm1",
       "rhs": "a0+a1*morekids+a2*agem1+a3*agefstm+a4*boy1st+a5*boy2nd+a6*blackm+a7*hispm+a8*othracem+resa",
       "line": 19,
       "tags": {"name": "eq1"}
      }
    , {"lhs": "workedm",
       "rhs": "b0+morekids*b1+agem1*b2+agefstm*b3+boy1st*b4+boy2nd*b5+blackm*b6+hispm*b7+othracem*b8+resb",
       "line": 21,
       "tags": {"name": "eq2"}
      }
    ]
    }

This is the file of interest for the OLS routine as we want to maintain the lag
information contained in the model block (in this case, all variables appear at
time ``t``, but if there were any lags or leads, we’d see them here). This file
is written when ``json=compute`` or ``json=transform`` is passed as an option
to the ``dynare`` command.

The final two files, ``afv2013table1_dynamic.json`` and
``afv2013table1_static.json``, contain the derivatives of the dynamic
and static models. These files are a byproduct of using
``json=compute``. Our OLS routine doesn’t need them.

The OLS routine in Matlab: ``dyn_ols.m``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The OLS routine outlined herein was written in Matlab but could have
just as easily been written in Julia, Python, C, or the language of your
choice. There are three main steps involved in writing a routine
that makes use of the Dynare JSON output:

1. Parse the JSON file, loading it into a language-specific structure
2. Parse this structure for your purposes
3. Run your computational task, in our case estimation via OLS

Step 1: Parsing the JSON file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As JSON is widely supported, the first step is often straightforward,
regardless of your choice of programming language. In our case, though
Matlab doesn’t offer JSON support out of the box, there’s a widely-used
and well-tested toolbox called JSONlab that provides JSON support and is
available on the `Matlab File
Exchange <https://fr.mathworks.com/matlabcentral/fileexchange/33381-jsonlab--a-toolbox-to-encode-decode-json-files>`__.
Downloading JSONlab and adding it to our path allows us to access the
model block specified in just two lines:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 52

    jsonmodel = loadjson([M_.fname '_original.json']);
    jsonmodel = jsonmodel.model;

Line 52 reads in ``afv2013table1_original.json`` and loads it
into a Matlab structure we call ``jsonmodel``. Line 53 then selects the
``model`` field as that is the only one we’re interested in and
overwrite ``jsonmodel`` with it. When finished, ``jsonmodel`` contains
the following two cell entries:

.. code:: matlab

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

As you can see, reading in the JSON code already gives us a lot of
information; we have string representaitons of the expressions on the
left hand side, right hand side, and equation tag(s) of each equation as
well as the line number on which the equation appeared in the ``.mod``
file. We are now ready to begin parsing each equation in order to
contsruct the matrices we will need to run our OLS estimation.

Step 2: Parsing the model block
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below I will describe the parsing algorithm that I implemented in a
draft version of ``dyn_ols.m``. There may be speed improvements to be
made and it certainly can be made to be more general (we impose, for
example, that a parameter can only appear once per equation; a more
general parsing algorithm would allow a parameter to appear multiple
times and simplify the equation). Though parsing is done in Matlab, one
could imagine writing a full parser in Bison and Yacc or PLY to deal
with parsing the equations. In short, the correct solution depends on
the problem that you are trying to solve, the time you have to implement
the solution, and the necessary robustness of the solution.

Our ``dyn_ols`` routine allows the user to specify equation tags that
will be used to select the equations on which to run OLS. This
functionality has been split out into ``getEquationsByTags.m`` which
takes the aforementioned ``jsonmodel`` cell array and the equation tags
as arguments and returns ``jsonmodel`` containing only the equations
corresponding to the specified equation tags. The returned cellarray is
in the same order as the equation tags argument:

.. code-block:: matlab
    :linenos: inline

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

Given the pared-down ``jsonmodel`` variable, I then enter a loop in
``dyn_ols.m`` with one iteration for every equation (first setting a few
variables that will be used in the loop):

.. code-block:: matlab
    :linenos: inline
    :linenostart: 67

    M_endo_exo_names_trim = [M_.endo_names; M_.exo_names];
    regex = strjoin(M_endo_exo_names_trim(:,1), '|');
    mathops = '[\+\*\^\-\/\(\)]';
    for i = 1:length(jsonmodel)

In our example we estimate two equations. I’ll expose the parsing
and estimation of the first equation
(``weeksm1 = a0 + a1*morekids + a2*agem1 + a3*agefstm + a4*boy1st + a5*boy2nd + a6*blackm +a7*hispm + a8*othracem + resa;``),
as the process is the same for the second equation.

The first thing we do upon entering the loop is ensure there are no
leads in the equation we want to estimate via OLS:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 72

        rhs_ = strsplit(jsonmodel{i}.rhs, {'+','-','*','/','^','log(','exp(','(',')'});
        rhs_(cellfun(@(x) all(isstrprop(x, 'digit')), rhs_)) = [];
        vnames = setdiff(rhs_, M_.param_names);
        if ~isempty(regexp(jsonmodel{i}.rhs, ...
                ['(' strjoin(vnames, '\\(\\d+\\)|') '\\(\\d+\\))'], ...
                'once'))
            error(['dyn_ols: you cannot have leads in equation on line ' ...
                jsonmodel{i}.line ': ' jsonmodel{i}.lhs ' = ' jsonmodel{i}.rhs]);
        end

Here, line 72 splits the equation by operator such that ``rhs_``
is a cell array of parameter, endogenous, and exogenous names:

.. code:: matlab

    >> rhs_

    rhs_ =

      1x19 cell array

      Columns 1 through 11

        {'a0'}    {'5'}    {'a1'}    {'morekids'}    {'a2'}    {'agem1'}    {'a3'}    {'agefstm'}    {'a4'}    {'boy1st'}    {'a5'}

      Columns 12 through 19

        {'boy2nd'}    {'a6'}    {'blackm'}    {'a7'}    {'hispm'}    {'a8'}    {'othracem'}    {'resa'}

Line 73 removes any constants that may remain in the equation
(in our case, there are none). Line 74 removes the parameter
names, leaving us only with endogenous and exogenous variable names:

.. code:: matlab

    >> vnames

    vnames =

      1x9 cell array

        {'agefstm'}    {'agem1'}    {'blackm'}    {'boy1st'}    {'boy2nd'}    {'hispm'}    {'morekids'}    {'othracem'}    {'resa'}

Finally, the ``regexp`` command on line 75 sees if any of these variables
appear in the original equation with a lead. If so, the function ends with an
error indicating the equation that contains the lead.

We next initialize a few variables and loop over the parameter names
that appear in the right-hand side of the equation at hand:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 82

        pnames = intersect(rhs_, M_.param_names);
        vnames = cell(1, length(pnames));
        splitstrings = cell(length(pnames), 1);
        X = dseries();
        for j = 1:length(pnames)

Our goal in this loop is to see which parameters appear in the equation,
thereby constructing the ``X`` matrix of the standard OLS equation
:math:`Y=X\beta+\varepsilon`. Upon entering the loop, we find the starting
and ending index of the parameter in the equation:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 87

            createdvar = false;
            pregex = [...
                mathops pnames{j} mathops ...
                '|^' pnames{j} mathops ...
                '|' mathops pnames{j} '$' ...
                ];
            [startidx, endidx] = regexp(jsonmodel{i}.rhs, pregex, 'start', 'end');
            assert(length(startidx) == 1);

Here, the regular expression we create on line 88 matches the given parameter with
mathematical operators appearing before, after, or both. Hence, for the
first equation, we have:

.. code:: matlab

    >> pregex

    pregex =

        '[\+\*\^\-\/\(\)]a0[\+\*\^\-\/\(\)]|^a0[\+\*\^\-\/\(\)]|[\+\*\^\-\/\(\)]a0$'

    >> jsonmodel{i}.rhs

    ans =

        'a0+5*a1*morekids+a2*agem1+a3*agefstm+a4*boy1st+a5*boy2nd+a6*blackm+a7*hispm+a8*othracem+resa'

    >> jsonmodel{i}.rhs(startidx:endidx)

    ans =

        'a0+'

Here we see that for the first parameter, ``a0``, we find it at the
beginning of the right-hand side.

The next block of code deals with the various cases we can fall into,
depending on the mathematical operator(s) that are found before, after,
or both before and after, the parameter. We impose that parameters be
multiply their regressors, and hence take action depending on the
location of ``*`` (in other words, our parsing algorithm does not
handle the case where a parameter divides, or is divided by, a
regressor):

.. code-block:: matlab
    :linenos: inline
    :linenostart: 95

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

In our case, given that there is no ``*`` operator, we deduce that
``a0`` is the intercept and we fall into the `elseif` block of code below:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 110

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

We thus create a variable named ``intercept`` to multiply ``a0``. Processing continues
into the ``if`` statement:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 127

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

Since we created a new ``intercept`` variable in the ``elseif`` block beginning
on line 110, we create the associated entries for the ``X`` matrix on line 131,
which is just a series of ``1``\'s. Finally, we concatenate ``Xtmp`` with the
other series in ``X`` (in the first pass, ``X`` is empty):

.. code-block:: matlab
    :linenos: inline
    :linenostart: 137

            X = [X Xtmp];

The above loop is repeated for the next parameter in ``pnames``, ``a1``.
This time, the regular expression on line 93 returns the value

.. code:: matlab

    >> jsonmodel{i}.rhs(startidx:endidx)

    ans =

        '+a1*'

Here, we see that ``a1`` is a parameter that multiplies a regressor. We hence
fall into the ``elseif`` block beginning on line 103. Since we know that the
regressor is to the right of the ``*``, we call a helper function called
``getStrMoveRight``, which returns the regressor, in this case ``morekids``. As
we have not created an ``intercept`` term here, we fall into the ``else`` block
on line 133, obtaining the value of ``morekids`` from our ``dseries`` and
assigning it to ``Xtmp``. We subsequently concatenate this to our variable
``X`` on line 137.

Now, after two loops, we have two columns in ``X`` associated with a
:math:`\beta` vector of ``[a0; a1]``. We continue in this fashion until all
parameters in the equation have been treated. When we finish with the loop,
``X`` has 927,267 observations and 9 columns, implying that :math:`\beta` is
equal to ``[a0; a1; a2; a3; a4; a5; a6; a7; a8]``.

Having obtained our ``X`` matrix, we turn our attention to the ``Y``
vector. First we see if there were any regressors on the right-hand side
that were not multiplied by a parameter. If this is the case, we create
a ``dseries`` with their values and substract them from the variable(s)
that appear on the left-hand side:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 140

        lhssub = getRhsToSubFromLhs(ds, jsonmodel{i}.rhs, regex, [splitstrings; pnames]);
        residuals = setdiff(intersect(rhs_, M_.exo_names), ds.name);
        assert(~isempty(residuals), ['No residuals in equation ' num2str(i)]);
        assert(length(residuals) == 1, ['More than one residual in equation ' num2str(i)]);

        Y = eval(regexprep(jsonmodel{i}.lhs, regex, 'ds.$&'));
        for j = 1:lhssub.vobs
            Y = Y - lhssub{j};
        end

By the time we have finished with this block, ``Y`` is a column vector
with 927,267 rows. We next find the first observed period and last
observed period in the estimation:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 150

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

We allow users to specify the sample range as an equation tag. If this
tag exists (line 152), we adjust the range to accord with that found in the sample
tag (lines 157-158). We adjust ``X`` and ``Y`` accordingly:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 162

        Y = Y(fp:lp);
        X = X(fp:lp).data;

Thus, when parsing is finished, we will have constructed the ``Y``
vector and the ``X`` matrix of the standard OLS regression.

Step 3: Estimation via OLS
^^^^^^^^^^^^^^^^^^^^^^^^^^

Having obtained our Y vector and X matrix, we are now ready to run our
estimation. Though we know that :math:`\hat{\beta} = (X'X)^{-1}X'Y`,
matrix inversion is slow and numerically unstable for small values.
Hence we use the QR decomposition; instead of performing the estimation
by simply running the standard OLS estimation, we run
:math:`\hat{\beta} = R^{-1}Q'Y`:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 174

        [nobs, nvars] = size(X);
        oo_.ols.(tag).dof = nobs - nvars;

        % Estimated Parameters
        [q, r] = qr(X, 0);
        xpxi = (r'*r)\eye(nvars);
        oo_.ols.(tag).beta = r\(q'*Y.data);
        for j = 1:length(pnames)
            M_.params(strcmp(M_.param_names, pnames{j})) = oo_.ols.(tag).beta(j);
        end

After this block, the estimated parameters will be in
``oo_.ols.eq1.beta`` and will have been asigned to ``M_.params``, the
Dynare parameter vector that is updated every time an estimation
procedure is run.

And that’s it! The rest of the code simply takes care of calculating the
various statistics and standard errors and displaying the estimated
parameters in a table:

.. code:: matlab

                    OLS Estimation of equation 'eq1'

        Dependent Variable: weeksm1
        No. Independent Variables: 9
        Observations: 927267 from 1Y to 927267Y

                     Coefficients    t-statistic      Std. Error
                     ____________    ____________    ____________

        intercept        19.45968       143.37407         0.13573
        morekids         -9.60721      -171.41863         0.05605
        agem1             0.99457       193.09006         0.00515
        agefstm          -1.11455      -152.68575         0.00730
        boy1st           -0.16694        -3.66758         0.04552
        boy2nd           -3.20527       -65.88935         0.04865
        blackm            5.32933        74.30546         0.07172
        hispm            -1.94903       -13.69256         0.14234
        othracem          2.60498        20.10162         0.12959

        R^2: 0.061597
        R^2 Adjusted: 0.061588
        s^2: 479.946813
        Durbin-Watson: 1.913751
    _____________________________________________________________




                    OLS Estimation of equation 'eq2'

        Dependent Variable: workedm
        No. Independent Variables: 9
        Observations: 927267 from 1Y to 927267Y

                     Coefficients    t-statistic      Std. Error
                     ____________    ____________    ____________

        intercept         0.66257       223.69190         0.00296
        morekids         -0.18223      -148.99577         0.00122
        agem1             0.01444       128.50685         0.00011
        agefstm          -0.02044      -128.28998         0.00016
        boy1st           -0.00161        -1.62034         0.00099
        boy2nd           -0.05694       -53.63318         0.00106
        blackm            0.08355        53.38116         0.00157
        hispm            -0.05495       -17.68807         0.00311
        othracem          0.03345        11.82874         0.00283

        R^2: 0.039395
        R^2 Adjusted: 0.039386
        s^2: 0.228573
        Durbin-Watson: 1.919213
    _____________________________________________________________
