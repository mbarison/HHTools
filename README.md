# HHTools

Tools to import/export/maintain the Hacking Health Contacts database.

* EventImport.py : import participants from EventBrite csv files


## Useful code snippet
EventBrite saves the reports with meaningless names. If you want to have it renamed e.g. by event ID, you can use this shell snippet:

        newname=`head -n 2 report-2015-12-09T1106.csv | tail -n 1 | sed 's/[^0-9]*\?,\([0-9]\+\),.*/\1/'`
        mv report-2015-12-09T1106.csv report_$newname.csv   