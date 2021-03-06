'''
Created on 20 Jan. 2019

@author: Byron Wilson

This load script is to create a Schedule of Units Database in Neo4j from scratch. Master data only. Pre and Co requsites
still need to be created. This is handled with SOU_Linker

'''
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "test123"

sou = {}  # main dictionary that holds all the records. Each record is a dictionary of fields. Each field is either a value or a dictionary of values etc...
ListOfAreas = []  # List of Areas that a course may have as including values
ListOfDegrees = []  # list of degrees offered that can be part of a pre-requisite


def canonUnit(unit):
    'Reformats the Unit Code to remove spaces like for HRM 107 '
    #    print("CanonUnit(" + unit + ")")
    if not (isValidUnit(unit.upper())):
        #       print("Unit not valid in canonUnit")
        return ""
    if unit[3] == " ":
        unit = unit[0:2] + unit[4:6]
    return unit


def isValidUnit(unit):
    'Checks the length of the unit code, the alpha and numeric parts for validity'
    if len(unit) == 7:
        if not (unit[0:2].isupper()):
            return False
        if not (unit[3].isupper()) and unit[3] != " ":
            return False
        return unit[4:6].isdigit()
    if len(unit) == 6:  # old style three letter/three number units
        if not (unit[0:2].isupper()):
            return False
        return unit[3:5].isdigit()
    return False


def readValue(f, field):
    s = ""
    inQuotes = False
    while True:
        c = f.read(1)
        if len(c) == 0:
            return (s, 2)  # 2 signifies the end of the file, end of input
        if c == b'"':
            inQuotes = not (inQuotes)  # If quotes found, check variable and flick to True if starts at False
        elif c == b'\r' and inQuotes == False:
            return (s, 1)  # Question: does the 1 do anything? , end of line
        elif c == b'\r' and inQuotes:
            s = s + "|"  # insert pipe if there is line break
        else:
            if c == b',' and inQuotes == False:
                return (s, 0)  # end of a field
            #          print(c)
            if (c == b',') and inQuotes and field != "Name":
                s = s + " or "  # add in 'or' to field name
            elif c != b'\n' and c[0] < 128:
                s = s + c.decode("utf-8")


def addUnitField(f, ud, field):
    v, r = readValue(f, field)
    if r != 2:
        ud[field] = v
    return r


def readUnit(f):
    ud = {}  # dictionary for this unit
    addUnitField(f, ud, "Scope")
    addUnitField(f, ud, "Code")
    addUnitField(f, ud, "Name")
    addUnitField(f, ud, "Credit")
    addUnitField(f, ud, "Designation_Str")
    addUnitField(f, ud, "Type")
    addUnitField(f, ud, "Prereq_Str")
    addUnitField(f, ud, "Coreq_Str")
    addUnitField(f, ud, "NCCW_Str")
    addUnitField(f, ud, "When")
    addUnitField(f, ud, "Attend")
    addUnitField(f, ud, "Dept")
    addUnitField(f, ud, "PF")
    addUnitField(f, ud, "CoTaught")
    addUnitField(f, ud, "CoLo")
    addUnitField(f, ud, "Quota")
    addUnitField(f, ud, "SONIA")
    v, r = readValue(f, "")
    v, r = readValue(f, "")
    v, r = readValue(f, "")
    v, r = readValue(f, "")
    return ud, r


def readScheduleOfUnits(fileName):
    with open(fileName, "rb") as f:
        r = 0
        while r != 2:  # 2 is being used to stop reading file
            ud, r = readUnit(f)  # ud is a line from the csv mapped to field names and r is return code
            if r != 2:
                unit = canonUnit(ud["Code"])  # Check if the value mapped to the field "Code" is a valid code
                if len(unit) != 0:  # If the check returns a code of any length. Write it to the sou variable
                    if unit in sou:
                        if ud["Prereq_Str"] != "":
                            # we can have multiple lines for the same unit for multiple changes (sigh!)
                            print("Duplicate Unit: " + unit)
                    else:
                        #                        print("Adding Unit " + unit)
                        sou[unit] = ud


def readScheduleOfDegrees(fileName):
    with open(fileName) as f:
        for line in f:
            ListOfDegrees.append(line.strip().lower())


def readAreasOfUnits(fileName):
    with open(fileName) as f:
        for line in f:
            ListOfAreas.append(line.strip().lower())


