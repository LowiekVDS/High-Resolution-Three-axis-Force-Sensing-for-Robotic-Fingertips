\def\fileversion{1}
\def\filedate{2019/05/11}

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ugent-thesis}[\filedate\space Version \fileversion\space by
  Achim Vandierendonck]

\def\studentnumber#1{\gdef\@studentnumber{#1}}
\def\supervisor#1{\gdef\@supervisor{#1}}
\def\counsellor#1{\gdef\@counsellor{#1}}
\def\degree#1{\gdef\@degree{#1}}
\def\department#1{\gdef\@department{#1}}
\def\chair#1{\gdef\@chair{#1}}
\def\academicyear#1{\gdef\@academicyear{#1}}

\def\acknowledgements#1{\gdef\@acknowledgements{#1}}
\def\abstract#1{\gdef\@abstract{#1}}
\def\extendedabstract#1{\gdef\@extendedabstract{#1}}
\def\keywords#1{\gdef\@keywords{#1}}

\def\bibliographyfile#1{\gdef\@bibliographyfile{#1}}

\newcommand{\isdutch}[2]{%
  \ifdutch%
    #1%
  \else%
    #2%
  \fi%
}
\newcommand{\ismaster}[2]{%
  \ifmaster%
    #1%
  \else%
    #2%
  \fi%
}

\newif\ifbw
\newif\ifenglish
\newif\ifdutch
\newif\ifmaster
\newif\iftwoside
\newif\ifnoindent
\englishtrue
\twosidetrue
\mastertrue

\DeclareOption{oneside}{
  \twosidefalse
  \PassOptionsToClass{oneside}{book}
}
\DeclareOption{bachelor}{
  \masterfalse
}
\DeclareOption{english}{
  \englishtrue
}
\DeclareOption{noindent}{
  \noindenttrue
}
\ifenglish
  \PassOptionsToClass{english}{book}
  \PassOptionsToPackage{english}{babel}
\fi
\DeclareOption{dutch}{
  \dutchtrue
  \PassOptionsToClass{dutch}{book}
  \PassOptionsToPackage{dutch}{babel} 
}
\DeclareOption{bw}{
  \bwtrue
}

\DeclareOption*{%
  \PassOptionsToClass{notitlepage}{book}%
  \PassOptionsToClass{\CurrentOption}{book}%
}
\ProcessOptions\relax
\LoadClass[a4paper]{book}

\PassOptionsToPackage{pdfpagelabels=false}{hyperref}
\PassOptionsToPackage{hidelinks}{hyperref}

\RequirePackage{fancyhdr}
\RequirePackage{hyperref}
\RequirePackage{acronym}
\RequirePackage{graphicx}
\RequirePackage{titlesec}
\RequirePackage{pdfpages}
\RequirePackage{babel}
\RequirePackage{xstring}
\RequirePackage{import}
\RequirePackage{todonotes}

\ifnoindent
  \RequirePackage{parskip}
\fi

\iftwoside
  \RequirePackage[top=2.5cm,bottom=2.5cm,inner=3cm,outer=2cm]{geometry}
  \reversemarginpar
  \setlength{\marginparwidth}{2.5cm}
\else
  \RequirePackage[margin=2.5cm]{geometry}
  \setlength{\marginparwidth}{2cm}
\fi

