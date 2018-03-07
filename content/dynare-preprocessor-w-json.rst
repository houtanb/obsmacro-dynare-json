Using the Dynare Preprocessor’s JSON Output
###########################################

:date: 2018-03-13
:tags: Dynare, Preprocessor, JSON, Matlab
:category: Dynare
:slug: dynare-preprocessor-w-json
:authors: Houtan Bastani
:summary: An example of how to use the JSON output from the Dynare Preprocessor
:download: https://github.com/houtanb/obsmacro-dynare-json.git
:status: draft

We have recently added an option to produce JSON output from the Dynare
Preprocessor. If you're new to Dynare you should know that the Preprocessor is
the part of Dynare that transforms your ``.mod`` file into a file usable by
Matlab, Octave, C, or Julia. Providing JSON output allows us to communicate the
information contained in the ``.mod`` file, as well as the static and dynamic
derivatives of the model, in a way that is easily parsed by many programming
languages. This makes it possible to use the power of the Dynare Modeling
Language in any programming environment you may so desire.

In this post, I'd like to walk you through an example_ of putting the JSON
output of the Dynare Preprocessor to use. We will write a routine that parses
the JSON output and estimates the parameters, equation by equation, via
Ordinary Least Squares. We will then use this routine to estimate the Taylor
rule parameters from Smets and Wouters (2007). These OLS-estimated parameters
can in turn be compared against the parameters estimated via a MLE estimation
of the model as a whole.  However, before getting to the example, I'd like to
briefly give you some background on `the Dynare Preprocessor`_ and the JSON_
output it produces.

On a final, practical, note, you should know that the OLS routine and the
modified ``.mod`` file described herein work with the current `unstable
snapshot of Dynare <http://www.dynare.org/snapshot>`__ . A stable version of
Dynare with JSON output will be available in Dynare 4.6, due out in
summer 2018.

.. _preprocessor:

The Dynare Preprocessor
-----------------------

At the basic level, the `Dynare Preprocessor
<https://github.com/DynareTeam/dynare-preprocessor>`__ takes as input a Dynare
``.mod`` file and outputs the derivatives of the static and dynamic versions of
the model in addition to a “driver” file that guides the back end actions to be
taken. These outputs are provided for use with Matlab, Octave, C, and, as of
the current unstable version of Dynare, Julia.

In addition to the aforementioned outputs, the unstable version of
Dynare provides output in JSON format that represents the ``.mod`` file
at every major preprocessing stage: Parsing, Check Pass, Transform Pass,
and Computing Pass. To better understand the type of JSON output that
can be obtained, it is helpful to see the Dynare Preprocessor Flow Chart
and know in a general sense what is done at each stage:

.. image:: {filename}/images/preprocessor-4.6.png
   :width: 85%
   :alt: Dynare Preprocessor Flow Chart
   :align: center

As you can see from the flow chart above, there are 6 preprocessing
stages:

1. **Macroprocessor**: the Dynare Macroprocessing language is used to
   perform textual manipulations of the ``.mod`` file. The output from
   this stage is a ``.mod`` file that is ready to be parsed. You can
   read more about the Dynare Macroprocessing language
   `here <http://www.dynare.org/summerschool/2017/sebastien/macroprocessor.pdf>`__.
2. **Parsing**: takes a potentially macro-expanded ``.mod`` file and parses it,
   creating an internal representation of the ``.mod`` file. In doing so, among
   other cursory checks, it verifies that the ``.mod`` file has valid Dynare
   commands and options, and that all variables have been declared.
3. **Check Pass**: verifies the coherence of the ``.mod`` file. For example,
   this is where we ensure that the number of declared endogenous
   variables equals the number of equations in the model block.
4. **Transform Pass**: among other transformations, adds auxiliary variables
   and equations for leaded and lagged variables, thereby transforming
   the model into ``t-1``, ``t``, ``t+1`` form.
5. **Computing Pass**: calculates the derivatives of the transformed static
   and dynamic models using the symbolic derivative engine.
6. **Write Output**: writes Matlab, Octave, C, or Julia files

.. _JSON:

More on JSON
------------

JSON is a data interchange format that is easily understood by humans and
easily parsed by many programming languages. In short, it associates keys with
values like a dictionary. In JSON, keys are strings whereas values can be
strings, numbers, arrays, objects, boolean, or null.

The easiest way to get a sense of what a JSON file looks like is to see
it. This declaration of parameters in a ``.mod`` file

::

    parameters beta $\beta$ (long_name='discount factor'), rho;

would produce the following lines in JSON

.. code:: json

    "parameters": [{"name":"beta", "texName":"\\beta", "longName":"discount factor"}
                 , {"name":"rho", "texName":"rho", "longName":"rho"}]

This tells us that key ``"parameters"`` is associated with an array (enclosed
by brackets) of objects (enclosed by braces). The array has two entries. The
first entry in this array is an object where the key ``"name"`` is associated
with the string ``"beta"``, the key ``"texName"`` is associated with the string
``"\\beta"``, and the string ``"longName"`` is associated with the string
``"discount factor"``. The second entry has similar keys but, for the case of
``rho``, no specific :math:`\LaTeX` name or long name was declared, so those
keys take the default values. As you can see, understanding the contents of a
JSON file and seeing how they correspond to the originating ``.mod`` file is
straightforward. A list of JSON keys created by Dynare are outlined in the
`Dynare manual <http://www.dynare.org/documentation-and-support/manual>`__. For
more details on JSON visit https://www.json.org.

