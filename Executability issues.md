# exe Bug

## No notebooks was found for this paper

### Reason 1. Page was not parsed or downloaded

R: we need to make changes in Exe to be notified and to fix parser.

Example, http://msystems.asm.org/content/2/2/e00191-16

### Reason 2. Notebook is in archive.

R: we need to implement decompressor.
S: there might be many archives, how can we easily check which of them contains notebook?

Example, ...

### Reason 3. Shortened / With redirects Links.

## Extension is not installed

?Double check this case

[A data set with kinematic and ground reaction forces of human balance](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5534162/)
https://github.com/demotu/datasets/blob/master/PDS/notebooks/PostureDataset.ipynb

```Python
#!pip install version_information
%load_ext version_information
```

## Not whole repository is cloned

R: tbd
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5534162/

https://github.com/ajouary/VR_Zebrafish/blob/master/Code/FishTracking.ipynb

## Too big data / Timeout on download

https://dx.doi.org/10.12688/f1000research.9110.1

## Didn't define Kernel / Old notebook format

http://nbviewer.jupyter.org/github/biocore/American-Gut/blob/master/ipynb/module2_v1.0.ipynb
https://github.com/DCPROGS/SCALCS/blob/master/notebooks/Calculate_Popen_SynapticCurrent_alpha1GlyR_Flip.ipynb


# Paper issues

## No notebooks was found for this paper

### Actually, no notebooks, indeed

## Not direct link mentioned in the paper

Example,
http://nbviewer.ipython.org/urls/raw.github.com/cschin/Write_A_Genome_Assembler_With_IPython/master/Write_An_Assembler.ipynb
vs
http://nbviewer.jupyter.org/github/cschin/Write_A_Genome_Assembler_With_IPython/blob/master/Write_An_Assembler.ipynb
(in this case platform changed URL)


# Dependencies issue

## Library can't be installed automatically or installed with errors


Example, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4670004/
*automatic error log:* ImportError: No module named 'py2cytoscape'
*Explanation:* 'C core' lib of 'igraph', which is lib of 'py2cytoscape' can't be installed. Look for details in the full log.

## Installation in Python should include validation

Correct declaration:

```Python
import pkgutil
import pip
if not pkgutil.find_loader("YourModuleName"):
   pip.main(['install', 'YourModuleName'])
import YourModuleName
```

*It would be nice to note versions of the modules in the comments for preservation purposes or use '==' and pip freeze. For example,*

```Python
pip install -I MySQL_python==1.2.2
```
https://stackoverflow.com/questions/5226311/installing-specific-package-versions-with-pip
https://pip.pypa.io/en/stable/reference/pip_freeze/

Example of wrong declaration:


## Installation in R should include validation

```R
if("RMySQL" %in% rownames(installed.packages()) == FALSE) {
  install.packages("RMySQL")
}
library(RMySQL)
```


## Outdated/deprecated mode

## Not working / buggy library

Example,
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5395614/
https://github.com/BlueBrain/nat/blob/master/notebooks/ThalamusStereology.ipynb
There is already issue: https://github.com/python-quantities/python-quantities/issues/128

## Not working external API

Example,
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5395614/
https://github.com/christian-oreilly/NIP_FENS2016/blob/master/Part3-Ontologies.ipynb
"KeyError: 'curie'
Try to reproduce manually in Jupyter: in response really no 'curie' attribute"
