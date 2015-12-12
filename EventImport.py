#!/usr/bin/env python
#############################################################
# EventImport.py 2015/12/09 Marcello Barisonzi
# Extract data from EventBrite csv file and import into db
#############################################################


import csv, sqlite3, os, sys, glob, codecs
from datetime import datetime
from OrganizationAliases import AliasDict

def event_info(r, conn):
    print("%(Event ID)s %(Event Name)s %(Date Attending)s" % r)
    event_id   = int(r["Event ID"])
    event_name = r["Event Name"]
    event_date = datetime.strptime(r["Date Attending"], "%b %d, %Y at %I:%M %p")
    
    c = conn.cursor()
    c.execute("SELECT * FROM event WHERE eventbrite_id=?", (event_id,))
    
    volunteer_call = False
    
    data = c.fetchall()
    
    if len(data)==0:
        print("Creating new event.")
        c.execute("INSERT INTO event VALUES (NULL, ?, ?, ?, 0)", (event_id, event_date, event_name))
    else:
        volunteer_call=bool(data[0][4])
        print("Event %s already exists." % event_id)
    
    return event_id, volunteer_call

def contact_info(r, conn, is_volunteer=False):
    
    is_volunteer |= (r["Organization ID"] == 1) 
    
    if is_volunteer:
        _type = "volunteer"
    else:
        _type = "contact"
        
    print("%(First Name)s %(Last Name)s %(Email)s" % r)
    
    first_name = r["First Name"].strip()
    last_name  = r["Last Name"].strip()
    
    # people don't know how to write their names...
    if first_name[0].islower() or first_name[-1].isupper():
        first_name = " ".join([i.capitalize() for i in first_name.split()])
    if last_name[0].islower() or last_name[-1].isupper():
        last_name  = " ".join([i.capitalize() for i in last_name.split()])
    email      = r["Email"].strip().lower()
    
    c = conn.cursor()
    c.execute("SELECT id FROM contact WHERE LOWER(email)=LOWER(?)", (email,))
    
    data = c.fetchall()
    contact_id = None
    
    if len(data)==0:
        print("Creating new %s." % _type)
#         "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,
#         "last_name" TEXT, 
#         "first_name" TEXT, 
#         "email" TEXT,
#         "title" TEXT, 
#         "responsible_id",
#         "organization_id", 
#         "role" TEXT, 
#         "category_id" INTEGER, 
#         "is_volunteer" BOOL,
#         "is_active" BOOL,
#         "notes" TEXT, 
        c.execute("INSERT INTO contact VALUES (NULL, ?, ?, ?, ?, NULL, ?, ?, NULL, ?, NULL, NULL)", (last_name, first_name, email, r["Prefix"], r["Organization ID"], r["Job Title"], bool(is_volunteer)))
    else:
        print("%s %s %s already exists." % (_type.capitalize(), first_name, last_name))
        contact_id = data[0][0]
    
    # get contact id
    if not contact_id:
        c.execute("SELECT id from contact WHERE LOWER(email)=LOWER(?)", (email,))
        contact_id = c.fetchone()[0]
    
    # create attendee relationship
    c.execute("INSERT INTO attendee VALUES (NULL, ?, ?)",  (int(r["Event ID"]), contact_id))
    
    return

def organization_info(r, conn):
    print("%(Company)s" % r)
    
    org = r["Company"].strip()
    
    r["Organization ID"] = None
    
    # strip some extra bullshit
    org = org.strip(".")
    org = org.strip(",")
    org = org.replace("Inc","").strip()
        
    #for i in AliasDict.keys():
    #    print("1>%s<< 2>%s<< %s %s %s" % (org, i, repr(org), repr(i), i==org))
    
    if org in AliasDict.keys():
        org = AliasDict[org]
    
    if org == "" or org == None:
        return None    
    
    print(repr(org))
    
    c = conn.cursor()
    c.execute("SELECT id FROM organization WHERE UPPER(name)=UPPER(?)", (org,))
    
    data = c.fetchall()
    organization_id = None
    
    if len(data)==0:
        print("Creating new organization.")
        c.execute("INSERT INTO organization VALUES (NULL, ?, NULL)", (org,))
    else:
        print("Organization %s already exists." % org)
        organization_id = data[0][0]
        
    if not organization_id:
        c.execute("SELECT id FROM organization WHERE UPPER(name)=UPPER(?)", (org,))
        organization_id = c.fetchone()[0]
        
    r["Organization ID"] = organization_id

        
    return organization_id

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
    
    csv_file = codecs.open(in_csv,"r","utf-8")
    reader = csv.DictReader(csv_file)

    event_id = None
    volunteer_call = False
    
    for r in reader:
        #print(r.keys())
        
        # Event info is run once per event
        if not event_id:
            event_id, volunteer_call = event_info(r, conn)
    
        organization_info(r, conn)
        
        contact_info(r, conn, volunteer_call)
    
    
    csv_file.close()
    
    conn.commit()
    conn.close()
    
    return

if __name__ == "__main__":
    main()