A JSON representation of the ``.mod`` file can be obtained after the
Parsing, Check Pass, Transform Pass, and Computing Pass
stages outlined `above <preprocessor_>`_. To obtain JSON output from the Dynare
Preprocessor, you must choose where you want that output to be produced
by passing the command line option
``json=parse|check|transform|compute``. Note that the output provided
varies a bit, depending on where you want that output produced. For
example, the JSON representation of the derivatives of the dynamic and
static models will only be produced after the derivatives of the model
have been calculated in the Computing Pass. Again, the details of what
is produced after every stage are outlined in the `Dynare
manual <http://www.dynare.org/documentation-and-support/manual>`__.

.. _example:

An Example of Putting the JSON output to use: Ordinary Least Squares
--------------------------------------------------------------------

As an example application of how one can use the Dynare JSON output, I will run
OLS on the Taylor rule in Smets and Wouters (2007).

The original ``.mod`` file, ``Smets_Wouters_2007.mod``, and data file,
``usmodel_data.mat``, were downloaded from Johannes Pfeifer's `DSGE_mod
repository <https://github.com/JohannesPfeifer/DSGE_mod>`__.

Below, I show the ``.mod`` and describe the modifications I made to it. After
that, I describe the construction of the Matlab routine that makes use of the
JSON representation of any ``.mod`` file to run OLS. I then run OLS on the
monetary policy rule, and compare the parameters estimated via OLS to those
estimated via MLE

The .mod file
~~~~~~~~~~~~~

The following are the contents of ``Smets_Wouters_2007.mod``, that I modified
for this post. The changes I made can be seen in an easy-to-view fashion by
looking at the `commit on GitHub
<https://github.com/houtanb/obsmacro-dynare-json/commit/981bcdaa46ff06c52d9059be310671082a2c4099>`__.

