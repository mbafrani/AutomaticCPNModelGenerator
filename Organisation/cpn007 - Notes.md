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




## Message

Hey everybody,

in order to enable the user to change the performance and probability information, we have to actually store the petri nets on the server
This should include all of the additional information.
I have experimented with saving petri nets into a file and it is relatively simple.
I have altered the enrich_petri_net class a bit, so that the performance information and probability information is now calculated seperately form the gviz visualization.
We call petrinet.enrich_petri_net() to add the information and petrinet.viz_petri_net() to get the gviz instance.


Thus, I propose that we change the process a bit:
1. Upon uploading of the XES file to the server, we immedeately discover the process model, enrich it and save it into a file.
2. If a user calls for the visualization of the petri net, we only visualize and do not discover or enrich.
3. When a user posts a change to the data, we just change our saved petri net.