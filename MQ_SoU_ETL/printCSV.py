#
# Python file to print out a Unit dictionary.
# We have a method to display each of the fields.
#

import csv


def displayUnit(dict):
    createCSV(dict, "")
    
def createCSV(u, dict, level):
    with open('MQ_Hdbk_gdb.csv','w', newline='') as f:
        fieldnames = ['from','rel','to']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        # writer.writerow({'from': 'unit1', 'rel': 'HAS_PREREQUISITE', 'to': 'unit2'})  #example#
        writeUnitEntries(u, dict, level)
  
def writeUnitEntries(u, dict, level):
    if not("Type" in dict):
        #print(level, "No Prerequisites")
        open('MQ_Hdbk_gdb.csv','w') as f:
            csv.writer()
        return
    sw = {
        "And": displayAnd,
        "Or":  displayOr,
        "Admission": displayAdmission,
        "GPA": displayGPA,
        "Permission": displayPermission,
        "Degree": displayDegree,
        "Course": displayCourse,
        "Range":  displayRange,
        "CreditPoints": displayCreditPoints,
        "AreaList": displayAreaList }
    return (sw.get(dict["Type"], displayError))(dict, level)

def displayError(dict, level):
    print(level, "Invalid Dictionary Entry: ", dict)

def displayAnd(dict, level):
    print(level, "AND:")    
    for d in dict["Value"]:
        displayUnitEntries(d, level + "  ")

def displayOr(dict, level): 
    print(level, "OR:")
    for d in dict["Value"]:
        displayUnitEntries(d, level + "  ")

def displayAdmission(dict, level):
    print(level, "Admission To: ", end="")
    d = dict["Value"]
    s=""
    for i in d:
        print(s, end="")
        displayDegree(i, "")
        s=","
    print()

def displayDegree(dict, level):
    print(level, "Degree: ", end="")
    d = dict
    print(d["Value"], end="")
    if "In" in d:
        print(" In", d["In"], end="")
    if "prior" in d:
        print(" Prior to", d["prior"], end="")

def displayGPA(dict, level):
    print(level, "GPA of", dict["Value"], end="")
    if "OutOf" in dict:
        print(" Out Of", dict["OutOf"], end="")
    print()

def displayPermission(dict, level):
    print(level, "Permission by Special Approval")

def displayCourse(dict, level):
    if "HSC" in dict:
        return displayHSC(dict, level)
    v = "Course: "
    if "coreq" in dict:
        v = v + "Corequisite of "
    v = v + dict["Value"]
    if "Min" in dict:
        v = v + "(" + dict["Min"] + ")"
    print(level, v)

def displayHSC(dict, level):
    v = "HSC " + dict["Value"]
    print(level, v)
    level = level + "  "
    if "bands" in dict:
        print(level, "Bands:", end="")
        s=""
        for b in dict["bands"]:
            print(s, b, end="")
            s=","
        print()
    if "Extension1" in dict:
        e1s = "Extension 1"
        s=": "
        for i in dict["Extension1"]:
            e1s = e1s + s + "E" + str(i)
            s = ", "
        print(level, e1s)
    if "Extension2" in dict:
        print(level, "Extension 2")

def displayRange(dict, level):
    print(level, "Course Range:")
    displayCourse(dict["Start"], level + "   ")
    displayCourse(dict["End"], level + "To:")

def displayCreditPoints(dict, level):
    cp=str(dict["Points"]) + " Credit Points"
    if "Min" in dict:
        cp = cp + "(" + dict["Min"] + ")"
    if "Level" in dict:
        cp = cp + " at " + str(dict["Level"]) + " level"
        if "Above" in dict:
            cp = cp + " or Above"
    print(level, cp)
    if "Area" in dict:
        print(level, "  Areas: ")
        displayAreaList(dict["Area"], level + "    ")
    if "Including" in dict:
        print(level, "  Including:")
        displayEntry(dict["Including"], level + "    ")

def displayAreaList(dict, level):
    al = dict["Value"]
    print(level, end="")
    s = ""
    for i in al:
        print(s, i, end="")
        s=","
    print()
