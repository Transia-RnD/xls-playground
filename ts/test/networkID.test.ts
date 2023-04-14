import { assert } from "chai";

// XRPL
// ---------------------------------------------------------------------------

import { Client } from "@transia/xrpl";

// INSTALL
// ----------------------------------------------------------------------------
// yarn add @transia/xrpl

describe("test network id", function () {
  it("all", async function () {
    const WSS_RPC_URL = "wss://hooks-testnet-v3.xrpl-labs.com";
    const client = new Client(WSS_RPC_URL);
    await client.connect();
    client.networkID = await client.getNetworkID();
    assert.equal(client.networkID, 21338);
    await client.disconnect();
  });
});
