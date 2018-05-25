CREATE CONSTRAINT ON (u:Unit) ASSERT u.Code IS UNIQUE;
CREATE CONSTRAINT ON (ut:Unit_Type) ASSERT ut.Unit_Type IS UNIQUE;
CREATE CONSTRAINT ON (ud:Unit_Designation) ASSERT ud.Designation IS UNIQUE;

//Delete nodes
match (u:Unit)
detach delete u;

match (ut:Unit_Type)
detach delete ut;

match (ud:Unit_Designation)
detach delete ud;


//Create Unit Designations first and only once outside of Load Data loop
CREATE (:Unit_Designation {Designation: 'Applied Linguistics'})
CREATE (:Unit_Designation {Designation: 'Arts'})
CREATE (:Unit_Designation {Designation: 'Commerce'})
CREATE (:Unit_Designation {Designation: 'Economics'})
CREATE (:Unit_Designation {Designation: 'Engineering'})
CREATE (:Unit_Designation {Designation: 'Information Technology'})
CREATE (:Unit_Designation {Designation: 'Medical Sciences'})
CREATE (:Unit_Designation {Designation: 'Science'})
;

// Load data
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///SoU_2018.csv' AS row

//Create Unit Type
MERGE (ut:Unit_Type {Type:row.`Data Scope`})

//Create Units
CREATE (u:Unit {Code: row.Code, Name: row.Name, Credit_Points: row.`Credit Points`})

//Create link Unit Type Units together
CREATE (u)-[rt:IS_TYPE]->(ut)

//links Unit Designations to units
MATCH (ud:Unit_Designation)
WHERE ud.Designation = 'Applied Linguistics'
FOREACH (n IN CASE WHEN row.`Unit Designation` CONTAINS 'Applied Linguistics' THEN [1] ELSE [] END | MERGE (u)-[:IS_DESIGNATED]->(ud)
;


//Test matching with relationships
MATCH (u:Unit)-[:IS_TYPE]->(ut:Unit_Type)
WHERE ut.Type = 'Undergraduate'
RETURN u.credit_points;

//Return ENGG units
MATCH (u:Unit)
WHERE u.Code CONTAINS 'ENGG'
RETURN *;

match (u:Unit)-[d:IS_DESIGNATED]->(ud:Unit_Designation {Designation: 'Applied Linguistics'})
Return *;


//////////

CASE 

WHEN row.`Unit Designation` CONTAINS 'Applied Linguistics' THEN
MATCH (ud:Unit_Designation)
WHERE ud.Designation = 'Applied Linguistics'
CREATE (u)-[:IS_DESIGNATED]->(ud)

WHEN row.`Unit Designation` CONTAINS 'Arts' THEN
MATCH (ud:Unit_Designation)
WHERE ud.Designation = 'Arts'
CREATE (u)-[:IS_DESIGNATED]->(ud)

WHEN row.`Unit Designation` CONTAINS 'Commerce' THEN
MATCH (ud:Unit_Designation)
WHERE ud.Designation = 'Commerce'
CREATE (u)-[:IS_DESIGNATED]->(ud)

WHEN row.`Unit Designation` CONTAINS 'Economics' THEN
MATCH (ud:Unit_Designation)
WHERE ud.Designation = 'Economics'
CREATE (u)-[:IS_DESIGNATED]->(ud)

WHEN row.`Unit Designation` CONTAINS 'Engineering' THEN
MATCH (ud:Unit_Designation)
WHERE ud.Designation = 'Engineering'
CREATE (u)-[:IS_DESIGNATED]->(ud)

WHEN row.`Unit Designation` CONTAINS 'Information Technology' THEN
MATCH (ud:Unit_Designation)
WHERE ud.Designation = 'Information Technology'
CREATE (u)-[:IS_DESIGNATED]->(ud)

WHEN row.`Unit Designation` CONTAINS 'Medical Sciences' THEN
MATCH (ud:Unit_Designation)
WHERE ud.Designation = 'Medical Sciences'
CREATE (u)-[:IS_DESIGNATED]->(ud)

WHEN row.`Unit Designation` CONTAINS 'Science' THEN
MATCH (ud:Unit_Designation)
WHERE ud.Designation = 'Science'
CREATE (u)-[:IS_DESIGNATED]->(ud)

END