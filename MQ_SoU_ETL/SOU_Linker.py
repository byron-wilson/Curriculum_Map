#
# Python file to link units together with their co and pre-requisite data.
# We have already created the master data in a neo4j graph db
#

import csv
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "test123"

driver = GraphDatabase.driver(uri, auth=(user, password))

def createChild(parent, child_type, child_name):
    if isinstance(parent, int):
        with driver.session() as session:
            statement = ("MATCH (p) WHERE id(p) = {par_id}"
                         "CREATE (c:"+str.title(child_type)+" {Name: {Name}})"
                         "CREATE (p)-[r:HAS_PREREQUISITE]->(c)"
                         "RETURN id(c)")
            result = session.run(statement, {"par_id": parent, "Name": child_name})
        node_id = result._records[0][0]
        return node_id
    else:
        with driver.session() as session:
            statement = ("MATCH (p:Unit {Code: {Code}})"
                         "CREATE (c:"+str.title(child_type)+" {Name: {Name}})"
                         "CREATE (p)-[r:HAS_PREREQUISITE]->(c)"
                         "RETURN id(c)")
            result = session.run(statement, {"Code": parent, "Name": child_name})
        node_id = result._records[0][0]
        return node_id


def writeEntry(DStruct):
    createPrereq(DStruct, "")
    
def createPrereq(DStruct, par):
    # u: is the unit code requested
    # DStruct: is the pre-requisite structure
    # level: is the level in the hierarchy
    l = 0
    p_type = 'Unit'
    writeUnitEntries(DStruct, par, p_type, l)
  
def writeUnitEntries(DStruct, par, p_type, l):
    if not("Type" in DStruct):
        print(par, "No Prerequisites") # if no pre-req, print code into console and skip
        return
    sw = {
        "And": writeAnd,
        "Or":  writeOr,
        "Admission": writeAdmission,
        "GPA": writeGPA,
        "Permission": writePermission,
        "Degree": writeDegree,
        "Unit": writeUnit,
        "Range":  writeRange,
        "CreditPoints": writeCreditPoints,
        "AreaList": writeAreaList }
    return (sw.get(DStruct["Type"], writeError))(DStruct, par, p_type, l)


def writeError(DStruct, par, p_type, l):
    print(par, "Invalid Dictionary Entry: ", DStruct)


def writeAnd(DStruct, par, p_type, l): #  DONE
    c_type = 'AND'
    cid = createChild(par, c_type, c_type)
    l += 1
    for d in DStruct["Value"]:
        writeUnitEntries(d, cid, c_type, l)


def writeOr(DStruct, par, p_type, l):
    c_type = 'OR'
    cid = createChild(par, c_type, c_type)
    l += 1
    for d in DStruct["Value"]:
        writeUnitEntries(d, cid, c_type, l)


def writeAdmission(DStruct, par, p_type, l):
    d = DStruct["Value"]
    s=""
    for i in d:
        writeDegree(i, par, p_type, l)
        s=","


def writeDegree(DStruct, par, p_type, l):
    d = DStruct
    p = par
    pt = p_type
    if "In" in d:
        l = l + 1
        p = 'AND'+str(l)
        pt = 'AND'
#        writer.writerow({'from': par, 'f_type': p_type, 'rel': 'HAS_PREREQUISITE', 'r_type': pt, 'to': p, 't_type': pt})
#        writer.writerow({'from': p, 'f_type': pt, 'rel': 'HAS_PREREQUISITE', 'r_type': 'Major', 'to': d["In"], 't_type': 'Major'})
        print(" In", d["In"], end="")
    if "prior" in d:
#        writer.writerow({'from': p, 'f_type': pt, 'rel': 'HAS_PREREQUISITE', 'r_type': 'Prior_To', 'to': d["prior"], 't_type': 'Year'})
        print(" Prior to", d["prior"], end="")
#    writer.writerow({'from': p, 'f_type': pt, 'rel': 'HAS_PREREQUISITE', 'r_type': 'Degree', 'to': d["Value"], 't_type': 'Degree'})


def writeGPA(DStruct, par, p_type, l):
    node = str(DStruct["Value"])
    if "OutOf" in DStruct:
        node += " Out of" + DStruct["OutOf"]
#    writer.writerow({'from': par, 'f_type': p_type, 'rel': 'HAS_PREREQUISITE', 'r_type': 'GPA', 'to': node, 't_type': 'GPA'})


def writePermission(DStruct, par, p_type, l):
    c_type = "Permission"
    c_name = "Permission by Special Approval"
    cid = createChild(par, c_type, c_name)

#    writer.writerow({'from': par, 'rel': 'HAS_PREREQUISITE', 'to': 'Permission by Special Approval'})


def writeUnit(DStruct, par, p_type, l):
    if "HSC" in DStruct:                # To be updated
        return writeHSC(DStruct, l)
    elif "coreq" in DStruct:            # To be updated, may need to exit into coreq linker
        return 0 # to be removed, placeholder
#        v = v + "Corequisite of "
    elif "Min" in DStruct:
        with driver.session() as session:
            statement = ("MATCH (p) WHERE ID(p) = {par_id}" 
                         "MATCH (c:Unit {Code: {Code}})" 
                         "CREATE (p)-[r:HAS_PREREQUISITE {Min_Grade: {Grade}]->(c)")
            session.run(statement, {"par_id": par, "Code": str.upper(DStruct["Value"]), "Grade": DStruct["Min"]})
    else:
        with driver.session() as session:
            statement = ("MATCH (p) WHERE ID(p) = {par_id}" 
                         "MATCH (c:Unit {Code: {Code}})" 
                         "CREATE (p)-[r:HAS_PREREQUISITE]->(c)")
            session.run(statement, {"par_id": par, "Code": str.upper(DStruct["Value"])})


def writeHSC(DStruct, level):
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


def writeRange(DStruct, level):
    print(level, "Unit Range:")
    writeUnit(DStruct["Start"], level + "   ")
    writeUnit(DStruct["End"], level + "To:")


def writeCreditPoints(DStruct, level):
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
        writeAreaList(DStruct["Area"], level + "    ")
    if "Including" in DStruct:
        print(level, "  Including:")
        writeEntry(DStruct["Including"], level + "    ")


def writeAreaList(DStruct, level):
    al = DStruct["Value"]
    print(level, end="")
    s = ""
    for i in al:
        print(s, i, end="")
        s=","
    print()
