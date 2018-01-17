PY?=python
PELICAN?=pelican
PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py

DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

html: content/dynare-preprocessor-w-json.md
	$(PELICAN) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS) $(INPUTDIR)
