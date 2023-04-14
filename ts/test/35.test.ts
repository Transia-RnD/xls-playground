import { assert } from "chai";

// XRPL
// ---------------------------------------------------------------------------

import {
  Client,
  Wallet,
  URITokenMint,
  convertStringToHex,
} from "@transia/xrpl";
import { encode } from "@transia/ripple-binary-codec";

// INSTALL
// ----------------------------------------------------------------------------
// yarn add @transia/xrpl

describe("test 35", function () {
  it("mint", async function () {
    const WSS_RPC_URL = "ws://127.0.0.1:6006";
    const client = new Client(WSS_RPC_URL);
    const wallet = Wallet.fromSeed("snoPBrXtMeMyMHUVTgbuqAfg1SUTb");
    await client.connect();
    const tx: URITokenMint = {
      TransactionType: "URITokenMint",
      Account: wallet.classicAddress,
      URI: convertStringToHex("ipfs://CID"),
    };

    await testTransaction(client, tx, wallet);
  });
});
