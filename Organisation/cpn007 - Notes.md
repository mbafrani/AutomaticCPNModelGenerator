# CPN007
Let the users change the information of the petri net

## Process
1. Discover Petri Net
2. Enrich Petri Net
3. Save Enriched Petri Net on Server
4. Present Enriched Petri Net to User
5. Percieve Updates from User
6. Change Petri Net Accordingly
7. Save Petri Net

## Todo
* Present IDs for everything that can be changed
 * Give Decision points a name
   * Maybe rename from skip_x to decision_x
 * Give Each Activity a name
* Accept changes, based on ID
 * If ID is unknown: Return an error
 * Accept one change at a time
* Save Discovered Petri Net on Server
* Change old api
  * On Upload of XES:
    * Directly discover Petri Net
    * Directly enrich Petri Net  
    * Save Petri Net
    * 
