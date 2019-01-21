'''
Created on 20 Jan. 2019

@author: Byron Wilson

This load script is to create a Schedule of Units Database in Neo4j from scratch

'''
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "test123"


sou = {}    # main dictionary that holds all the records. Each record is a dictionary of fields. Each field is either a value or a dictionary of values etc...
ListOfAreas = []            # List of Areas that a course may have as including values
ListOfDegrees = []        # list of degrees offered that can be part of a pre-requisite


def canonUnit(unit):
    'Reformats the Unit Code to remove spaces like for HRM 107 '
#    print("CanonUnit(" + unit + ")")
    if not(isValidUnit(unit.upper())):
#       print("Unit not valid in canonUnit")
        return ""
    if unit[3] == " ":
        unit = unit[0:2] + unit[4:6]
    return unit

def isValidUnit(unit):
    'Checks the length of the unit code, the alpha and numeric parts for validity'
    if len(unit) == 7:
            if not(unit[0:2].isupper()):
                return False
            if not(unit[3].isupper()) and unit[3] != " ":
                return False
            return unit[4:6].isdigit()
    if len(unit) == 6:     # old style three letter/three number units
            if not(unit[0:2].isupper()):
                return False
            return unit[3:5].isdigit()
    return False

def readValue(f):
        s=""
        inQuotes=False
        while True:
            c = f.read(1)
            if len(c) == 0:
                return (s,2)                # 2 signifies the end of the file, end of input
            if c == b'\r':
                return (s,1)                # Question: does the 1 do anything? , end of line
            if c == b'"':
                inQuotes = not(inQuotes)    # If quotes found, check variable and flick to True if starts at False
            else:
                if c == b',' and inQuotes == False:
                    return (s,0)                # end of a field
        #          print(c)
                if (c == b',') and inQuotes:
                    s = s + " or "              # add in 'or' to field name
                elif c != b'\n' and c[0] < 128:
                    s = s + c.decode("utf-8")

def addUnitField(f, ud, field):
        v,r = readValue(f)
        if r != 2:
            ud[field] = v
        return r
        
def readUnit(f):
        ud = {}     # dictionary for this unit
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
        v,r = readValue(f)
        v,r = readValue(f)
        v,r = readValue(f)
        v,r = readValue(f)
        return ud,r

def readScheduleOfUnits(fileName):
    with open(fileName, "rb") as f:
        r = 0
        while r != 2:                       #2 is being used to stop reading file
            ud,r = readUnit(f)              #ud is a line from the csv mapped to field names and r is return code
            if r != 2:
                unit = canonUnit(ud["Code"])    #Check if the value mapped to the field "Code" is a valid code
                if len(unit) != 0:              #If the check returns a code of any length. Write it to the sou variable
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
    
    #Delete all nodes in the test database
    with driver.session() as session:
        session.run("match (n)"
                    "detach delete n")
        
    #=== skip for now ========================================================================
    # with driver.session() as session:
    #     UnqCon = "CREATE CONSTRAINT ON {node} ASSERT {Field} IS UNIQUE"
    #     session.run(UnqCon, {"node": "(u:Unit)","field":"u.Code"})
    #     session.run(UnqCon, {"node": "(us:Unit_Scope)","field":"us.Scope"})
    #     session.run(UnqCon, {"node": "(ud:Unit_Designation)","field":"ud.Designation"})
    #     session.run(UnqCon, {"node": "(ut:Unit_Type)","field":"ut.Type"})
    #     session.run(UnqCon, {"node": "(wo:Offering)","field":"wo.Session"})
    #     session.run(UnqCon, {"node": "(d:Department)","field":"d.Name"})
    #     session.run(UnqCon, {"node": "(f:Faculty)","field":"f.Name"})                    
    #===========================================================================
    
    with driver.session() as session:
        'Create Unit Nodes with code, name and credit point attributes'
        statement = "MERGE (u:Unit {Code: {Code}, Name: {Name}, Credit_Points: {Credit_Points}, Pass_Fail: {PF}})"
        for v in sou.values():
            session.run(statement,{"Code": v['Code'], "Name": v['Name'], "Credit_Points": v['Credit'], "PF": v['PF']})
            
    #===========================================================================
    # with driver.session() as session:
    #     'Set unit nodes property Pass_Fail'
    #     statement = ("MATCH (u:Unit {Code:{Code}})"
    #                  "SET u.`Pass/Fail` = {PF}")
    #     for v in sou.values():
    #         session.run(statement,{"Code": v['Code'], "PF": v['PF']})        
    #===========================================================================
    with driver.session() as session:
        'Create Scope Nodes'
        statement = "MERGE (us:Unit_Scope {Scope:{Scope}})"           
        for v in sou.values():
            session.run(statement,{"Scope": v['Scope']})
            
    with driver.session() as session:
        'link it to existing unit nodes'
        statement = ("MATCH (us:Unit_Scope {Scope:{Scope}}),(u:Unit {Code:{Code}})"
                     "MERGE (u)-[:IS_SCOPE]->(us)")
        for v in sou.values():
            session.run(statement,{"Scope": v['Scope'], "Code": v['Code']})
            
main()