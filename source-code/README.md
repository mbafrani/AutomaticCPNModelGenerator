# Process Discovery Using Python - CPN Model WS2020
Implement the discovery and simulation of CPN models in pm4py.


## Participants:
* Deekshith Shetty
* Mehmood Ahmed
* Shubham Balyan
* Sonam Chugh
* Younes Müller


## Getting started
```bash
$ cd source-code/src
$ flask run
```


## Linting/Style guide
PEP8


## Application Structure

```
.
├── src                      # Application source code
│   ├── models               # Python model classes
│   ├── services             # Python classes allowing you to interact with models
│   ├── data                 # Place to store event-logs and intermediate files
│   ├── routes               # Routes definitions
│   ├── util                 # Useful Python functions for the project
│   ├── config.py            # Project configuration settings
│   └── app.py               # App/Server configuration
│── test                     # Unit tests source code
└── server.log               # Logs generated by the server
```