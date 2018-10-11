#
# Python file to print out a Unit dictionary.
# We have a method to display each of the fields.
#

import csv


def displayUnit(dict):
    createCSV(dict, "")
    
def createCSV(dict, par):
    #u: is the unit code requested
    #dict: is the pre-requisite structure
    #level: is the level in the hierarchy
    l = 0
    p_type = 'Unit'
    with open('MQ_Hdbk_gdb.csv','w', newline='') as f:
        fieldnames = ['from', 'f_type','rel','r_type','to','t_type']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        writeUnitEntries(dict, par, p_type, writer, l)
        #writer.writerow({'from': c, 'rel': b, 'to': c})
  
def writeUnitEntries(dict, par, p_type, writer, l):
    if not("Type" in dict):
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
    return (sw.get(dict["Type"], displayError))(dict, par, p_type, writer, l)

def displayError(dict, par, writer, l):
    print(par , "Invalid Dictionary Entry: ", dict)

def displayAnd(dict, par, p_type, writer, l):
    l = l + 1
    newpar = 'AND'+str(l)
    np_type = 'AND'
    writer.writerow({'from': par, 'f_type': p_type, 'rel': 'HAS_PREREQUISITE', 'r_type': np_type, 'to': newpar, 't_type': np_type})
    for d in dict["Value"]:
        writeUnitEntries(d, newpar, np_type, writer, l)

def displayOr(dict, par, p_type, writer, l): 
    l = l + 1
    newpar = 'OR'+str(l)
    np_type = 'OR'
    writer.writerow({'from': par, 'f_type': p_type, 'rel': 'HAS_PREREQUISITE', 'r_type': np_type, 'to': newpar, 't_type': np_type}) 
    for d in dict["Value"]:
        writeUnitEntries(d, newpar, np_type , writer, l)

def displayAdmission(dict, par, p_type, writer, l):
    d = dict["Value"]
    s=""
    for i in d:
        displayDegree(i, par, p_type, writer, l)
        s=","

def displayDegree(dict, par, p_type, writer, l):
    d = dict
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
    
def displayGPA(dict, par, p_type, writer, l):
    node = str(dict["Value"])
    if "OutOf" in dict:
        node += " Out of" + dict["OutOf"]
    writer.writerow({'from': par, 'f_type': p_type, 'rel': 'HAS_PREREQUISITE', 'r_type': 'GPA', 'to': node, 't_type': 'GPA'})

def displayPermission(dict, par, writer, l):
    writer.writerow({'from': par, 'rel': 'HAS_PREREQUISITE', 'to': 'Permission by Special Approval'})

def displayCourse(dict, par, writer, l):
    if "HSC" in dict:
        return displayHSC(dict, l)
    v = "Course: "
    if "coreq" in dict:
        v = v + "Corequisite of "
    v = v + dict["Value"]
    if "Min" in dict:
        v = v + "(" + dict["Min"] + ")"
    writer.writerow({'from': par, 'rel': 'HAS_PREREQUISITE', 'to': str.upper(dict["Value"])})

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
