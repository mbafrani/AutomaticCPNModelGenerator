import * as apiService from "./api-service.js";
import Wizard from "./wizard.js";

const wizard = new Wizard();

// import an event log page
wizard.addPage(
  "Import an event log",
  () => {  // on load event listener
    // disable the right button until a file is uploaded
    wizard.disableRightButton();
    // logic once file is clicked in the form
    $("#import-log-file").change(function() {
      // show the uploaded filename in the ui
      const filename = $("#import-log-file")[0].files[0].name;
      $("#import-log-filename").text(filename);
      // enable the right button
      wizard.enableRightButton();
    });
  }, 
  "", () => {}, // left button event listener,  do nothing
  "Next", () => { // right button event listener
    // disable the right button
    wizard.disableRightButton();
    // show loading gif
    $("#import-log-loading").show();
    // get the file from the input
    const file = $("#import-log-file")[0].files[0]
    // call the api to upload the event log
    apiService.uploadEventLog(file)
      .then(response => {
        console.log("Uploaded");
        console.log("Event Log id: " + response.event_log_id);
        // store the event log id in shared data
        wizard.setSharedDataForKey("event-log-id", response.event_log_id);
        // enable the right button
        wizard.enableRightButton();
        // hide the loading gif
        $("#import-log-loading").hide();
        // view the next page
        wizard.viewNextPage()
      })
      .catch(error => {
        // hide the loading gif
        $("#import-log-loading").hide();
        // TODO: Show in the UI instead of alert
        alert(error.message)
        // enable the right button
        wizard.enableRightButton();
      });
  }
);

// view process model page
wizard.addPage(
  "Enriched Process Model",
  () => { // on load event listener
    wizard.enableLeftButton();
    // show loading gif
    $("#process-model-loading").show();
    // get the event log id from wizard shared dictionary
    const eventLogId = wizard.getSharedDataForKey("event-log-id");
    // call the api to get the process model
    apiService.getProcessModel(eventLogId)
      .then(imageURL => {
        // hide the loading gif
        $("#process-model-loading").hide();
        $("#process-model").attr("href", imageURL);
        $("#process-model-img").attr("src", imageURL);
        $('.easyzoom').easyZoom();
      })
      .catch(error => {
        alert(error.message); // TODO: Show in the UI
        // disable the right button
        wizard.disableRightButton();
      });
      $("#export-file").click(function() {
        apiService.exportCpnModel(eventLogId)
        .then(response => console.log("Downloaded")) 
        .catch(error => alert(error.message)); 
        // enable the right button
        wizard.enableRightButton();
      });
  },
  "Upload New Event Log", () => location.reload(),  // left button event listener
  "Change Parameters", () => wizard.viewNextPage() // right button event listener
);

// third page
wizard.addPage(
  "Change Arrival Rate and Service Times of Activities",
  () => { // on load event listener
    // enable the left button
    wizard.enableLeftButton();
    const eventLogId = wizard.getSharedDataForKey("event-log-id");
    apiService.getChangeParameters(eventLogId)
    .then(response => {
      $('#arrival_rate').val(response.arrivalrate);
      var transitions= response.transitions;
      $('#service_times').empty();
      var content='<thead> <tr><th>Transition</th> <th>Mean (in mins) </th> <th> Std Dev (in mins)</th></tr></thead><tbody>'
       for( var i=0; i< transitions.length; i++){
        content += '<tr> <td id="t_'+[i]+'">' + transitions[i]['transition'] +'</td>'  
        content += '<td contenteditable="true">' + transitions[i]['mean'] +'</td>'
        content += '<td contenteditable="true">' + transitions[i]['std'] +'</td>'
      } 
      content += '</tbody>'
      $('#service_times').append(content);
      }
    
    ) 
    .catch(error => alert(error.message));
  },
  "Back", () => wizard.viewPreviousPage(), // left button event listener
  "Update", () => {
    var rows = [];
            $('tbody tr').each(function(i, n){
                var $row = $(n);
                rows.push({
                    mean:   parseFloat($row.find('td:eq(1)').text()),
                    std:    parseFloat($row.find('td:eq(2)').text()),
                    transition: $row.find('td:eq(0)').text(),
                });
            });

            var changeParamObj = new Object();
            changeParamObj.arrivalrate= parseFloat($('#arrival_rate').val());
            changeParamObj.event_log_id = wizard.getSharedDataForKey("event-log-id");
            changeParamObj.transitions = rows;
            apiService.updateChangeParameters(changeParamObj)
            .then(response => console.log("Updated"))
            .catch(error => alert(error.message));
            wizard.viewPreviousPage();
  } // right button event listener
);

wizard.showWizard();