\def\faculty#1{%
  \gdef\@faculty{#1}%
  \ifdefined\@faculty
    \ifdutch
      \IfSubStr{#1}{bw}{\gdef\@fullfaculty{Faculteit Bio-Ingenieurswetenschappen}}{}
      \IfSubStr{#1}{di}{\gdef\@fullfaculty{Faculteit Diergeneeskunde}}{}
      \IfSubStr{#1}{ea}{\gdef\@fullfaculty{Faculteit Ingenieurswetenschappen en Architectuur}}{}
      \IfSubStr{#1}{eb}{\gdef\@fullfaculty{Faculteit Economie en Bedrijfskunde}}{}
      \IfSubStr{#1}{fw}{\gdef\@fullfaculty{Faculteit Farmaceutische Wetenschappen}}{}
      \IfSubStr{#1}{ge}{\gdef\@fullfaculty{Faculteit Geneeskunde en Gezondheidswetenschappen}}{}
      \IfSubStr{#1}{lw}{\gdef\@fullfaculty{Faculteit Letteren en Wijsbegeerte}}{}
      \IfSubStr{#1}{pp}{\gdef\@fullfaculty{Faculteit Psychologie en Pedagogische Wetenschappen}}{}
      \IfSubStr{#1}{ps}{\gdef\@fullfaculty{Faculteit Politieke en Sociale Wetenschappen}}{}
      \IfSubStr{#1}{rw}{\gdef\@fullfaculty{Faculteit Recht en Criminologie}}{}
      \IfSubStr{#1}{we}{\gdef\@fullfaculty{Faculteit Wetenschappen}}{}
    \else
      \IfSubStr{#1}{bw}{\gdef\@fullfaculty{Faculty of Bioscience Engineering}}{}
      \IfSubStr{#1}{di}{\gdef\@fullfaculty{Faculty of Veterinary Medicine}}{}
      \IfSubStr{#1}{ea}{\gdef\@fullfaculty{Faculty of Engineering and Architecture}}{}
      \IfSubStr{#1}{eb}{\gdef\@fullfaculty{Faculty of Economics and Business Administration}}{}
      \IfSubStr{#1}{fw}{\gdef\@fullfaculty{Faculty of Pharmaceutical Sciences}}{}
      \IfSubStr{#1}{ge}{\gdef\@fullfaculty{Faculty of Medicine and Health Sciences}}{}
      \IfSubStr{#1}{lw}{\gdef\@fullfaculty{Faculty of Arts and Philosophy}}{}
      \IfSubStr{#1}{pp}{\gdef\@fullfaculty{Faculty of Psychology and Educational Sciences}}{}
      \IfSubStr{#1}{ps}{\gdef\@fullfaculty{Faculty of Political and Social Sciences}}{}
      \IfSubStr{#1}{rw}{\gdef\@fullfaculty{Faculty of Law and Criminology}}{}
      \IfSubStr{#1}{we}{\gdef\@fullfaculty{Faculty of Sciences}}{}
    \fi
  \fi
}

\newcommand*\chapnumfont{\normalfont\Huge}
\newcommand*\chaptitlefont{\normalfont\Huge\bfseries}

\newlength\beforechapskip
\setlength\beforechapskip{18mm}

\newlength\midchapskip
\setlength\midchapskip{\paperwidth}
\addtolength\midchapskip{-\textwidth}
\addtolength\midchapskip{-\oddsidemargin}
\addtolength\midchapskip{-1in}

\titleformat{\chapter}[display]
  {\normalfont\filleft}
  {%
    \resizebox{!}{\beforechapskip}{\chapnumfont\vphantom{A}\thechapter}%
    \makebox[0pt][l]{%
      \hspace{1.6em}%
      \rule{\midchapskip}{\beforechapskip}%
    }%
  }
  {25pt}
  {\chaptitlefont}
\titlespacing*{\chapter}
  {0pt}{0pt}{1.5cm}

%\setlength{\voffset}{0.8cm}
%\setlength{\headheight}{0.5cm}
%\setlength{\headsep}{1cm}

\fancypagestyle{custom}{
  \fancyhf{}
  \iftwoside
    \fancyhead[RO]{\rightmark\hphantom{hhh}\thepage}
    \fancyhead[LE]{\thepage\hphantom{hhh}\leftmark}
  \else
    \fancyhead[R]{\thepage}
    \fancyhead[L]{\rightmark}
  \fi
}

\fancypagestyle{appendix}{
  \fancyhf{}
  \iftwoside
    \fancyhead[RO]{\rightmark\hphantom{hhh}\thepage}
    \fancyhead[LE]{\thepage\hphantom{hhh}\leftmark}
  \else
    \fancyhead[R]{\thepage}
    \fancyhead[L]{\leftmark}
  \fi
}

\newcommand{\acronyms}[2][1]{
  \gdef\@acronymsize{#1}
  \gdef\@acronyms{#2}
}

\newcommand*{\blankpage}{%
  \thispagestyle{empty}%
  \vspace*{\fill}{%
    \centering%
    \textit{%
    \isdutch{Deze pagina is opzettelijk leeg gelaten}
            {This page is intentionally left blank.}%
    }\par%
    \vspace{1cm}
  }%
  \vspace{\fill}%
  \newpage%
}

\renewcommand*{\cleardoublepage}{%
  \clearpage%
  \iftwoside
    \ifodd\c@page%
    \else%
      \blankpage%
      \if@twocolumn\hbox{}\newpage\fi%
    \fi
  \fi
}

\ifdutch
  \ifbw
    \gdef\@logopath{./logo/dutch/bw}
  \else
    \gdef\@logopath{./logo/dutch/rgb}
  \fi
\else
  \ifbw
    \gdef\@logopath{./logo/english/bw}
  \else
    \gdef\@logopath{./logo/english/rgb}
  \fi
\fi

\addto\captionsenglish{
  \renewcommand{\contentsname}%
    {Table of Contents}%
}

\renewcommand{\maketitle}{%
  \begin{figure}%
    \ifdefined\@faculty
      \includegraphics[trim={0.7cm 0cm 0cm 0cm},width=0.6\textwidth]{%
        \@logopath/\@faculty%
      }%
    \else
      \phantom{\includegraphics[trim={0.7cm 0cm 0cm 0cm},width=0.8\textwidth]{%
        \@logopath/ea%
      }}%
    \fi
    \par%
  \end{figure}%
  {\setlength{\parindent}{0cm}%
  \vspace*{2cm}%
  {\huge\textsc{\@title}}\par%
  \vspace{0.4cm}%
  {\Large\textsc{\@author}}\par%
  \ifdefined\@studentnumber%
    {\textsc{\isdutch{Studentennummer}{Student number}: \@studentnumber}}\par%
  \else%
    \phantom{{\textsc{Student number:}}}\par%
  \fi%
  \vspace{2cm}%
  \ifdefined\@supervisor%
    \isdutch{Promotor}{Supervisor}: \@supervisor
  \else%
    \phantom{Supervisor:}%
  \fi%
  \par%
  \ifdefined\@counsellor%
    \isdutch{Begeleider}{Counsellor}: \@counsellor
  \else%
    \phantom{Counsellor:}%
  \fi%
  \par%
  \vspace{0.5cm}%
  \ifdefined\@degree%
    \isdutch{\ismaster{Master}{Bachelor}proef ingediend tot het behalen van de academische graad van}
    {\ismaster{Master}{Bachelor}'s dissertation submitted in order to obtain the academic degree of}
    \@degree%
  \else%
    \phantom{\ismaster{Master}{Bachelor}'s dissertation submitted in order to obtain the academic
    degree of \ismaster{Master}{Bachelor} of Science in XXX}%
  \fi
  \par%
  \vfill%
  \begin{minipage}{5cm}%
    \includegraphics*[trim={0.7cm 0cm 0cm 0cm},width=\textwidth]{%
      \@logopath/ugent%
    }%
  \end{minipage}\hfill%
  \begin{minipage}{9cm}%
    \begin{flushright}%
      \ifdefined\@department%
        \isdutch{Vakgroep}{Department of} \@department%
      \else
        \phantom{Department of Xxxxxxxxxxx Xxxxxxxxxx}%
      \fi
      \par%
      \ifdefined\@chair%
        \isdutch{Voorzitter}{Chair}: \@chair%
      \else
        \phantom{Chair: Prof. dr. ir. Xxxx Xxxxxx}%
      \fi
      \par%
      \ifdefined\@fullfaculty%
        \@fullfaculty%
      \else
        \phantom{Faculty of Xxxxxxxxxxx xxx Xxxxxxxxxxxx}%
      \fi
      \par%
      \ifdefined\@academicyear%
        \isdutch{Academiejaar}{Academic year} \@academicyear%
      \else
        \phantom{Academic year}%
      \fi
    \end{flushright}%
  \end{minipage}%
  }%
}
\newcommand{\makecoverpage}{%
  \pagestyle{empty}%
  \newgeometry{margin=2.5cm}%
  \maketitle%
  \clearpage%
  \restoregeometry%
  \iftwoside%
    \null%
    \clearpage%
  \fi
  \pagestyle{plain}%
}
\newcommand{\maketitlepage}{%
  \pagestyle{empty}%
  \maketitle%
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
  \pagestyle{plain}%
}
\newcommand{\makeacknowledgements}{%
  \phantomsection%
  \addcontentsline{toc}{chapter}{\isdutch{Dankwoord}{Acknowledgements}}%
  \chapter*{\isdutch{Dankwoord}{Acknowledgements}}%
  \input{\@acknowledgements}%
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
}
\newcommand{\makeadmissiontoloan}{%
  \phantomsection%
  \addcontentsline{toc}{chapter}{%
    \isdutch{Toegang tot bruikleen}{Admission to loan}%
  }%
  \ifdutch%
  \else%
    \chapter*{Admission to loan}
    ``The author(s) gives (give) permission to make this \ismaster{master}{bachelor} dissertation available for consultation and to copy parts of this \ismaster{master}{bachelor}’s dissertation for personal use. In the case of any other use, the copyright terms have to be respected, in particular with regard to the obligation to state expressly the source when quoting results from this \ismaster{master}{bachelor} dissertation.''
    
    {\let\clearpage\relax\chapter*{}}%
    {\let\clearpage\relax\chapter*{}}%
  \fi

  {\let\clearpage\relax\chapter*{Toegang tot bruikleen}}
  ``De auteur(s) geeft (geven) de toelating dit afstudeerwerk voor consultatie beschikbaar te stellen en delen van het afstudeerwerk te kopi\"eren voor persoonlijk gebruik. Elk ander gebruik valt onder de beperkingen van het auteursrecht, in het bijzonder met betrekking tot de verplichting de bron uitdrukkelijk te vermelden bij het aanhalen van resultaten uit dit afstudeerwerk.''

  {\let\clearpage\relax\chapter*{}}%
  \@author, \@date
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
}
\newcommand{\makeabstract}{%
  \phantomsection%
  \addcontentsline{toc}{chapter}{Abstract}%
  \chapter*{\@title}%
  \begin{center}
    \large \isdutch{door}{by} \par
    \textsc{\@author}\par\vspace{0.4cm}
    \ifdefined\@degree%
      \isdutch{\ismaster{Master}{Bachelor}proef ingediend tot het behalen van de academische graad van}
      {\ismaster{Master}{Bachelor}'s dissertation submitted in order to obtain the academic degree of}
      \@degree%
    \else%
      \phantom{\ismaster{Master}{Bachelor}'s dissertation submitted in order to obtain the academic
      degree of \ismaster{Master}{Bachelor} of Science in XXX}%
    \fi
    \par\vspace{0.4cm}
    \ifdefined\@supervisor%
      \isdutch{Promotor}{Supervisor}: \@supervisor
    \else%
      \phantom{Supervisor:}%
    \fi%
    \par
    \ifdefined\@counsellor%
      \isdutch{Begeleider}{Counsellor}: \@counsellor
    \else%
      \phantom{Counsellor:}%
    \fi%
    \par\vspace{0.8cm}
    \ifdefined\@faculty%
      \@fullfaculty%
    \else
      \phantom{Faculty of Xxxxxxxxxxx xxx Xxxxxxxxxxxx}%
    \fi
    \par
    \isdutch{Universiteit Gent}{Ghent University}%
    \par\vspace{0.4cm}
    \ifdefined\@department%
      \isdutch{Vakgroep}{Department of} \@department%
    \else
      \phantom{Department of Xxxxxxxxxxx Xxxxxxxxxx}%
    \fi
    \par
    \ifdefined\@chair%
      \isdutch{Voorzitter}{Chair}: \@chair%
    \else
      \phantom{Chair: Prof. dr. ir. Xxxx Xxxxxx}%
    \fi
    \par
  \end{center}
  \vfill
  \textbf{Abstract} - \input{\@abstract}
  \par\vspace{0.4cm}%
  \ifdefined\@keywords%
    \noindent\textbf{\isdutch{Kernwoorden}{Keywords}} - \@keywords
  \else
    \phantom{\noindent\textbf{\isdutch{Kernwoorden}{Keywords}} - }
  \fi
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
}
\newcommand{\makeextendedabstract}{%
  \phantomsection%
  \addcontentsline{toc}{chapter}{\isdutch{Uitgebreid abstract}{Extended Abstract}}%
  \includepdf[pages=-]{\@extendedabstract}
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
}
\newcommand{\maketableofcontents}{%
  \phantomsection%
  \addcontentsline{toc}{chapter}{\isdutch{Inhoudsopgave}{Table of Contents}}%
  \tableofcontents%
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
}
\newcommand{\makelistoffigures}{%
  \phantomsection%
  \addcontentsline{toc}{chapter}{\isdutch{Lijst van figuren}{List of Figures}}%
  \listoffigures%
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
}
\newcommand{\makelistoftables}{%
  \phantomsection%
  \addcontentsline{toc}{chapter}{\isdutch{Lijst van tabellen}{List of Tables}}%
  \listoftables%
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
}
\newcommand{\makelistoffiguresandtables}{%
  \begingroup%
  \let\clearpage\relax%
  \let\cleardoublepage\relax%
  \phantomsection%
  \addcontentsline{toc}{chapter}{\isdutch{Lijst van figuren}{List of Figures}}%
  \listoffigures%
  \vspace{2cm}
  \phantomsection%
  \addcontentsline{toc}{chapter}{\isdutch{Lijst van tabellen}{List of Tables}}%
  \listoftables%
  \endgroup%
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
}
\newcommand{\makelistofacronyms}{%
  \phantomsection%
  \chapter*{\isdutch{Lijst met Acroniemen}{List of Acronyms}}%
  \addcontentsline{toc}{chapter}{\isdutch{Lijst met Acroniemen}{List of Acronyms}}%
  \begin{acronym}[\@acronymsize]%
    \input{\@acronyms}%
  \end{acronym}%
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
}

\newcommand*{\front}{\pagenumbering{roman}\pagestyle{plain}}
\newcommand{\makefront}{%
  \pagenumbering{roman}%
  \makecoverpage%
  \blankpage\cleardoublepage%
  \maketitlepage%
  \ifdefined\@acknowledgements%
    \makeacknowledgements%
  \fi%
  \makeadmissiontoloan%
  \ifdefined\@abstract%
    \makeabstract%
  \fi%
  \ifdefined\@extendedabstract%
    \IfFileExists{\@extendedabstract}{\makeextendedabstract}{}%
  \fi%
  \maketableofcontents%
  \makelistoffiguresandtables%
  \ifdefined\@acronyms%
    \makelistofacronyms
  \fi
}
\newcommand*{\body}{\pagenumbering{arabic}\pagestyle{custom}}
\let\appendixOld\appendix
\renewcommand{\appendix}{%
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
  \appendixOld%
  \pagestyle{appendix}%
  \thispagestyle{plain}%
}
\newcommand{\makebibliography}{%
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
  \phantomsection%
  \addcontentsline{toc}{chapter}{Bibliography}%
  \bibliographystyle{ieeetr}%
  \bibliography{\@bibliographyfile}%
  \iftwoside%
    \cleardoublepage%
  \else%
    \clearpage%
  \fi%
}
\newcommand{\back}{\cleardoublepage\pagestyle{empty}}
\newcommand{\makeback}{%
  \cleardoublepage%
  \pagestyle{empty}
  \blankpage\cleardoublepage%
  \null\newpage
}