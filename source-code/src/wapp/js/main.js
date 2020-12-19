import * as apiService from "./api-service.js";
import Wizard from "./wizard.js";

const handleUploadEventLog = file =>
  apiService.uploadEventLog(file)
    .then(response => console.log("Uploaded")) // TODO: Show in the UI
    .catch(error => alert(error.statusText)); // TODO: Show in the UI

const handleProcessModel = eventLogId => 
  apiService.getProcessModel(eventLogId)
    .then(imageURL => {
      // TODO: Show in the wizard UI
      const imageElement = document.getElementById("dummy-img");
      imageElement.setAttribute("src", imageURL);
    })
    .catch(error => alert(error.statusText)); // TODO: Show in the UI

const handleExportCpnModel = eventLogId => 
  apiService.exportCpnModel(eventLogId)
    .then(response => console.log("Downloaded")) // TODO: Show in the UI
    .catch(error => alert(error.statusText)); // TODO: Show in the UI

const handleGetChangeParameters = eventLogId => 
  apiService.getChangeParameters(eventLogId)
    .then(response => console.log(response)) // TODO: Show in the UI
    .catch(error => alert(error.statusText)); // TODO: Show in the UI

const handleUpdateChangeParameters = updateParametersBody =>
  apiService.updateChangeParameters(updateParametersBody)
    .then(response => console.log("Updated")) // TODO: Show in the UI
    .catch(error => alert(error.statusText)); // TODO: Show in the UI


const wizard = new Wizard();

// first page
wizard.addPage(
  "First Page",
  () => {  // on load
    wizard.disableRightButton();
    wizard.enableRightButton();
  }, 
  "", () => {}, // left button
  "Next", () => wizard.viewNextPage() // Right button
);

// second page
wizard.addPage(
  "Second Page",
  () => {},  // on load
  "Prev", () => wizard.viewPreviousPage(), // left button
  "Next", () => wizard.viewNextPage() // Right button
);

// third page
wizard.addPage(
  "Third Page",
  () => {},  // on load
  "Prev", () => wizard.viewPreviousPage(), // left button
  "Next", () => wizard.viewNextPage() // Right button
);

// fourth page
wizard.addPage(
  "Fourth Page",
  () => {},  // on load
  "Prev", () => wizard.viewPreviousPage(), // left button
  "Next", () => wizard.viewNextPage() // Right button
);

// fifth page
wizard.addPage(
  "Fifth Page",
  () => {},  // on load
  "Prev", () => wizard.viewPreviousPage(), // left button
  "Finish", () => {} // Right button
);

wizard.showWizard();