.. code-block:: dynare
    :linenos: inline

    // --+ options: json=compute +--
    path(['..' filesep 'ols'], path);

    /*
     * This file provides replication files for
     * Smets, Frank and Wouters, Rafael (2007): "Shocks and Frictions in US Business Cycles: A Bayesian
     * DSGE Approach", American Economic Review, 97(3), 586-606, that are compatible with Dynare 4.2.5 onwards
     *
     * To replicate the full results, you have to get back to the original replication files available at
     * https://www.aeaweb.org/articles.php?doi=10.1257/aer.97.3.586 and include the respective estimation commands and mode-files.
     *
     * Notes: Please see the header to the Smets_Wouters_2007_45.mod for more details and a fully documented version.
     *
     * This file was originally written by Frank Smets and Rafeal Wouters and has been updated by
     * Johannes Pfeifer.
     *
     * Please note that the following copyright notice only applies to this Dynare
     * implementation of the model
     */

    /*
     * Copyright (C) 2007-2013 Frank Smets and Raf Wouters
     * Copyright (C) 2013-15 Johannes Pfeifer
     *
     * This is free software: you can redistribute it and/or modify
     * it under the terms of the GNU General Public License as published by
     * the Free Software Foundation, either version 3 of the License, or
     * (at your option) any later version.
     *
     * This file is distributed in the hope that it will be useful,
     * but WITHOUT ANY WARRANTY; without even the implied warranty of
     * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     * GNU General Public License for more details.
     *
     * You can receive a copy of the GNU General Public License
     * at <http://www.gnu.org/licenses/>.
     */

    var labobs robs pinfobs dy dc dinve dw ewma epinfma zcapf rkf kf pkf cf
        invef yf labf wf rrf mc zcap rk k pk c inve y lab pinf w r a b g qs
        spinf sw kpf kp ygap;

    varexo ea eb eg eqs ms epinf ew;

    parameters curvw cgy curvp constelab constepinf constebeta cmaw cmap calfa
               czcap csadjcost ctou csigma chabb ccs cinvs cfc
               cindw cprobw cindp cprobp csigl clandaw
               crdpi crdy crr crpiMcrpiXcrr cryMcryXcrr
               crhoa crhoas crhob crhog crhols crhoqs crhoms crhopinf crhow
               ctrend cg;

    // fixed parameters
    ctou=.025;
    clandaw=1.5;
    cg=0.18;
    curvp=10;
    curvw=10;

    // estimated parameters initialisation
    calfa=.24;
    cbeta=.9995;
    csigma=1.5;
    cfc=1.5;
    cgy=0.51;

    csadjcost= 6.0144;
    chabb=    0.6361;
    cprobw=   0.8087;
    csigl=    1.9423;
    cprobp=   0.6;
    cindw=    0.3243;
    cindp=    0.47;
    czcap=    0.2696;
    crr=      0.8762;
    crdy=     0.2347;
    crpiMcrpiXcrr = 0.1842;
    cryMcryXcrr   = 0.0073;

    crhoa=    0.9977;
    crhob=    0.5799;
    crhog=    0.9957;
    crhols=   0.9928;
    crhoqs=   0.7165;
    crhoas=1;
    crhoms=0;
    crhopinf=0;
    crhow=0;
    cmap = 0;
    cmaw  = 0;

    constelab=0;

    model(linear);
    //deal with parameter dependencies; taken from usmodel_stst.mod
    #cpie=1+constepinf/100;
    #cgamma=1+ctrend/100;
    #cbeta=1/(1+constebeta/100);

    #clandap=cfc;
    #cbetabar=cbeta*cgamma^(-csigma);
    #cr=cpie/(cbeta*cgamma^(-csigma));
    #crk=(cbeta^(-1))*(cgamma^csigma) - (1-ctou);
    #cw = (calfa^calfa*(1-calfa)^(1-calfa)/(clandap*crk^calfa))^(1/(1-calfa));
    #cikbar=(1-(1-ctou)/cgamma);
    #cik=(1-(1-ctou)/cgamma)*cgamma;
    #clk=((1-calfa)/calfa)*(crk/cw);
    #cky=cfc*(clk)^(calfa-1);
    #ciy=cik*cky;
    #ccy=1-cg-cik*cky;
    #crkky=crk*cky;
    #cwhlc=(1/clandaw)*(1-calfa)/calfa*crk*cky/ccy;
    #cwly=1-crk*cky;

    #conster=(cr-1)*100;

        // flexible economy
        0*(1-calfa)*a + 1*a = calfa*rkf+(1-calfa)*(wf);
        zcapf = (1/(czcap/(1-czcap)))* rkf;
        rkf = (wf)+labf-kf;
        kf = kpf(-1)+zcapf;
        invef = (1/(1+cbetabar*cgamma))* (  invef(-1) + cbetabar*cgamma*invef(1)+(1/(cgamma^2*csadjcost))*pkf ) +qs;
        pkf = -rrf-0*b+(1/((1-chabb/cgamma)/(csigma*(1+chabb/cgamma))))*b +(crk/(crk+(1-ctou)))*rkf(1) +  ((1-ctou)/(crk+(1-ctou)))*pkf(1);
        cf = (chabb/cgamma)/(1+chabb/cgamma)*cf(-1) + (1/(1+chabb/cgamma))*cf(+1) +((csigma-1)*cwhlc/(csigma*(1+chabb/cgamma)))*(labf-labf(+1)) - (1-chabb/cgamma)/(csigma*(1+chabb/cgamma))*(rrf+0*b) + b;
        yf = ccy*cf+ciy*invef+g  +  crkky*zcapf;
        yf = cfc*( calfa*kf+(1-calfa)*labf +a );
        wf = csigl*labf   +(1/(1-chabb/cgamma))*cf - (chabb/cgamma)/(1-chabb/cgamma)*cf(-1);
        kpf = (1-cikbar)*kpf(-1)+(cikbar)*invef + (cikbar)*(cgamma^2*csadjcost)*qs;

        // sticky price - wage economy
        mc = calfa*rk+(1-calfa)*(w) - 1*a - 0*(1-calfa)*a;
        zcap = (1/(czcap/(1-czcap)))* rk;
        rk = w+lab-k;
        k = kp(-1)+zcap;
        inve = (1/(1+cbetabar*cgamma))* (  inve(-1) + cbetabar*cgamma*inve(1)+(1/(cgamma^2*csadjcost))*pk ) +qs;
        pk = -r+pinf(1)-0*b +(1/((1-chabb/cgamma)/(csigma*(1+chabb/cgamma))))*b + (crk/(crk+(1-ctou)))*rk(1) +  ((1-ctou)/(crk+(1-ctou)))*pk(1);
        c = (chabb/cgamma)/(1+chabb/cgamma)*c(-1) + (1/(1+chabb/cgamma))*c(+1) +((csigma-1)*cwhlc/(csigma*(1+chabb/cgamma)))*(lab-lab(+1)) - (1-chabb/cgamma)/(csigma*(1+chabb/cgamma))*(r-pinf(+1) + 0*b) +b;
        y = ccy*c+ciy*inve+g  +  1*crkky*zcap;
        y = cfc*( calfa*k+(1-calfa)*lab +a );
        pinf = (1/(1+cbetabar*cgamma*cindp)) * ( cbetabar*cgamma*pinf(1) +cindp*pinf(-1)+((1-cprobp)*(1-cbetabar*cgamma*cprobp)/cprobp)/((cfc-1)*curvp+1)*(mc)  )  + spinf;
        w = (1/(1+cbetabar*cgamma))*w(-1)+(cbetabar*cgamma/(1+cbetabar*cgamma))*w(1)+(cindw/(1+cbetabar*cgamma))*pinf(-1)-(1+cbetabar*cgamma*cindw)/(1+cbetabar*cgamma)*pinf+(cbetabar*cgamma)/(1+cbetabar*cgamma)*pinf(1)+(1-cprobw)*(1-cbetabar*cgamma*cprobw)/((1+cbetabar*cgamma)*cprobw)*(1/((clandaw-1)*curvw+1))*(csigl*lab + (1/(1-chabb/cgamma))*c - ((chabb/cgamma)/(1-chabb/cgamma))*c(-1) -w)+ 1*sw;
        [name='taylor_rule']
        r = crpiMcrpiXcrr*pinf + cryMcryXcrr*ygap + crdy*diff(ygap) + crr*r(-1) + ms;
        ygap = y - yf;
        a = crhoa*a(-1)  + ea;
        b = crhob*b(-1) + eb;
        g = crhog*(g(-1)) + eg + cgy*ea;
        qs = crhoqs*qs(-1) + eqs;
        spinf = crhopinf*spinf(-1) + epinfma - cmap*epinfma(-1);
        epinfma=epinf;
        sw = crhow*sw(-1) + ewma - cmaw*ewma(-1);
        ewma = ew;
        kp = (1-cikbar)*kp(-1)+cikbar*inve + cikbar*cgamma^2*csadjcost*qs;

        // measurment equations
        dy = y-y(-1)+ctrend;
        dc = c-c(-1)+ctrend;
        dinve = inve-inve(-1)+ctrend;
        dw = w-w(-1)+ctrend;
        pinfobs = 1*(pinf) + constepinf;
        robs = 1*(r) + conster;
        labobs = lab + constelab;
    end;

    steady_state_model;
    dy=ctrend;
    dc=ctrend;
    dinve=ctrend;
    dw=ctrend;
    pinfobs = constepinf;
    robs = (((1+constepinf/100)/((1/(1+constebeta/100))*(1+ctrend/100)^(-csigma)))-1)*100;
    labobs = constelab;
    end;

    shocks;
    var ea;
    stderr 0.4618;
    var eb;
    stderr 1.8513;
    var eg;
    stderr 0.6090;
    var eqs;
    stderr 0.6017;
    var ms;
    stderr 0.2397;
    var epinf;
    stderr 0.1455;
    var ew;
    stderr 0.2089;
    end;

    estimated_params;
    // PARAM NAME, INITVAL, LB, UB, PRIOR_SHAPE, PRIOR_P1, PRIOR_P2, PRIOR_P3, PRIOR_P4, JSCALE
    // PRIOR_SHAPE: BETA_PDF, GAMMA_PDF, NORMAL_PDF, INV_GAMMA_PDF
    stderr ea,0.4618,0.01,3,INV_GAMMA_PDF,0.1,2;
    stderr eb,0.1818513,0.025,5,INV_GAMMA_PDF,0.1,2;
    stderr eg,0.6090,0.01,3,INV_GAMMA_PDF,0.1,2;
    stderr eqs,0.46017,0.01,3,INV_GAMMA_PDF,0.1,2;
    stderr ms,0.2397,0.01,3,INV_GAMMA_PDF,0.1,2;
    stderr epinf,0.1455,0.01,3,INV_GAMMA_PDF,0.1,2;
    stderr ew,0.2089,0.01,3,INV_GAMMA_PDF,0.1,2;
    crhoa,.9676 ,.01,.9999,BETA_PDF,0.5,0.20;
    crhob,.2703,.01,.9999,BETA_PDF,0.5,0.20;
    crhog,.9930,.01,.9999,BETA_PDF,0.5,0.20;
    crhoqs,.5724,.01,.9999,BETA_PDF,0.5,0.20;
    crhoms,.3,.01,.9999,BETA_PDF,0.5,0.20;
    crhopinf,.8692,.01,.9999,BETA_PDF,0.5,0.20;
    crhow,.9546,.001,.9999,BETA_PDF,0.5,0.20;
    cmap,.7652,0.01,.9999,BETA_PDF,0.5,0.2;
    cmaw,.8936,0.01,.9999,BETA_PDF,0.5,0.2;
    csadjcost,6.3325,2,15,NORMAL_PDF,4,1.5;
    csigma,1.2312,0.25,3,NORMAL_PDF,1.50,0.375;
    chabb,0.7205,0.001,0.99,BETA_PDF,0.7,0.1;
    cprobw,0.7937,0.3,0.95,BETA_PDF,0.5,0.1;
    csigl,2.8401,0.25,10,NORMAL_PDF,2,0.75;
    cprobp,0.7813,0.5,0.95,BETA_PDF,0.5,0.10;
    cindw,0.4425,0.01,0.99,BETA_PDF,0.5,0.15;
    cindp,0.3291,0.01,0.99,BETA_PDF,0.5,0.15;
    czcap,0.2648,0.01,1,BETA_PDF,0.5,0.15;
    cfc,1.4672,1.0,3,NORMAL_PDF,1.25,0.125;
    crr,0.8258,0.5,0.975,BETA_PDF,0.75,0.10;
    crdy,0.2239,0.001,0.5,NORMAL_PDF,0.125,0.05;
    crpiMcrpiXcrr,0.1842,0.01,2,NORMAL_PDF,1.5,0.25;
    cryMcryXcrr,0.0073,0.001,0.975,NORMAL_PDF,0.125,0.05;
    constepinf,0.7,0.1,2.0,GAMMA_PDF,0.625,0.1;//20;
    constebeta,0.7420,0.01,2.0,GAMMA_PDF,0.25,0.1;//0.20;
    constelab,1.2918,-10.0,10.0,NORMAL_PDF,0.0,2.0;
    ctrend,0.3982,0.1,0.8,NORMAL_PDF,0.4,0.10;
    cgy,0.05,0.01,2.0,NORMAL_PDF,0.5,0.25;
    calfa,0.24,0.01,1.0,NORMAL_PDF,0.3,0.05;
    end;

    varobs dy dc dinve labobs pinfobs dw robs;

    ds = dseries('usmodel_dseries.csv');
    ds.ygap = ds.y.detrend(1);
    dyn_ols(ds, {}, {'taylor_rule'});
    crr           = 0.8762;
    crdy          = 0.2347;
    crpiMcrpiXcrr = 0.1842;
    cryMcryXcrr   = 0.0073;

    estimation(optim=('MaxIter',200),datafile=usmodel_data,mode_compute=4,first_obs=1, presample=4,lik_init=2,prefilter=0,mh_replic=0,mh_nblocks=2,mh_jscale=0.20,mh_drop=0.2, nograph, nodiagnostic, tex, filtered_vars);

    shock_decomposition y;