def main():
    readScheduleOfDegrees("degrees.txt")
    readAreasOfUnits("areas.txt")
    readScheduleOfUnits("units.csv")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Delete all nodes in the test database
    with driver.session() as session:
        session.run("match (n)"
                    "detach delete n")

    # === skip for now ========================================================================
    # with driver.session() as session:
    #     UnqCon = "CREATE CONSTRAINT ON {node} ASSERT {Field} IS UNIQUE"
    #     session.run(UnqCon, {"node": "(u:Unit)","field":"u.Code"})
    #     session.run(UnqCon, {"node": "(us:Unit_Scope)","field":"us.Scope"})
    #     session.run(UnqCon, {"node": "(ud:Unit_Designation)","field":"ud.Designation"})
    #     session.run(UnqCon, {"node": "(ut:Unit_Type)","field":"ut.Type"})
    #     session.run(UnqCon, {"node": "(wo:Offering)","field":"wo.Session"})
    #     session.run(UnqCon, {"node": "(d:Department)","field":"d.Name"})
    #     session.run(UnqCon, {"node": "(f:Faculty)","field":"f.Name"})                    
    # ===========================================================================

    with driver.session() as session:
        'Create Unit Nodes with code, name and credit point attributes'
        statement = "MERGE (u:Unit {Code: {Code}, Name: {Name}, Credit_Points: {Credit_Points}, Pass_Fail: {PF}})"
        for v in sou.values():
            session.run(statement, {"Code": v['Code'], "Name": v['Name'], "Credit_Points": v['Credit'], "PF": v['PF']})

    # ===========================================================================
    # with driver.session() as session:
    #     'Set unit nodes property Pass_Fail'
    #     statement = ("MATCH (u:Unit {Code:{Code}})"
    #                  "SET u.`Pass/Fail` = {PF}")
    #     for v in sou.values():
    #         session.run(statement,{"Code": v['Code'], "PF": v['PF']})        
    # ===========================================================================
    with driver.session() as session:
        'Create Scope Nodes'
        statement = "MERGE (us:Unit_Scope {Scope:{Scope}})"
        for v in sou.values():
            session.run(statement, {"Scope": v['Scope']})

    with driver.session() as session:
        'link it to existing unit nodes'
        statement = ("MATCH (us:Unit_Scope {Scope:{Scope}}),(u:Unit {Code:{Code}})"
                     "MERGE (u)-[:IS_SCOPE]->(us)")
        for v in sou.values():
            session.run(statement, {"Scope": v['Scope'], "Code": v['Code']})

    with driver.session() as session:
        'Create and link unit type nodes to units'
        statement = "MERGE (ut:Unit_Type {Type:{Type}})"
        for v in sou.values():
            if v['Type'] != '':
                session.run(statement, {"Type": v['Type']})

        statement = ("MATCH (ut:Unit_Type {Type:{Type}}),(u:Unit {Code:{Code}})"
                     "MERGE (u)-[:IS_TYPE]->(ut)")
        for v in sou.values():
            if v['Type'] != '':
                session.run(statement, {"Type": v['Type'], "Code": v['Code']})

    with driver.session() as session:
        'Create and link Departments'
        statement = "MERGE (d:Department {Name:{Name}})"
        for v in sou.values():
            session.run(statement, {"Name": v['Dept']})

        statement = ("MATCH (d:Department {Name:{Name}}),(u:Unit {Code:{Code}})"
                     "MERGE (u)-[:OFFERED_BY]->(d)")
        for v in sou.values():
            session.run(statement, {"Code": v['Code'], "Name": v['Dept']})

    with driver.session() as session:
        'Create and link Designations'
        statement = "MERGE (ud:Unit_Designation {Designation:{Des}})"
        for v in sou.values():
            if v['Designation_Str'] != '':
                for u_des in v['Designation_Str'].split(' or '):
                    session.run(statement, {"Des": u_des.strip(' ')})

        statement = ("MATCH (ud:Unit_Designation {Designation:{Des}}),(u:Unit {Code:{Code}})"
                     "MERGE (u)-[:DESIGNATED]->(ud)")
        for v in sou.values():
            if v['Designation_Str'] != '':
                for u_des in v['Designation_Str'].split(' or '):
                    session.run(statement, {"Des": u_des.strip(' '), "Code": v['Code']})

    with driver.session() as session:
        'Link Units to NCCW Units or create Unit Nodes'  # There is an outstanding issue with HSC results
        statement = ("MERGE (nccw:Unit {Code:{NCCWCode}})"
                     "ON CREATE SET nccw.Name = 'Legacy Unit'")
        for v in sou.values():
            if v['NCCW_Str'] != '':
                for nccw in v['NCCW_Str'].split(' or '):
                    session.run(statement, {"NCCWCode": nccw.strip(' ')})

        statement = ("MATCH (nccw:Unit {Code:{NCCWCode}}),(u:Unit {Code:{Code}})"
                     "MERGE (u)-[:IS_NCCW]->(nccw)")
        for v in sou.values():
            if v['NCCW_Str'] != '':
                for nccw in v['NCCW_Str'].split(' or '):
                    session.run(statement, {"NCCWCode": nccw.strip(' '), "Code": v['Code']})

    with driver.session() as session:  # Not working. Need to split at \\n but it is being skipped in the csv import
        'Create When offered nodes with attendance mode linked to units'
        statement = "MERGE (wo:Offering {Session:{Sess}})"
        for v in sou.values():
            if v['When'] != '':
                for when_o in v['When'].split("|"):
                    session.run(statement, {"Sess": when_o.strip(' ')})

        statement_with = ("MATCH (wo:Offering {Session:{Sess}}),(u:Unit {Code:{Code}})"
                          "MERGE (u)-[:OFFERED_IN {Attendance_Mode: {Att}}]->(wo)")

        statement_without = ("MATCH (wo:Offering {Session:{Sess}}),(u:Unit {Code:{Code}})"
                             "MERGE (u)-[:OFFERED_IN]->(wo)")

        for v in sou.values():
            if v['When'] != '':
                i = -1
                att_list = v['Attend'].split("|")
                for when_o in v['When'].split("|"):
                    i += 1
                    try:  # handle any issues where offering and attendance mode is not formatted in csv
                        if att_list[i] == '':
                            session.run(statement_without, {"Sess": when_o.strip(' '), "Code": v['Code']})
                        else:
                            session.run(statement_with, {"Sess": when_o.strip(' '), "Att": att_list[i], "Code": v['Code']})
                    except:
                        print(v['Code'])  # print code that has the error

main()
