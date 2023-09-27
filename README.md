# UGent Thesis LaTeX Template
A LaTeX template for a master's thesis at Ghent University.
This includes the UGent logo and the logo of the faculty.

## Requirements
A LaTeX distribution has to be present in the system `PATH` variable.
For example [TeX Live](https://www.tug.org/texlive/) or 
[TeXstudio](https://www.texstudio.org) for Windows, macOS and
various Linux distributions.

Required LaTeX packages to be present on the system:
- fancyhdr
- hyperref
- acronym
- graphicx
- titlesec
- geometry
- pdfpages
- babel
- xstring
- import
- parskip
- todonotes

## Editor
The repository can be opened in Visual Studio Code and will automatically
compile on file change using the `LaTeX Workshop` package.
The package can be installed using the package manager or simply run
`ext install latex-workshop` in VS Code Quick Open (`ctrl`/`cmd` + `P`).
The package will automatically compile the individual chapter you are working
on or the full project when the root [main](main.tex) file is open.

Another way is to use [Overleaf](https://www.overleaf.com) and upload the zip
to create a new project. To compile individual chapters, you can change the
main document file (click on the `menu`) to the
[main](chapters/example/main.tex) file of the individual chapter or appendix.
Currently Overleaf does not allow to independently change the main documents
for individual users, making collaboration only possible if both users are
working at the same chapter (and thus the same preview) or if they change
the main document each time they want to preview their changes.

If one users wants to work locally using Visual Studio Code, he first needs
to fork the repository at the latest stable version and the new Overleaf project
should be created from his forked repository instead of via zip file.

However I do not recommend using Overleaf for a big project like a thesis as
Overleaf will not be able to compile the full thesis if there are to many pages
and even individual chapters will start to take a long time even though the
chapter itself might be small.
Try to stick with TeX Live + Visual Studio Code + LaTeX Workshop for the best
experience.

## Example usage
An example [main.tex](main.tex) is supplied in the repository.

The [acknowledgements file](acknowledgements/content.tex) may not contain any
images or acronyms, just plain text, adding any additional parts would not fit
in the acknowledgements.

To create chapters, you have to copy the [example](chapters/example) folder and
rename it to the chapter title (or something else, it just needs to be matched
in the root [main](main.tex) file when including the chapter).
The [main](chapters/example/main.tex) file from the individual chapters don't
need to be modified. The same procedure is valid for the
[appendices](appendices/example).

A full example thesis (my own) can be found on the [UGent GitHub](https://github.ugent.be/aavdiere/masters-thesis)
and can be used as a reference.

## Outline
For the most part the [guidlines](https://www.ugent.be/ea/en/education/master-dissertation/note-lay-out-masters-dissertations.pdf/view)
of Ghent University (Faculty of Engineering and Architecture) have been obeyed.
The only difference is made in the page margins for double sided printing.

The proposed inner margin of 4cm is to large and has been reduced to 3cm, which
is still sufficient (if not better).
The proposed outer margin of 1cm is to narrow and has been increased to 2cm,
this to allow for space to hold the book without obstructing the text.

## Class options
- `twoside`: for recto-verso print, places empty page in between
    to force chapter to start at right page (default).
- `oneside`: for recto print, does not force chapters to start at right page.
- `bw`: forces cover page and title page logos in black and white.
- `english`: will show all headers and logos in English (default).
- `dutch`: will show all headers and logos in Dutch.
- `noindent`: this will load the `parskip` package and remove all the
    paragraph indents.
- `bachelor`: this will adapt the template for a bachelor's thesis.
- all other options are directly passed through to the `book` class.

## Variables
### Required
```tex
\title{}
\author{}
```

### Optional
Only the optional arguments that are used will show up in the final result.
```tex
\studentnumber{}
\date{}
\supervisor{}
\counsellor{}
\degree{}

\department{}
\chair{}
\faculty{}
\year{}

\acknowledgements{lorem.tex}
\abstract{abstract.tex}
\keywords{Digital to Analog Conversion,
          Digital to Optical Conversion,
          Digital Band Interleaving,
          Mach-Zehnder Modulator,
          Opto-Electronic Oscillator}
\extendedabstract{extended-abstract.pdf}
\acronyms[ACRO]{acronyms.acro}
\bibliographyfile{references}
```

The `faculty`should be one of the following:
- `bw`: Faculty of Bioscience Engineering
- `di`: Faculty of Veterinary Medicine
- `ea`: Faculty of Engineering and Architecture
- `eb`: Faculty of Economics and Business Administration
- `fw`: Faculty of Pharmaceutical Sciences
- `ge`: Faculty of Medicine and Health Sciences
- `lw`: Faculty of Arts and Philosophy
- `pp`: Faculty of Psychology and Educational Sciences
- `ps`: Faculty of Political and Social Sciences
- `rw`: Faculty of Law and Criminology
- `we`: Faculty of Sciences

Example files for [`abstract`](abstract.tex), [`extendedabstract`](extended_abstract.pdf),
[`acronyms`](acronyms.acro) and [`references`](references.bib) can also be found.
The file extensions for `abstract` and `acronyms` don't matter, but
`extendedabstract` expects a `.pdf` file while `references` expects a `.bib`
file (without the extension).

`acronyms` takes in an optional argument which it will use to line all acronyms
up.
You can put any letters there as it will only check the length of the argument.
Best practice is to pass the longest acronym.

## Commands
- `isdutch{true}{false}`: simple conditional overwrite
- `chapnumfont`: sets the font size and style for the chapter number
- `chaptitlefont`: sets the font size and style for the chapter title
- `blankpage`: inserts a blank page without any headers/footers
- `makecoverpage`: creates the cover page, with equal margins no matter
                   `oneside` or `twoside`. Will be followed by a completely
                   empty page (`twoside` only) as a cover is not printed on the
                   inside.
- `maketitlepage`: creates the title page, this does have different margins
                   depending on `oneside` or `twoside`. Will force the next page
                   to start on the right side by adding a blank page.
- `makeacknowledgements`: creates the acknowledgements page. Will force the next
                          page to start on the right side by adding a blank
                          page.
- `makeadmissiontoloan`: creates the admission to loan page. Will force the next
                         page to start on the right side by adding a blank page.
- `makeabstract`: creates the abstract from the earlier specified abstract file.
                  Will force the next page to start on the right side by adding 
                  a blank page.
- `makeextendedabstract`: imports the extended abstract for the earlier
                          specified PDF file. Will force the next page to start
                          on the right side by adding a blank page.
- `maketableofcontents`: inserts the table of contents. Will force the next page
                         to start on the right side by adding a blank page.
- `makelistoffigures`: inserts the list of figures. Will force the next page to
                       start on the right side by adding a blank page.
- `makelistoftables`: inserts the list of tables. Will force the next page to
                      start on the right side by adding a blank page.
- `makelistoffiguresandtables`: inserts the list of figures directly followed by
                                the list of tables without starting a new page.
                                Will force the next page to start on the right 
                                side by adding a blank page.
- `makelistofacronyms`: inserts the list of acronyms from the earlier specified
                        acronyms file. Will force the next page to start on the
                        right side by adding a blank page.
- `front`: command to load the style for the front of the dissertation. This
           will set the numbering format.
- `makefront`: a collection of all the `make` prefixed commands above. This
               saves the user the trouble of putting in each section manually.
               It will only load the supplied pages, e.g. if no acronyms file
               was given in the preamble, no list of acronyms will be generated.
- `body`: command to load the style for the body of the dissertation. This will
          set the numbering format as well as the header style.
- `makebibliography`: inserts the bibliography from the earlier specified bib
                      file. Will force the next page to start on the right side
                      by adding a blank page.
- `appendix`: command to load the style for the appendices of the dissertation.
              This will set the numbering format as well as the header style.
- `back`: command to load the style for the back of the dissertation. This will
          set the header style to empty.
- `makeback`: a collection of commands that will start the back of the
              dissertation and insert the blank page as well as the back cover
              page (empty page).

## License
This project is licensed under the Apache License - see the [LICENSE](LICENSE)
file for details
