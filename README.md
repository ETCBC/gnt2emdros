**gnt2emdros 1.0**

Converts the [SBLGNT treebanks](https://github.com/biblicalhumanities/greek-new-testament/tree/master/syntax-trees/sblgnt) to a raw [Emdros](http://emdros.org) file (mql). Note: gnt2emdros (1.0) currently only works with the SBLGNT treebanks. Support for Nestle and lowfat versions is coming later.

RUN INSTRUCTIONS

First, edit the main.cfg file to specify the location of the input directory as well as the desired destination of output files:  
```input = /Users/User/github/gnt2emdros/input```  
You should also name the database under 'name.'

Second, note that the input directory should contain subdirectories (allowing multiple databases) which contain the files to be converted. The desired database is specified by referencing the subdirectory as a first position argument on run:  
```Python run.py SBL```

Place the XML files directly into the subdirectory. The program will retrieve and process all the files. Ensure that they are numbered so that the script pulls them in order. The program will print a live report of its activities as well as a final report on what was created in the mql file.

ADDITIONAL INSTRUCTIONS  
Once the final mql file is generated, the file can be given an SQLite3 backend for running queries in Emdros. This step requires an installation of Emdros with command line functions.

Simply run:  
```mql -b 3 SBL.mql```

You may then create a configuration file by following the instructions in the help manual included in Emdros under 'Help > Help Contents > Emdros Query Tool Users > Graphical version Users > Configuring the Program.'

Connect to the database configuration file and to the newly generated SQLite file. You are now ready for MQL queries in the Greek New Testament.