First Modification
^^^^^^^^^^^^^^^^^^

The first line of the file tells the Dynare Preprocessor to produce JSON output
after the Computing Pass. This creates the files ``Smets_Wouters_2007.json``,
``Smets_Wouters_2007_original.json``, ``Smets_Wouters_2007_static.json``, and
``Smets_Wouters_2007_dynamic.json``.

The first file, ``Smets_Wouters_2007.json``, is the equivalent of the
standard ``.m`` file output by the Dynare Preprocessor only in JSON
format. It contains lists of model variables, the model block
(transformed into ``t-1``, ``t``, ``t+1`` format), a list of Dynare
statements, the list of equation cross references, and some general
information about the model.

The second file, ``Smets_Wouters_2007_original.json`` contains a slightly
modified version of the model as written in the model block. It contains no
auxiliary variables or auxiliary equations, but it does expand ``adl`` nodes,
if there are any. Here is what the Taylor rule looks like in JSON format:

.. code-block:: json

    {
    "model":
    [
      ...
      {
        "lhs": "r",
        "rhs": "pinf*crpiMcrpiXcrr+cryMcryXcrr*ygap+crdy*diff(ygap)+crr*r(-1)+ms",
        "line": 141,
        "tags": {
                  "name": "taylor_rule"
                }
      },
      ...
    ]
    }

