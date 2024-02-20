rst_files := $(patsubst %.ipynb,../docstrings/%.rst,$(wildcard *.ipynb))
export MPLBACKEND := module://matplotlib_inline.backend_inline

docstrings: ${rst_files}

../docstrings/%.rst: %.ipynb
	../../tools/nb_to_doc.py $*.ipynb ../docstrings
	@if [ -f ../generated/escodrinyar.$*.rst ]; then \
	    touch ../generated/escodrinyar.$*.rst; \
	 fi

clean:
	rm -rf ../docstrings