
import sys
from printUnit import *
from printCSV import *

"""
Schedule of Units parser
This file parses the schedule of units csv file and produces an internal data structure that we can query against.

"""

sou = {}    # main dictionary that holds all the records. Each record is a dictionary of fields. Each field is either a value or a dictionary of values etc...
ListOfAreas = []            # List of Areas that a course may have as including values
ListOfDegrees = []        # list of degrees offered that can be part of a pre-requisite

def canonUnit(unit):
#    print("CanonUnit(" + unit + ")")
        if not(isValidUnit(unit.upper())):
#        print("Unit not valid in canonUnit")
            return ""
        if unit[3] == " ":
            unit = unit[0:2] + unit[4:6]
        return unit

def isValidUnit(unit):
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
                return (s,2)                # end of input
            if c == b'\r':
                return (s,1)                # end of line
            if c == b'"':
                inQuotes = not(inQuotes)
            else:
                if c == b',' and inQuotes == False:
                    return (s,0)                # end of a field
        #          print(c)
                if (c == b',') and inQuotes:
                    s = s + " or "
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
        while r != 2:
            ud,r = readUnit(f)
            if r != 2:
                unit = canonUnit(ud["Code"])
                if len(unit) != 0:
                    if unit in sou:
                        if ud["Prereq_Str"] != "":
                            # we can have multiple lines for the same unit for multiple changes (sigh!)
                            print("Duplicate Unit: " + unit)
                    else:
#                        print("Adding Unit " + unit)
                        sou[unit] = ud

"""
Tokenise a string. We break on brackets or white space
"""
def tokenise(str):
    sl = []
    s=""
    state=0             # looking for a token (scanning white space)
    o = 0
    while o < len(str):
        i = str[o]
        o = o + 1
        if state == 1:    # inside a multichar token
            if i.isalnum() or i == '.':
                s = s + i
                continue
            if i == '(' and str[o:o+5] == "Hons)":
                s = s + "(Hons)"
                o = o + 5
                continue
            sl.append(s)
            s = ""
            if i in "()[]-":
                state = 0
            else:
                state = 0
        if state == 0:    # scanning white space
            if i.isspace():
                continue
            if i in "()[]-":
                sl.append(i)
                continue
            if i.isalnum():
                s = i;
                state = 1
                continue
            print("Found Unknown token char in string -->" + i + "<--")
            continue
    if len(s) != 0:
        sl.append(s)
    return sl

def getRawToken(prs, t):
    if t >= len(prs):
        return ""
    return prs[t]

def getToken(prs, t):
    return getRawToken(prs, t).lower()

"""
Take a token string and return a flag if valid, the number of tokens used and a dictionary
Here we eat the 'AND' list of rules
"""
def rule(prs, startToken):
    dl=[]
    if startToken >= len(prs):
#        print("end of prs in rule")
        return False,startToken,{}
    v,t,d = r1(prs, startToken)
    if not v:
#        print("Fail first in rule")
        return False,startToken,{}
    dl.append(d)
#
# We could turn the strange including phrases into 'and' phrases (they are practically equivalent)
# by adding a test for including here. The problem is that we also have to search for including elsewhere.
#    while getToken(prs, t) == "and" || getToken(prs, t) == "including":
    while getToken(prs, t) == "and":
#        print("Rule AND: ", prs[t+1:])
        v1,t1,d1 = r1(prs, t+1)
#        print("Rule: ", v1, t1, d1, "-->", prs[t1:], "<--")
        if not v1:
            print("Found AND but no valid second rule")
            return True,t,d
        dl.append(d1)
        t = t1
    if len(dl) > 1:
        d={"Type": "And", "Value": dl}
    return True,t,d

"""
Take a token string and return a flag if valid, the number of tokens used and a dictionary
Here we eat the 'OR' list of rules
"""
def r1(prs, startToken):
    dl=[]
    if startToken >= len(prs):
        return False,startToken,{}
    v,t,d = r2(prs, startToken)
#    print("r1 first -> ", d)
    if not v:
#        print("Failed first in r1")
        return False,startToken,{}
    dl.append(d)
    while getToken(prs, t) == "or":
        v1,t1,d1 = r2(prs, t+1)
        if not v1:
#            print("Found OR but no valid second rule")
            return False,startToken,{}
        dl.append(d1)
        t = t1
#    print("r1: ", dl)
    if len(dl) > 1:
        d={"Type": "Or", "Value": dl}
    return True,t,d