This is the file of interest for the OLS routine as we want to maintain the lag
information contained in the model block. This file is written when either
``json=compute`` or ``json=transform`` is passed as an option to the ``dynare``
command.

The final two files, ``Smets_Wouters_2007_static.json`` and
``Smets_Wouters_2007_dynamic.json``, contain the derivatives of the dynamic and
static models. These files are a byproduct of using ``json=compute``. Our OLS
routine doesn’t need them.

Second Modification
^^^^^^^^^^^^^^^^^^^

The second change I made to the original ``.mod`` file (on line 2) was to add
the relative path to the `ols` folder containing the OLS routine that we will
write. Since this routine is not part of the official Dynare release, Dynare
will not actually take care of adding its folder to the Matlab path. Hence,
this line.

Third Modification
^^^^^^^^^^^^^^^^^^

On line 141, I add an equation tag to the monetary policy rule. This allows me
to select this equation by its equation tag and run OLS on it. I make sure not
to include any spaces in the equation tag name as the output of the OLS routine
is stored in a substructure of ``oo_.ols`` with the name of the equation
tag. Hence, here, the output will be stored in ``oo_.ols.taylor_rule``.

Fourth Modification
^^^^^^^^^^^^^^^^^^^

In Smets and Wouters (2007), potential output (``yf``) is calculated elsewhere
in the model. But, if we are to run OLS on the Taylor rule equation, we need
observations on this variable. Since that is not possible, I add a new equation
on line 143, ``ygap = y - yf``, replacing ``y-yf`` in the Taylor rule with
``ygap``. This allows me to estimate the model as before while providing
observed data on ``ygap`` for my OLS estimation (more on that later). NB: I
could have left ``y-yf`` in the equation and provided data for ``yf`` but this
change makes more clear that ``ygap`` is calculated differently for the
estimation run and the OLS estimation.

I further create two new parameters, ``crpiMcrpiXcrr`` and ``cryMcryXcrr``
because the parsing algorithm that I implemented in the OLS routine only
accounts for the situation where a single parameter multiplies one or more
endogenous variables. This change implies the changes on lines 76 and 77
defining their initial values, and on lines 222 and 223 defining them as
parameters to be estimated.

Finally, I redefine ``ms`` as an exogenous variable and remove the equation
that defined it as well as the definition of the variable ``em``.

Last Modification
^^^^^^^^^^^^^^^^^^

I load the data into a ``dseries`` called ``ds`` on line 234. As mentioned
above, I need data for ``ygap`` for the OLS estimation. This is obtained by
detrending the output series, as shown on line 235. I then call the OLS routine
on line 236, telling it to run OLS using the dataset ``ds`` on the equation
specified by the equation tag ``taylor_rule``.

As the OLS routine sets the parameter values it estimates in ``M_.params``, I
reset their initial values after the call to the routine on lines 237-240, in
preparation for the call to the estimation routine.


The OLS routine in Matlab: ``dyn_ols.m``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The OLS routine outlined herein was written in Matlab but could have just as
easily been written in Julia, Python, C, or the language of your choice. There
are three main steps involved in writing a routine that makes use of the Dynare
JSON output:

1. Parse the JSON file, loading it into a language-specific structure
2. Parse this structure for your purposes
3. Run your computational task, in our case estimation via OLS

Step 1: Parsing the JSON file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As JSON is widely supported, the first step is often straightforward,
regardless of your choice of programming language. In our case, though Matlab
doesn’t offer JSON support out of the box, there’s a widely-used and
well-tested toolbox called JSONlab that provides JSON support and is available
on the `Matlab File Exchange
<https://fr.mathworks.com/matlabcentral/fileexchange/33381-jsonlab--a-toolbox-to-encode-decode-json-files>`__.
Downloading JSONlab and adding it to our path allows us to access the model
block specified in just two lines:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 52

    jsonmodel = loadjson(jsonfile);
    jsonmodel = jsonmodel.model;

