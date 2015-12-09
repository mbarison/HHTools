#!/usr/bin/env python
#############################################################
# EventImport.py 2015/12/09 Marcello Barisonzi
# Extract data from EventBrite csv file and import into db
#############################################################


import csv, sqlite3, os, sys, glob
from datetime import datetime

def event_info(r, conn):
    print("%(Event ID)s %(Event Name)s %(Date Attending)s" % r)
    event_id   = r["Event ID"]
    event_name = r["Event Name"]
    event_date = datetime.strptime(r["Date Attending"], "%b %d, %Y at %I:%M %p")
    
    c = conn.cursor()
    c.execute("SELECT * FROM event WHERE eventbrite_id=?", (event_id,))
    
    if len(c.fetchall())==0:
        print("Creating new event.")
        c.execute("INSERT INTO event VALUES (NULL, ?, ?, ?)", (event_id, event_date, event_name))
    else:
        print("Event %s already exists." % event_id)
    
    return

def main():
    # get the input files
    if len(sys.argv) != 3:
        print("USAGE: EventImport.py <sqlite_file> <event_file>")
        sys.exit(666)
        
    # let's not be bothered by the file order
    if ".csv" == sys.argv[1][-4:]:
        in_csv = sys.argv[1]
    elif ".csv" == sys.argv[2][-4:]:
        in_csv = sys.argv[2]        
    if ".sqlite" == sys.argv[1][-7:]:
        in_sql = sys.argv[1]
    elif ".sqlite" in sys.argv[2][-7:]:
        in_sql = sys.argv[2]       
    
    print(os.path.exists(in_sql))
    print(datetime.today().strftime("%b %d, %Y at %I:%M %p"))
    
    conn = sqlite3.connect(in_sql)
    
    csv_file = open(in_csv)
    reader = csv.DictReader(csv_file)

    run_once = True
    
    for r in reader:
        #print(r.keys())
        
        # Event info is run once per event
        if run_once:
            event_info(r, conn)
            run_once = False
    
    csv_file.close()
    
    conn.commit()
    conn.close()
    
    return

if __name__ == "__main__":
    main()