"""
Take a token string and return a flag if valid, the number of tokens used and a dictionary
Here we are looking at the actual meat of the rules themselves
"""
def r2(prs, startToken):
#    print("r2(", prs[startToken:], ")")
    if startToken >= len(prs):
        return False,startToken,{}
    if getToken(prs, startToken) == '(':
        v,t,d = creditPoints(prs, startToken)     # check for the '(' creditpoints ')' ... form first.
        if v:
            return v,t,d
#        print("R2: Try brackets: -->", prs[startToken+1:], "<--")
        v,t,d = rule(prs, startToken+1)
        if v and getToken(prs, t) == ')':
            return v,t+1,d
    if getToken(prs, startToken) == '[':
        v,t,d = rule(prs, startToken+1)
        if v and getToken(prs, t) == ']':
            return v,t+1,d
    if getToken(prs, startToken) == "admission" and getToken(prs, startToken+1) == "to":
        v,t,d = degreeList(prs, startToken+2)
        if v:
            d = {"Type": "Admission", "Value": d}
            return True,t,d
    if getToken(prs, startToken) == "gpa" and getToken(prs, startToken+1) == "of":
        try:
            gpa = float(getToken(prs, startToken+2))
        except ValueError:
            gpa = 0
        if gpa != 0:
            t = startToken + 3
            d = {"Type": "GPA", "Value":gpa}
            if getToken(prs, t) == '(' and getToken(prs, t+1) == 'out' and getToken(prs, t+2) == 'of' and getToken(prs, t+4) == ')':
                try:
                    gpa = float(getToken(prs, t + 3))
                except:
                    gpa = 0
                if gpa != 0:
                    t = t + 5
                    d["OutOf"] = gpa
#            print("GPA Rule:", d)
            return True,t,d
    if getToken(prs, startToken) == "permission" and getToken(prs, startToken+1) == "by" and getToken(prs, startToken+2) == "special" and getToken(prs, startToken+3) == "approval":
        return True,startToken+4,{"Type": "Permission"}
    v,t,d = courseList(prs, startToken)
    if v:
        if len(d) == 1:
            return True,t,d[0]                # don't bother returning a list of just one element
        return True,t,{"Type": "Or", "Value": d}
#    print("Failed courseList in r2")
    v,t,d = creditPoints(prs, startToken)
    if v:
        return v,t,d
    return False,startToken,{}

def readAreasOfUnits(fileName):
    with open(fileName) as f:
        for line in f:
            ListOfAreas.append(line.strip().lower())

def isArea(areaName):
    return areaName in ListOfAreas

def readScheduleOfDegrees(fileName):
    with open(fileName) as f:
        for line in f:
            ListOfDegrees.append(line.strip().lower())

def isDegree(degreeName):
#    print("IsDegree(" + degreeName + ")")
    return degreeName.lower() in ListOfDegrees

def getDegree(prs, startToken):
    token = getRawToken(prs, startToken)
    if not(isDegree(token) or token.lower() == "bed" or token.lower() == "bteach" or token.lower() == "babed"):
        return False,startToken,{}
    dd = {"Type":"Degree"}
    t = startToken + 1
    if getToken(prs, t) == "in":
        if getToken(prs, t+1) == "Biodiversity".lower() and getToken(prs, t+2) == "Conservation".lower():
            t = t + 3
            dd["In"] = "Biodiversity Conservation"
        elif getToken(prs, t+1) == "Advanced".lower() and getToken(prs, t+2) == "Mathematics".lower():
            t = t + 3
            dd["In"] = "Advanced Mathematics"
    if getToken(prs, t) == "prior" and getToken(prs, t + 1) == "to" and getToken(prs, t + 2).isdigit():
        dd["prior"] = int(getToken(prs, t + 2))
        t = t + 3
    while getToken(prs, t) == '(' or getToken(prs, t) == '-':
        if getToken(prs, t + 2) == ')':
            token = token+'('+getRawToken(prs, t+1)+')'
            t = t + 3
        elif getToken(prs, t + 2) == '-' and getToken(prs, t + 4) == ')':
            token = token+'('+getRawToken(prs, t+1)+'-'+getToken(prs, t+3)+')'
            t = t + 5
        elif getToken(prs, t) == '-':
            token = token+'-'+getRawToken(prs, t+1)
            t = t + 2
        else:
            break
    dd["Value"] = token
#    print("GetDegree() --> ", dd)
    return True,t,dd

