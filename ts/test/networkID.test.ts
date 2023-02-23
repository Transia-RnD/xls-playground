import { assert } from 'chai'

import { Client } from 'xrpl';

const fs = require("fs");

describe("test network id", function () {
  it("all", async function () {
    const WSS_RPC_URL = "wss://hooks-testnet-v3.xrpl-labs.com"
    const client = new Client(WSS_RPC_URL);
    await client.connect();
    await client.setNetworkID();
    assert.equal(client.networkID, 21338)
    await client.disconnect()
  });
});
