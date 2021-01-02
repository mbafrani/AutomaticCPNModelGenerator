const apiEndpoint = "http://127.0.0.1:5000/api/";

const uploadEventLog = file => new Promise((resolve, reject) => {
  const formData  = new FormData();
  formData.append("file", file);

  fetch(apiEndpoint + "event-log", {
    method: "POST",
    headers: {
      "Accept": "application/json"
    },
    body: formData
  })
  .then(response => {
    if (response.status == 200) {
      response.json().then(response => resolve(response))
    } else {
      response.json().then(response => reject(response))
    }
  })
});

const getProcessModel = eventLogId => new Promise((resolve, reject) => {
  fetch(apiEndpoint + "process-model/" + eventLogId)
    .then(response => {
      if (response.status == 200) {
        return response.blob()
      } else {
        response.json().then(response => reject(response))
      }
    })
      .then(image => {
        // create a local URL for that image
        const processModelImageUrl = URL.createObjectURL(image)
        resolve(processModelImageUrl)
      })
});

const exportCpnModel = eventLogId => new Promise((resolve, reject) => {
  fetch(apiEndpoint + "cpn-export", {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      event_log_id: eventLogId
    })
  })
  .then(response => {
    if (response.status == 200) {
      return response.blob()
    } else {
      response.json().then(response => reject(response))
    }
  })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = "cpn-model.cpn";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      resolve();
    })
    // .catch(() => alert("Something went wrong!"));
});

const getChangeParameters = eventLogId => new Promise((resolve, reject) => {
  fetch(apiEndpoint + "change-parameter/" + eventLogId)
    .then(response => {
      if (response.status == 200) {
        response.json().then(response => resolve(response))
      } else {
        response.json().then(response => reject(response))
      }
    })
});

const updateChangeParameters = changeParametersBody => new Promise((resolve, reject) => {
  fetch(apiEndpoint + "change-parameter", {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify(changeParametersBody)
  })
  .then(response => {
    if (response.status == 200) {
      return response.blob()
    } else {
      response => reject(response)
    }
  })
});

export {
  uploadEventLog,
  getProcessModel,
  exportCpnModel,
  getChangeParameters,
  updateChangeParameters,
};