def degreeList(prs, startToken):
    dl = []
    v,t,d = getDegree(prs, startToken)
    if not(v):
        return False,startToken,[]
    dl = [d]
    while getToken(prs, t) == "or":
        v1,t1,d1 = getDegree(prs, t+1)
        if not(v1):
            return True,t,dl
        dl.append(d1)
        t = t1
    return True,t,dl

def getCourse(prs, startToken):
    c = False
    t = startToken
    if getToken(prs, startToken) == "corequisite" and getToken(prs, t + 1) == "of":
        c = True
        t = t + 2
    unit = canonUnit(getToken(prs, t))
    if unit == "":
        return False,startToken,{}
    t = t + 1
    d = { "Type": "Course", "Value": unit }
    if c:
        d["coreq"] = True
    if getToken(prs, startToken+1) == '(' and getToken(prs, startToken+2) in ["p", "cr", "d", "hd"] and getToken(prs, startToken+3) == ')':
        d["Min"] = getToken(prs, startToken+2)
        t = t + 3
    return True,t,d

def getHSC(prs, startToken):
    t = startToken + 1
    if getToken(prs, t) == "chemistry":
        bl=[]
        t=t+1
        if getToken(prs, t) == "band" and getToken(prs, t + 1).isdigit():
            bl = [int(getToken(prs, t + 1))]
            t = t + 2
        return True,t,{"Type": "Course", "HSC": True, "Value": "Chemistry", "Bands": bl}
    if getToken(prs, t) == "physics":
        bl=[]
        t=t+1
        if getToken(prs, t) == "band" and getToken(prs, t + 1).isdigit():
            bl = [int(getToken(prs, t + 1))]
            t = t + 2
            while getToken(prs, t) == "or" and getToken(prs, t + 1).isdigit():
                bl.append(int(getToken(prs, t + 1)))
                t = t + 2
        return True,t,{"Type": "Course", "HSC": True, "Value": "Physics", "Bands": bl}
    ct = t
    if getToken(prs, t) == "mathematics":
        md = {"Type": "Course", "HSC": True, "Value": "Mathematics"}
        bl=[]
        t = t + 1
        if getToken(prs, t) == "band":
            if getToken(prs, t + 1).isdigit() and getToken(prs, t + 2) == '-' and getToken(prs, t + 3).isdigit():
                bl = list(range(int(getToken(prs, t + 1)), int(getToken(prs, t + 3))+1))
                md["bands"] = bl
                t = t + 4
            elif getToken(prs, t + 1).isdigit():
                bl = [int(getToken(prs, t + 1))]
                t = t + 2
                while getToken(prs, t) == "or" and getToken(prs, t + 1).isdigit():
                    bl.append(int(getToken(prs, t + 1)))
                    t = t + 2
                md["bands"] = bl
            else:
                return False,startToken,{}
            ct = t
            if getToken(prs, ct) != "or":
                # return if no trailing OR - End of maths section
                return True,ct,md
            t = ct + 1
        if getToken(prs, t) == "extension" and getToken(prs, t+1) == "1":
            bl = []
            t = t + 2
            if getToken(prs, t) == "band" and getToken(prs, t + 1)[:1] == "e" and getToken(prs, t + 1)[1:].isdigit() and getToken(prs, t + 2) == '-' and getToken(prs, t + 3)[:1] == "e" and getToken(prs, t + 3)[1:].isdigit():
                bl = list(range(int(getToken(prs, t + 1)[1:]), int(getToken(prs, t + 3)[1:])+1))
                t = t + 4
            elif getToken(prs, t) == "band" and getToken(prs, t + 1)[:1] == "e" and getToken(prs, t + 1)[1:].isdigit():
                bl = [int(getToken(prs, t + 1)[1:])]
                t = t + 2
                while getToken(prs, t) == "or" and getToken(prs, t + 1)[:1] == "e" and getToken(prs, t + 1)[1:].isdigit:
                    bl.append(int(getToken(prs, t + 1)[1:]))
                    t = t + 2
            md["Extension1"] = bl
            ct = t
        if getToken(prs, ct) != "or":
            return True,ct,md
        t = ct + 1
        if getToken(prs, t) == "extension" and getToken(prs, t+1) == "2":
            md["Extension2"] = True
            t = t + 2
        return True,t,md
    return False,startToken,{}

def getCourseRange(prs, startToken):
    if getToken(prs, startToken) == "hsc":
        # HSC Courses. We'll add these are special courses!
        return getHSC(prs, startToken)
    v,t,d = getCourse(prs, startToken)
    if not(v):
