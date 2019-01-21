#
# Python file to print out a Unit dictionary.
# We have a method to display each of the fields.
#

import csv


def displayUnit(DStruct):
    createCSV(DStruct, "")
    
def createCSV(DStruct, par):
    #u: is the unit code requested
    #DStruct: is the pre-requisite structure
    #level: is the level in the hierarchy
    l = 0
    p_type = 'Unit'
    with open('MQ_Hdbk_gdb.csv','w', newline='') as f:
        fieldnames = ['from', 'f_type','rel','r_type','to','t_type']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        writeUnitEntries(DStruct, par, p_type, writer, l)
        #writer.writerow({'from': c, 'rel': b, 'to': c})
  
def writeUnitEntries(DStruct, par, p_type, writer, l):
    if not("Type" in DStruct):
        #print(level, "No Prerequisites")
        writer.writerow({'from': par})
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
    return (sw.get(DStruct["Type"], displayError))(DStruct, par, p_type, writer, l)

def displayError(DStruct, par, writer, l):
    print(par , "Invalid Dictionary Entry: ", DStruct)

def displayAnd(DStruct, par, p_type, writer, l):
    l = l + 1
    newpar = 'AND'+str(l)
    np_type = 'AND'
    writer.writerow({'from': par, 'f_type': p_type, 'rel': 'HAS_PREREQUISITE', 'r_type': np_type, 'to': newpar, 't_type': np_type})
    for d in DStruct["Value"]:
        writeUnitEntries(d, newpar, np_type, writer, l)

def displayOr(DStruct, par, p_type, writer, l): 
    l = l + 1
    newpar = 'OR'+str(l)
    np_type = 'OR'
    writer.writerow({'from': par, 'f_type': p_type, 'rel': 'HAS_PREREQUISITE', 'r_type': np_type, 'to': newpar, 't_type': np_type}) 
    for d in DStruct["Value"]:
        writeUnitEntries(d, newpar, np_type , writer, l)

def displayAdmission(DStruct, par, p_type, writer, l):
    d = DStruct["Value"]
    s=""
    for i in d:
        displayDegree(i, par, p_type, writer, l)
        s=","

def displayDegree(DStruct, par, p_type, writer, l):
    d = DStruct
    p = par
    pt = p_type
    if "In" in d:
        l = l + 1
        p = 'AND'+str(l)
        pt = 'AND'
        writer.writerow({'from': par, 'f_type': p_type, 'rel': 'HAS_PREREQUISITE', 'r_type': pt, 'to': p, 't_type': pt})
        writer.writerow({'from': p, 'f_type': pt, 'rel': 'HAS_PREREQUISITE', 'r_type': 'Major', 'to': d["In"], 't_type': 'Major'})
        print(" In", d["In"], end="")
    if "prior" in d:
        writer.writerow({'from': p, 'f_type': pt, 'rel': 'HAS_PREREQUISITE', 'r_type': 'Prior_To', 'to': d["prior"], 't_type': 'Year'})
        print(" Prior to", d["prior"], end="")
    writer.writerow({'from': p, 'f_type': pt, 'rel': 'HAS_PREREQUISITE', 'r_type': 'Degree', 'to': d["Value"], 't_type': 'Degree'})
    
def displayGPA(DStruct, par, p_type, writer, l):
    node = str(DStruct["Value"])
    if "OutOf" in DStruct:
        node += " Out of" + DStruct["OutOf"]
    writer.writerow({'from': par, 'f_type': p_type, 'rel': 'HAS_PREREQUISITE', 'r_type': 'GPA', 'to': node, 't_type': 'GPA'})

def displayPermission(DStruct, par, writer, l):
    writer.writerow({'from': par, 'rel': 'HAS_PREREQUISITE', 'to': 'Permission by Special Approval'})

def displayCourse(DStruct, par, writer, l):
    if "HSC" in DStruct:
        return displayHSC(DStruct, l)
    v = "Course: "
    if "coreq" in DStruct:
        v = v + "Corequisite of "
    v = v + DStruct["Value"]
    if "Min" in DStruct:
        v = v + "(" + DStruct["Min"] + ")"
    writer.writerow({'from': par, 'rel': 'HAS_PREREQUISITE', 'to': str.upper(DStruct["Value"])})

def displayHSC(DStruct, level):
    v = "HSC " + DStruct["Value"]
    print(level, v)
    level = level + "  "
    if "bands" in DStruct:
        print(level, "Bands:", end="")
        s=""
        for b in DStruct["bands"]:
            print(s, b, end="")
            s=","
        print()
    if "Extension1" in DStruct:
        e1s = "Extension 1"
        s=": "
        for i in DStruct["Extension1"]:
            e1s = e1s + s + "E" + str(i)
            s = ", "
        print(level, e1s)
    if "Extension2" in DStruct:
        print(level, "Extension 2")

def displayRange(DStruct, level):
    print(level, "Course Range:")
    displayCourse(DStruct["Start"], level + "   ")
    displayCourse(DStruct["End"], level + "To:")

def displayCreditPoints(DStruct, level):
    cp=str(DStruct["Points"]) + " Credit Points"
    if "Min" in DStruct:
        cp = cp + "(" + DStruct["Min"] + ")"
    if "Level" in DStruct:
        cp = cp + " at " + str(DStruct["Level"]) + " level"
        if "Above" in DStruct:
            cp = cp + " or Above"
    print(level, cp)
    if "Area" in DStruct:
        print(level, "  Areas: ")
        displayAreaList(DStruct["Area"], level + "    ")
    if "Including" in DStruct:
        print(level, "  Including:")
        displayEntry(DStruct["Including"], level + "    ")

def displayAreaList(DStruct, level):
    al = DStruct["Value"]
    print(level, end="")
    s = ""
    for i in al:
        print(s, i, end="")
        s=","
    print()
