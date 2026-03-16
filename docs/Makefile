# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
CONFIGDIR     = .

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" -c "$(CONFIGDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

livehtml:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" -c "$(CONFIGDIR)" $(SPHINXOPTS) $(O)
	@$(SPHINXBUILD) -b html -E -a "$(SOURCEDIR)" "$(BUILDDIR)/html" -c "$(CONFIGDIR)" $(SPHINXOPTS) $(O)
	@sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" -c "$(CONFIGDIR)" $(SPHINXOPTS) $(O)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" -c "$(CONFIGDIR)" $(SPHINXOPTS) $(O)