#        print("Failed getCourse in getCourseRange")
        return False,startToken,{}
    if getToken(prs, t) == '-':
        v1,t1,d1 = getCourse(prs, t+1)
        if not(v1):
            return True,t,d
        t = t1
        d = { "Type": "Range", "Start": d, "End": d1 }
    return True,t,d
    
def courseList(prs, startToken):
    v,t,d = getCourseRange(prs, startToken)
    if not(v):
#        print("Failed getCourseRange first in courseList")
        return False,startToken,[]
    cl = [ d ]
    while getToken(prs, t) == "or":
        v1,t1,d1 = getCourseRange(prs, t+1)
        if not(v1):
            break                         # not a list of courses, the OR we found must relate to something else.
        cl.append(d1)
        t = t1
    return True,t,cl

"""
Parse the Xcp string
"""
def numPoints(str):
    if len(str) < 3 or str[-2:] != "cp":
        return 0
    try:
        points = int(str[:-2])
    except ValueError:
        return 0
    return points

"""
Parse credit points requirements
Here we have multiple strange formats. It would be nice to standardise
"""
def creditPoints(prs, startToken):
    t = startToken
    b = False
    if getToken(prs, t) == '(':
        b = True
        t = t + 1             # step over the initial bracket
    if getToken(prs, t + 1) == "cp" and getToken(prs, t).isdigit():
        try:
            cp = int(getToken(prs, t))
            t = t + 1
        except ValueError:
            cp = 0
    else:
        cp = numPoints(getToken(prs, t))
    if cp <= 0:
        return False,startToken,{}
    cd = { "Type": "CreditPoints", "Points": cp }
    t = t + 1
    if getToken(prs, t) == '(' and getToken(prs, t+1) in ["p", "cr", "d", "hd"] and getToken(prs, t+2) == ')':
        cd["Min"] = getToken(prs, t+1)
        t = t + 3
    token = getToken(prs, t)
#    print("CP1: " + token)
    if token == "in" or token == "from":
        v1,t1,d1 = areaList(prs, t+1)
        if v1:
            cd["Area"] = d1
            t = t1
        if getToken(prs, t) == "units":
            t = t + 1
    if getToken(prs, t) == "at" and getToken(prs, t + 2) == "level":
        try:
            level = int(getToken(prs, t + 1))
        except ValueError:
            level = 0
        if level != 0:
            cd["Level"] = level
            t = t + 3
    if getToken(prs, t) == "or" and getToken(prs, t + 1) == "above":
        cd["Above"] = True
        t = t + 2
    if b:
        if getToken(prs , t) == ')':
            t = t + 1
        else:
            return False,startToken,{}
    if getToken(prs, t) == "including" or getToken(prs, t) == "from":
#        print("including/from rule")
        v1,t1,d1 = rule(prs, t + 1)
        if v1:
            cd["Including"] = d1
        t = t1
#    print("CP2: ", cd, "-->", prs[t:], "<--")
    return True,t,cd

"""
Area list, areas that a course can be in, such as COMP, or ENGG etc.
"""
def areaList(prs, startToken):
    token = getToken(prs, startToken)
    if not(isArea(token)):
        return False,startToken,{}
    al = [token]
    t = startToken + 1
    while getToken(prs, t) == "or" and isArea(getToken(prs, t + 1)):
        al.append(getToken(prs, t + 1))
        t = t + 2
    return True,t,{"Type":"AreaList", "Value":al}
    

"""
Pre-requisites parser.
We take a string and return a dictionary object that describes the 
"""
def parsePreReq(prereq):
    prs = tokenise(prereq)
#    print("PRS: ", prs)
    if len(prs) == 0:
        return True,{}        # none
    v,t,d =    rule(prs, 0)
    if v and t == len(prs):
        return True,d
    return False,d

def main():
    readScheduleOfDegrees("degrees.txt")
    readAreasOfUnits("areas.txt")
    readScheduleOfUnits("units.csv")
    for i in sou:
#        print(i)
        v,d = parsePreReq(sou[i]["Prereq_Str"])
        if not(v):
            print(i, v, d)
    while True:
        str = input("Enter Unit Code: ").upper()
        if len(str) == 0:
            quit()
#        print("Input was: " + str)
        if str in sou:
#            print(sou[str])
#            print("PRS: ", tokenise(sou[str]["Prereq_Str"]))
            v,d = parsePreReq(sou[str]["Prereq_Str"])
#            print(v, d)
            print(str)
            displayEntry(d, "")
            createCSV(str, d, "")


main()
