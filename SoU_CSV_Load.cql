CREATE CONSTRAINT ON (u:Unit) ASSERT u.Code IS UNIQUE;
CREATE CONSTRAINT ON (us:Unit_Scope) ASSERT us.Scope IS UNIQUE;
CREATE CONSTRAINT ON (ud:Unit_Designation) ASSERT ud.Designation IS UNIQUE;
CREATE CONSTRAINT ON (ut:Unit_Type) ASSERT ut.Type IS UNIQUE;

// DROP CONSTRAINT ON (us:Unit_Scope) ASSERT us.Unit_Scope IS UNIQUE;
 
// Delete nodes
match (n)
detach delete n
;

// Load data
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///SoU_2018.csv' AS row

//Create Units
MERGE (u:Unit {Code: row.Code, Name: row.Name, Credit_Points: row.`Credit Points`})

//Set Prerequisites for Unit node
FOREACH (x IN CASE WHEN trim(row.Prerequisites) <> "" THEN [1] ELSE [] END | SET u.Prerequisites = row.Prerequisites)

//Set Corequisites for Unit node
FOREACH (x IN CASE WHEN trim(row.Corequisites) <> "" THEN [1] ELSE [] END | SET u.Corequisites = row.Corequisites)

//Set NCCW for Unit node
FOREACH (x IN CASE WHEN trim(row.NCCW) <> "" THEN [1] ELSE [] END | SET u.NCCW = row.NCCW)

//Create link Unit Scope Units together
MERGE (us:Unit_Scope {Scope:row.`Data Scope`})
MERGE (u)-[rs:IS_SCOPE]->(us)

//Create link Unit Type Units together
FOREACH (x IN CASE WHEN trim(row.`Unit Type`) <> "" THEN [1] ELSE [] END | MERGE (ut:Unit_Type {Type:row.`Unit Type`})
	MERGE (u)-[rt:IS_TYPE]->(ut))
//MERGE (ut:Unit_Type {Type:row.`Unit Type`})

;


//links Unit Designations to units
// Load data
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///SoU_2018.csv' AS row
WITH row, split(row.`Unit Designation`,",") AS list_ud 
UNWIND
	CASE
		WHEN list_ud = []
			THEN [null]
		ELSE list_ud
	END AS result
MATCH(u:Unit {Code: row.Code})
MERGE(ud:Unit_Designation {Designation:trim(result)})
MERGE(u)-[:IS_DESIGNATED]->(ud)
;

//links Unit NCCW to units
// Load data
//NEED TO ADD CONDITION ON CREATE FOR MERGE IF NO EXISTING UNIT IS LOADED 
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///SoU_2018.csv' AS row
WITH row, split(row.NCCW,",") AS list_nccw 
UNWIND
	CASE
		WHEN list_nccw = []
			THEN [null]
		ELSE list_nccw
	END AS result
MATCH(u:Unit {Code: row.Code})
MERGE(nccw:Unit {Code:trim(result)})
MERGE(u)-[:IS_NCCW]->(nccw)
;

//Create offering nodes and link to units
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///SoU_2018.csv' AS row
WITH row, split(row.`When Offered`,'\n') AS list
UNWIND
	CASE
		WHEN list = []
			THEN [null]
		ELSE list
	END AS result
MATCH (u:Unit {Code: row.Code})
MERGE(wo:Offering {Code:trim(result)})
MERGE(u)-[:OFFERED_IN]->(wo)
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


////////// working code archive
//links Unit Designations to units
MERGE (ud1:Unit_Designation {Designation: 'Applied Linguistics'})
FOREACH (n IN CASE WHEN row.`Unit Designation` CONTAINS 'Applied Linguistics' THEN [1] ELSE [] END | MERGE (u)-[:IS_DESIGNATED]->(ud1))

MERGE (ud2:Unit_Designation {Designation: 'Arts'})
FOREACH (n IN CASE WHEN row.`Unit Designation` CONTAINS 'Arts' THEN [1] ELSE [] END | MERGE (u)-[:IS_DESIGNATED]->(ud2))

MERGE (ud3:Unit_Designation {Designation: 'Commerce'})
FOREACH (n IN CASE WHEN row.`Unit Designation` CONTAINS 'Commerce' THEN [1] ELSE [] END | MERGE (u)-[:IS_DESIGNATED]->(ud3))

MERGE (ud4:Unit_Designation {Designation: 'Economics'})
FOREACH (n IN CASE WHEN row.`Unit Designation` CONTAINS 'Economics' THEN [1] ELSE [] END | MERGE (u)-[:IS_DESIGNATED]->(ud4))

MERGE (ud5:Unit_Designation {Designation: 'Engineering'})
FOREACH (n IN CASE WHEN row.`Unit Designation` CONTAINS 'Engineering' THEN [1] ELSE [] END | MERGE (u)-[:IS_DESIGNATED]->(ud5))

MERGE (ud6:Unit_Designation {Designation: 'Information Technology'})
FOREACH (n IN CASE WHEN row.`Unit Designation` CONTAINS 'Information Technology' THEN [1] ELSE [] END | MERGE (u)-[:IS_DESIGNATED]->(ud6))

MERGE (ud7:Unit_Designation {Designation: 'Medical Sciences'})
FOREACH (n IN CASE WHEN row.`Unit Designation` CONTAINS 'Medical Sciences' THEN [1] ELSE [] END | MERGE (u)-[:IS_DESIGNATED]->(ud7))

MERGE (ud8:Unit_Designation {Designation: 'Science'})
FOREACH (n IN CASE WHEN row.`Unit Designation` CONTAINS 'Science' THEN [1] ELSE [] END | MERGE (u)-[:IS_DESIGNATED]->(ud8))