Line 52 reads in ``Smets_Wouters_2007_original.json`` (stored in the
``jsonfile`` variable) and loads it into a Matlab structure we call
``jsonmodel``. Line 53 then selects the ``model`` field as that is the only one
we’re interested in and overwrites ``jsonmodel`` with it. When finished,
``jsonmodel`` is a cell array with 40 entries, one for each equation. Entry 23
of this cell array corresponds to the monetary policy equation and looks like:

.. code:: matlab

    >> jsonmodel{23}

    ans =

      struct with fields:

         lhs: 'r'
         rhs: 'pinf*crpiMcrpiXcrr+cryMcryXcrr*ygap+crdy*diff(ygap)+crr*r(-1)+ms'
        line: 141
        tags: [1x1 struct]

As you can see, reading in the JSON code already gives us a lot of information;
we have string representations of the expressions on the left hand side, right
hand side, and equation tag(s) of each equation as well as the line number on
which the equation appeared in the ``.mod`` file. We are now ready to begin
parsing the equation in order to construct the matrices we will need to run
our OLS estimation.

Step 2: Parsing the model block
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below I describe the parsing algorithm that I implemented in a draft version of
``dyn_ols.m``. There may be speed improvements to be made and it certainly can
be made to be more general (we impose, for example, that a parameter can only
appear once per equation; a more general parsing algorithm would allow a
parameter to appear multiple times and simplify the equation). Though parsing
is done in Matlab, one could imagine writing a full parser using Bison and Yacc
to deal with parsing the equations. You could also imagine using an
out-of-the-box equation parser, modifying it to work with leads and lags. In
short, the correct solution depends on the problem that you are trying to
solve, the time you have to implement the solution, and the necessary
robustness of the solution.

Our ``dyn_ols`` routine allows the user to specify equation tags that will be
used to select the equations on which to run OLS. This functionality has been
split out into ``getEquationsByTags.m`` which takes the aforementioned
``jsonmodel`` cell array and the equation tags as arguments and returns
``jsonmodel`` containing only the equations corresponding to the specified
equation tags. The returned cellarray is in the same order as the equation tags
argument.

.. code-block:: matlab
    :linenos: inline

    function [jsonmodel] = getEquationsByTags(jsonmodel, tagname, tagvalue)
    %function [jsonmodel] = getEquationsByTags(jsonmodel, tagname, tagvalue)
    % Return the jsonmodel structure with the matching tags
    %
    % INPUTS
    %   jsonmodel       [cell array]    JSON representation of model block
    %   tagname         [string]        The name of the tag whos values are to
    %                                   be selected
    %   tagvalue        [string]        The values to be selected for the
    %                                   provided tagname
    %
    % OUTPUTS
    %   jsonmodel       [cell array]    JSON representation of model block,
    %                                   with equations removed that don't match
    %                                   eqtags
    %
    % SPECIAL REQUIREMENTS
    %   none

    % Copyright (C) 2017-2018 Dynare Team
    %
    % This file is part of Dynare.
    %
    % Dynare is free software: you can redistribute it and/or modify
    % it under the terms of the GNU General Public License as published by
    % the Free Software Foundation, either version 3 of the License, or
    % (at your option) any later version.
    %
    % Dynare is distributed in the hope that it will be useful,
    % but WITHOUT ANY WARRANTY; without even the implied warranty of
    % MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    % GNU General Public License for more details.
    %
    % You should have received a copy of the GNU General Public License
    % along with Dynare.  If not, see <http://www.gnu.org/licenses/>.

    assert(nargin == 3, 'Incorrect number of arguments passed to getEquationsByTags');
    assert(iscell(jsonmodel) && ~isempty(jsonmodel), ...
        'the first argument must be a cell array of structs');
    assert(ischar(tagname), 'Tag name must be a string');
    assert(ischar(tagvalue) || iscell(tagvalue), 'Tag value must be a string or a cell string array');

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
    end

Given the pared-down ``jsonmodel`` variable returned by
``getEquationsByTags.m``, we then enter a loop in ``dyn_ols.m`` with one
iteration for every equation (first setting a few variables that will be used
in the loop):

.. code-block:: matlab
    :linenos: inline
    :linenostart: 67

    M_endo_exo_names_trim = [M_.endo_names; M_.exo_names];
    [junk, idxs] = sort(cellfun(@length, M_endo_exo_names_trim), 'descend');
    regex = strjoin(M_endo_exo_names_trim(idxs), '|');
    mathops = '[\+\*\^\-\/\(\)]';
    for i = 1:length(jsonmodel)

The first thing we do upon entering the loop is ensure there are no leads in
the equation we want to estimate via OLS:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 73

        rhs_ = strsplit(jsonmodel{i}.rhs, {'+','-','*','/','^','log(','diff(','exp(','(',')'});
        rhs_(cellfun(@(x) all(isstrprop(x, 'digit')), rhs_)) = [];
        vnames = setdiff(rhs_, M_.param_names);
        if ~isempty(regexp(jsonmodel{i}.rhs, ...
                ['(' strjoin(vnames, '\\(\\d+\\)|') '\\(\\d+\\))'], ...
                'once'))
            error(['dyn_ols: you cannot have leads in equation on line ' ...
                jsonmodel{i}.line ': ' jsonmodel{i}.lhs ' = ' jsonmodel{i}.rhs]);
        end

