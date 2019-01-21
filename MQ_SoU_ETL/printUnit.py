#
# Python file to print out a Unit dictionary.
# We have a method to display each of the fields.
#
def displayUnit(DStruct):
    displayEntry(DStruct, "")

def displayEntry(DStruct, level):
    displayUnitEntries(DStruct, level)
  
def displayUnitEntries(displayEntry, level):
    if not("Type" in displayEntry):
        print(level, "No Prerequisites")
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
    return (sw.get(displayEntry["Type"], displayError))(displayEntry, level)

def displayError(DStruct, level):
    print(level, "Invalid Dictionary Entry: ", DStruct)

def displayAnd(DStruct, level):
    print(level, "AND:")    
    for d in DStruct["Value"]:
        displayUnitEntries(d, level + "  ")

def displayOr(DStruct, level): 
    print(level, "OR:")
    for d in DStruct["Value"]:
        displayUnitEntries(d, level + "  ")

def displayAdmission(DStruct, level):
    print(level, "Admission To: ", end="")
    d = DStruct["Value"]
    s=""
    for i in d:
        print(s, end="")
        displayDegree(i, "")
        s=","
    print()

def displayDegree(DStruct, level):
    print(level, "Degree: ", end="")
    d = DStruct
    print(d["Value"], end="")
    if "In" in d:
        print(" In", d["In"], end="")
    if "prior" in d:
        print(" Prior to", d["prior"], end="")

def displayGPA(DStruct, level):
    print(level, "GPA of", DStruct["Value"], end="")
    if "OutOf" in DStruct:
        print(" Out Of", DStruct["OutOf"], end="")
    print()

def displayPermission(DStruct, level):
    print(level, "Permission by Special Approval")

def displayCourse(DStruct, level):
    if "HSC" in DStruct:
        return displayHSC(DStruct, level)
    v = "Course: "
    if "coreq" in DStruct:
        v = v + "Corequisite of "
    v = v + DStruct["Value"]
    if "Min" in DStruct:
        v = v + "(" + DStruct["Min"] + ")"
    print(level, v)

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
