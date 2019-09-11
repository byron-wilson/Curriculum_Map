print("MATCH (p) WHERE id(p) = {par_id}"
      "CREATE (c:"+str.title("OR")+" {Name: {Name}})"
      "CREATE (p)-[r:HAS_PREREQUISITE]->(c)"
      "RETURN id(c)")