Here, line 73 splits the equation by operator such that ``rhs_`` is a cell
array of parameter, endogenous, and exogenous names:

.. code:: matlab

    >> rhs_

    rhs_ =

      1x10 cell array

      Columns 1 through 7

        {'pinf'}    {'crpiMcrpiXcrr'}    {'cryMcryXcrr'}    {'ygap'}    {'crdy'}    {'ygap'}    {'crr'}

      Columns 8 through 10

        {'r'}    {'1'}    {'ms'}

Line 74 removes any constants that may remain in the equation. In our case, it
removes the lag on ``r``. Line 75 removes the parameter names, leaving us with
endogenous and exogenous variable names:

.. code:: matlab

    >> vnames

    vnames =

      1x4 cell array

        {'ms'}    {'pinf'}    {'r'}    {'ygap'}

Finally, the ``regexp`` command in the ``if`` statement on line 76 sees if any
of these variables appear in the original equation with a lead. If so, the
function ends with an error indicating the equation that contains the lead.

We next initialize a few variables and loop over the parameter names that
appear on the right-hand side of the equation at hand:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 83

        pnames = intersect(rhs_, M_.param_names);
        vnames = cell(1, length(pnames));
        splitstrings = cell(length(pnames), 1);
        X = dseries();
        for j = 1:length(pnames)

Our goal in this loop is to see which parameters appear in the equation,
thereby constructing the ``X`` matrix of the standard OLS equation
:math:`Y=X\beta+\varepsilon`. Upon entering the loop, we find the starting and
ending index of the parameter in the equation:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 88

            createdvar = false;
            pregex = [...
                mathops pnames{j} mathops ...
                '|^' pnames{j} mathops ...
                '|' mathops pnames{j} '$' ...
                ];
            [startidx, endidx] = regexp(jsonmodel{i}.rhs, pregex, 'start', 'end');
            assert(length(startidx) == 1);

Here, the regular expression we create on line 89 matches the given parameter
with mathematical operators appearing before, after, or both. Hence, for the
first parameter, ``crdy``, we have:

.. code:: matlab

    >> pregex

    pregex =

        '[\+\*\^\-\/\(\)]crdy[\+\*\^\-\/\(\)]|^crdy[\+\*\^\-\/\(\)]|[\+\*\^\-\/\(\)]crdy$'

    >> jsonmodel{i}.rhs

    ans =

        'pinf*crpiMcrpiXcrr+cryMcryXcrr*ygap+crdy*diff(ygap)+crr*r(-1)+ms'

    >> jsonmodel{i}.rhs(startidx:endidx)

    ans =

        '+crdy*'

Here, we see that it matches in the middle of the equation, being added to what
comes before it and multiplying what comes after it.

The next block of code deals with the various cases we can fall into,
depending on the mathematical operator(s) that are found before, after,
or both before and after, the parameter. We impose that parameters
multiply their regressors, and hence take action depending on the
location of ``*`` (in other words, our parsing algorithm does not
handle the case where a parameter divides, or is divided by, a
regressor):

.. code-block:: matlab
    :linenos: inline
    :linenostart: 96

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

In our case, given that the ``*`` operator appears after the parameter name, we
fall into the second ``elseif`` block.

The first thing we do here is call a helper function called
``getStrMoveRight``. This function returns the regressor
immediately to the right of the ``*``. Hence, the value returned is:

.. code-block:: matlab

    >> vnames{j}

    ans =

        'diff(ygap)'

This is the regressor that is multiplied by ``crdy``.

With the regressor name in hand, we are ready to add a column to our ``X``
matrix. This is done in the following bit of code:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 128

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

The regular expression on line 135 creates a string, ``'diff(ds.ygap)'`` which
is then evaluated, drawing the ``ygap`` variable from the dseries ``ds`` and
applying the ``dseries`` ``diff`` operator to it. Finally, this column is added
to ``X`` on line 138:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 138

            X = [X Xtmp];

The above loop is repeated for all of the parameters in the equation,
``crpiMcrpiXcrr``, ``cryMcryXcrr``, and ``crr``. Parsing for these parameters
is analogous to the parsing steps described above. Once the loop has been
completed, we have an ``X`` matrix with 4 columns, one for each regressor.
These are associated with the :math:`\beta` vector
``[crdy; crpiMcrpiXcrr; crr; cryMcryXcrr]``.

Having obtained our ``X`` matrix, we turn our attention to the ``Y``
vector. First we see if there were any regressors on the right-hand side
that were not multiplied by a parameter. If this is the case, we create
a ``dseries`` with their values and subtract them from the variable(s)
that appear on the left-hand side:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 141

        lhssub = getRhsToSubFromLhs(ds, jsonmodel{i}.rhs, regex, splitstrings, pnames);
        residuals = setdiff(intersect(rhs_, M_.exo_names), ds.name);
        assert(~isempty(residuals), ['No residuals in equation ' num2str(i)]);
        assert(length(residuals) == 1, ['More than one residual in equation ' num2str(i)]);

        Y = eval(regexprep(jsonmodel{i}.lhs, regex, 'ds.$&'));
        if ~isempty(lhssub)
            Y = Y - lhssub;
        end

