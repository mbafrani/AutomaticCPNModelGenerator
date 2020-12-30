import * as apiService from "./api-service.js";
import Wizard from "./wizard.js";

const handleGetChangeParameters = eventLogId => 
  apiService.getChangeParameters(eventLogId)
    .then(response => console.log(response)) // TODO: Show in the UI
    .catch(error => alert(error.message)); // TODO: Show in the UI

const handleUpdateChangeParameters = updateParametersBody =>
  apiService.updateChangeParameters(updateParametersBody)
    .then(response => console.log("Updated")) // TODO: Show in the UI
    .catch(error => alert(error.message)); // TODO: Show in the UI


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
        // TODO: Show in the wizard UI properly
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
  //"Back", () => {}, // left button event listener,  do nothing
  "Back", () => location.reload(),  // left button event listener
  "Change parameters", () => wizard.viewNextPage() // right button event listener
);

// third page
wizard.addPage(
  "Third Page",
  () => { // on load event listener
    // enable the left button
    wizard.enableLeftButton();
  },
  "Back", () => wizard.viewPreviousPage(), // left button event listener
  "Next", () => wizard.viewNextPage() // right button event listener
);

// fourth page
wizard.addPage(
  "Fourth Page",
  () => {},  // on load event listener
  "Back", () => wizard.viewPreviousPage(), // left button event listener
  "Finish", () => location.reload() // right button event listener, reload the page
);

wizard.showWizard();
