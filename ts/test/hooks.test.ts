import { assert } from "chai";

// XRPL
// ---------------------------------------------------------------------------

import {
  Client,
  Wallet,
  getFeeEstimateXrp,
  SetHook,
  calculateHookOn,
  TTS,
  hexNamespace,
} from "xrpl";
import { encode } from "ripple-binary-codec";

// INSTALL
// ----------------------------------------------------------------------------
// yarn add "https://github.com/Transia-RnD/xrpl.js.git#hooks" --save

const fs = require("fs");

describe("test hook binary", function () {
  it("all", async function () {
    const WSS_RPC_URL = "wss://hooks-testnet-v3.xrpl-labs.com";
    const fromAcct = "rfdxDZK1cW6YBLcbx2BrtQUivjBXe5hqeB";
    const fromSeed = "ssYZKpUET4ZR5Q88DpYHzjnFsYgFj";
    const client = new Client(WSS_RPC_URL);
    await client.connect();
    client.networkID = await client.getNetworkID();
    const wallet = Wallet.fromSeed(fromSeed);

    // CreateCode
    const binary = fs
      .readFileSync("test/fixtures/starter.c.wasm")
      .toString("hex")
      .toUpperCase();

    // HookOn
    const invokeOn: Array<keyof TTS> = ["ttACCOUNT_SET"];
    const hookOn = calculateHookOn(invokeOn);

    // NameSpace
    const namespace = await hexNamespace("starter");

    // Build Hook
    const hook = {
      Hook: {
        CreateCode: binary,
        HookOn: hookOn,
        Flags: 1,
        HookApiVersion: 0,
        HookNamespace: namespace,
      },
    };

    // Prepare Hook
    const tx: SetHook = {
      Account: fromAcct,
      TransactionType: "SetHook",
      Hooks: [hook],
      NetworkID: client.networkID,
    };
    const preparedTx = await client.autofill(tx);

    // Estimate Fee
    const copyTx = { ...preparedTx };
    copyTx.SigningPubKey = "";
    const txBlob = encode(copyTx);
    const netFeeXRP = await getFeeEstimateXrp(client, txBlob);
    preparedTx.Fee = netFeeXRP;

    // Sign Tx
    const signedTx = wallet.sign(preparedTx).tx_blob;

    // Submit Tx
    const response = await client.submit(signedTx);
    assert.equal(response.result.engine_result, "tesSUCCESS");
    await client.disconnect();
  });
});