By the time we have finished with this block, ``Y`` is a ``dseries``
with 1 column and 232 entries. We next find the first observed period and last
observed period in the estimation:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 151

        fp = max(Y.firstobservedperiod, X.firstobservedperiod);
        lp = min(Y.lastobservedperiod, X.lastobservedperiod);
        if isfield(jsonmodel{i}, 'tags') ...
                && isfield(jsonmodel{i}.tags, 'sample') ...
                && ~isempty(jsonmodel{i}.tags.sample)
            colon_idx = strfind(jsonmodel{i}.tags.sample, ':');
            fsd = dates(jsonmodel{i}.tags.sample(1:colon_idx-1));
            lsd = dates(jsonmodel{i}.tags.sample(colon_idx+1:end));
            if fp > fsd
                warning(['The sample over which you want to estimate contains NaNs. '...
                    'Adjusting estimation range to begin on: ' fp.char])
            else
                fp = fsd;
            end
            if lp < lsd
                 warning(['The sample over which you want to estimate contains NaNs. '...
                    'Adjusting estimation range to end on: ' lp.char])
            else
                lp = lsd;
            end
        end

We allow users to specify the sample range as an equation tag. If this
tag exists (line 154), we adjust the range to accord with that found in the sample
tag (lines 157-158). We adjust ``X`` and ``Y`` accordingly:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 173

        Y = Y(fp:lp);
        X = X(fp:lp).data;
        if ~isempty(lhssub)
            lhssub = lhssub(fp:lp);
        end

Thus, when parsing is finished, we will have constructed the ``Y``
vector and the ``X`` matrix of the standard OLS regression.

Step 3: Estimation via OLS
^^^^^^^^^^^^^^^^^^^^^^^^^^

Having obtained our ``Y`` vector and ``X`` matrix, we are now ready to run our
estimation, :math:`\hat{\beta} = (X'X)^{-1}X'Y`. [#]_ This is done on line 194:

.. code-block:: matlab
    :linenos: inline
    :linenostart: 188

        [nobs, nvars] = size(X);
        oo_.ols.(tag).dof = nobs - nvars;

        % Estimated Parameters
        [q, r] = qr(X, 0);
        xpxi = (r'*r)\eye(nvars);
        oo_.ols.(tag).beta = r\(q'*Y.data);
        oo_.ols.(tag).param_idxs = zeros(length(pnames), 1);
        for j = 1:length(pnames)
            oo_.ols.(tag).param_idxs(j) = find(strcmp(M_.param_names, pnames{j}));
            M_.params(oo_.ols.(tag).param_idxs(j)) = oo_.ols.(tag).beta(j);
        end

After this block, the estimated parameters will be in
``oo_.ols.taylor_rule.beta`` and will have been assigned to ``M_.params``. The
variable ``oo_.ols.taylor_rule.param_idxs`` shows the corresponding indices in
``M_.params``.

And that’s it! The rest of the code simply takes care of calculating the
various statistics and standard errors and displaying the estimated
parameters in a table:

.. code:: matlab

    OLS Estimation of equation 'taylor_rule' [name = 'taylor_rule']

        Dependent Variable: r
        No. Independent Variables: 4
        Observations: 231 from 1947Q2 to 2004Q4

                      Coefficients    t-statistic      Std. Error
                      ____________    ____________    ____________

        diff(ygap)         0.05632         4.09137         0.01377
        pinf               0.06233         2.69131         0.02316
        r(-1)              0.95707        59.38408         0.01612
        ygap               0.00874         2.75587         0.00317

        R^2: 0.942770
        R^2 Adjusted: 0.942014
        s^2: 0.043718
        Durbin-Watson: 1.703493
    ______________________________________________________________

We can now compare the parameters estimated via MLE to the parameters estimated
via OLS. The relevant lines from the estimation routine run by Dynare
(``mode_compute=4``) is:

.. code:: matlab

    crdy            0.125   0.1455  0.0190 norm 0.0500
    crpiMcrpiXcrr   1.500   0.2311  0.0246 norm 0.2500
    crr             0.750   0.9240  0.0199 beta 0.1000
    cryMcryXcrr     0.125   0.0199  0.0035 norm 0.0500

Though in this case the comparison between the OLS-estimated parameters and
those estimated via the Dynare ``estimation`` routine is not very useful, we
can imagine cases where this sort of comparison could be informative.

Conclusion
-----------------------

This was just one example of how Dynare's new JSON output can be exploited to
construct your own back end routines in the language of your choosing. It
essentially frees you from the Dynare back end and allows you to build your own
library routines while taking advantage of the Dynare modeling language.

We hope you find this development useful. If this has encouraged you to learn
more about Dynare, please don't hesitate to visit our `GitHub page
<https://github.com/DynareTeam/dynare/>`__ where you can find guidelines for
contributing. If you notice a bug in the JSON output, don't hesitate to report
it on the `Dynare-preprocessor Issues page
<https://github.com/DynareTeam/dynare-preprocessor/issues>`__. Again, as a
reminder, the JSON output will be available in the upcoming stable release of
Dynare 4.6.

.. [#] As matrix inversion is slow and numerically unstable for small values,
       we use the QR decomposition instead of using the standard formula:
       :math:`\hat{\beta} = R^{-1}Q'Y`.
