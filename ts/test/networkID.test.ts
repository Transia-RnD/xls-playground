import { assert } from "chai";

// XRPL
// ---------------------------------------------------------------------------

import { Client } from "xrpl";

// INSTALL
// ----------------------------------------------------------------------------
// yarn add "https://github.com/Transia-RnD/xrpl.js.git#hooks" --save

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
