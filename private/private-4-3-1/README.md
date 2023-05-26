# Private Network

> DO NOT RUN THIS IN PRODUCTION. THIS IS ONLY FOR TESTING.

### Init python env (xrpl-py is only dependency)

`mkvirtualenv ripplednet && pip3 install -r requirements.txt`

### Start Validators

1. `./start_validators.sh`
2. `python3 report.py`

> Report shows the validators and peers status'

### Start Peers

> You need to wait till the validators are synced. On initial this takes seconds, when retesting it may take more time.

1. `./start_peers.sh`
2. `python3 report.py`

TODO: DA add sync script from "the lab" or recreate delay until validation.

### Teardown

`./stop_peers.sh && ./stop_validators.sh`

`./stop_peers.sh && ./stop_validators.sh destroy`

> destroy will remove the db for all validators and peers. Be careful
