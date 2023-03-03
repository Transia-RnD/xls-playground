# XLS Playgound


## Expermental Development

There are 2 libraries. Python and Typescript. Neither of the libraries have index/src functions. They only contain tests. This library serves 2 purposes.

1. A testing ground for new amendments
2. A prep area for adding expermental code to the production sdks. Unit & Integration Tests


In each library you will find a series of files that match the XRPLF amendment number. In each file is an install stanza.

// INSTALL
// ----------------------------------------------------------------------------
// yarn add "https://github.com/Transia-RnD/xrpl.js.git#hooks" --save

> If the branch of the install link is `beta` that means that the sdk has been added to the production sdk.

## Contributing

If you want to contribute or you clone this repo you will need to update the local links to the sdks.

The current links are pointed at `~/projects/xrpl-labs/[xrpl-sdk]`.

Rules;

- ONLY WRITE TESTS
- Have fun with it

### Quickstart

#### PY

```
cd py && source .venv/bin/activate && \
pip3 install ~/projects/xrpl-labs/xrpl-py && \
poetry run python3 test.py tests/test_xls_network_id.py
```

#### TS

```
cd ts && yarn add ~/projects/xrpl-labs/xrpl.js/packages/ripple-binary-codec && \
yarn add ~/projects/xrpl-labs/xrpl.js/packages/ripple-binary-codec && \
yarn run test test/networkID.test.ts
```

#### XRPLD

`cd xrpld && ./standalone.sh`
