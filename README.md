# Using the Dynare Preprocessor’s JSON Output: An Example

This repository contains the code for the above-titled blog post on the [CEPREMAP Macro Observatory blog](https://macro.nomics.world/).

To build the blog post, simply do the following (after having installed Python, Pelican, and other dependencies):
 - `git clone --recurse-submodules --depth 1 https://github.com/houtanb/obsmacro-dynare-json.git`
 - `cd obsmacro-dynare-json && make`

To run the code described in the model, do the following:
 - `git clone --depth 1 https://github.com/houtanb/obsmacro-dynare-json.git`
 - Download the latest [snapshot of dynare](http://www.dynare.org/snapshot/) for your system. The code below will work with any version of Dynare newer than the version pointed to by the submodule in this repository.
 - Open Matlab or Octave and type:
   - `addpath <<path to dynare/matlab folder>>` where `dynare` points to the snapshot you downloaded
   - `addpath <<path to obsmacro-dynare-json/ols>>`
   - `cd <<path to obsmacro-dynare-json/afv2013table1/>>`
   - `dynare afv2013table1.mod`
