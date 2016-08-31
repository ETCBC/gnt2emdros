**sblgnt2emdros 1.0**

Converts the [SBLGNT treebanks](https://github.com/biblicalhumanities/greek-new-testament/tree/master/syntax-trees/sblgnt) to a raw [Emdros](http://emdros.org) file (mql).


RUN INSTRUCTIONS

First, edit the main.cfg file to specify the location of the input directory as well as the desired destination of output files. 

*ex: input = /Users/User/github/sblgnt2emdros/input*

Second, run sblgnt from command line using run.py with the desired input as a first position argument. The program will retrieve all xml files stored in the source directory.

*ex: Python '/Users/User/github/sblgnt2emdros/convert/run.py' GNT*

The program will generate a live report of its activities as well as a final report on what was created in the mql file.

Once the final mql file is generated, the file can be given an SQL lite 3 backend for running queries in Emdros. This step requires an installation of Emdros with command line functions.

Simply run 
*mql -b 3 SBLGNT.mql*

You may then create a configuration file by following the instructions in the help manual included in Emdros under 'Help > Help Contents > Emdros Query Tool Users > Graphical version Users > Configuring the Program.'

Connect to the database confirguration file and to the newly generated SQL lite file. You are now ready for MQL queries in the sblgnt.
