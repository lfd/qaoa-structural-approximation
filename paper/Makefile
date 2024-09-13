
.PHONY: clean watch all figures

BUILD_DIR := build
CREATE_BUILD_DIR := $(BUILD_DIR)/.create_dir
BUILD_BIB := $(BUILD_DIR)/.bib
#FIGURES := figures/f_components_even.pdf figures/ck_components.pdf
FIGURES_DIR := figures
FIGURES := $(addprefix figures/R/, landscapes_facets.pdf ck_components.pdf clustering_dims.pdf qrf.pdf  uniform_analytic.pdf sat_cross_section.pdf circopt_vs_preopt.pdf circopt_vs_preopt_sat.pdf circopt_landscape.pdf)
TIKZ_FIGURES := $(addprefix figures/tikz/, kclique_DH.pdf qaoa_iterative.pdf qaoa_novel.pdf structure.pdf)
FIGURE_PDFS := $(foreach f,$(FIGURES),$(FIGURES_DIR)/$(f).pdf)

WATCH_FILES := *.tex figures/R/*.R figures/tikz/*.tex

R := Rscript
LATEX := pdflatex #lualatex
FIG_LATEX := lualatex
LATEX_FLAGS := --halt-on-error --output-directory=$(BUILD_DIR)
BASH := bash

#main.pdf: $(FIGURE_PDFS) $(CREATE_BUILD_DIR) $(BUILD_BIB)  main.tex 
main.pdf: $(CREATE_BUILD_DIR) $(BUILD_BIB) main.tex content.tex  $(FIGURES) 
	$(LATEX) $(LATEX_FLAGS) main.tex
	cp build/main.pdf main.pdf


$(CREATE_BUILD_DIR): 
	if [ -d "build" ]; then touch $(CREATE_BUILD_DIR); else mkdir build ; touch $(CREATE_BUILD_DIR); fi
	
$(BUILD_BIB): main.bib $(CREATE_BUILD_DIR)
	if [ ! -d "build/main.aux" ]; then $(LATEX) $(LATEX_FLAGS) main.tex ; fi
	cp build/mainNotes.bib .
	bibtex build/main
	$(LATEX) $(LATEX_FLAGS) main.tex
	$(LATEX) $(LATEX_FLAGS) main.tex
	touch $(BUILD_BIB)
	rm ./mainNotes.bib

#### TIKZ
figures/tikz/%.pdf: figures/tikz/%.tex
	$(FIG_LATEX) $(LATEX_FLAGS) $?
	cp build/$(notdir $@) $(FIGURES_DIR)/tikz

#### FIGURES

figures: $(FIGURES) $(TIKZ_FIGURES)


figures/R/%.pdf: $(BUILD_DIR)/figures/R/%.tex
	$(FIG_LATEX) $(LATEX_FLAGS) $(BUILD_DIR)/figures/R/$(basename $(notdir $@)).tex
	cp $(BUILD_DIR)/$(basename $(notdir $@)).pdf $(FIGURES_DIR)/R

$(BUILD_DIR)/figures/R/%.tex: figures/R/%.R figures/R/util.R
	$(R) figures/R/$(basename $(notdir $@)).R
	mkdir -p $(BUILD_DIR)/figures/R
	mv $(basename $(notdir $@)).tex $(BUILD_DIR)/figures/R

#### WATCH

watch:
	$(BASH) watch.sh $(WATCH_FILES)

#### CLEAN

clean:
	rm -r build main.pdf
	#$(MAKE) clean -C figures
	rm $(FIGURES_DIR)/R/*.pdf
	rm $(FIGURES_DIR)/tikz/*.pdf


clean-build:
	rm -r build 
