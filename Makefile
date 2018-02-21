PELICAN=pelican

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py

all: html

html: content/dynare-preprocessor-w-json.rst
	$(PELICAN) -o $(OUTPUTDIR) -s $(CONFFILE)

clean:
	[ ! -d $(OUTPUTDIR) ] || rm -rf $(OUTPUTDIR)
