import { assert } from "chai";

// XRPL
// ---------------------------------------------------------------------------

import {
  Client,
  Wallet,
  SetHook,
  calculateHookOn,
  TTS,
  hexNamespace,
  hexHookParameters,
  // LedgerEntryRequest,
  // LedgerEntryResponse,
} from "@transia/xrpl";
import { getFeeEstimateXrp } from "@transia/xrpl/dist/npm/sugar";
import { encode } from "@transia/ripple-binary-codec";
// import { TRANSACTION_TYPES } from "ripple-binary-codec";

const fs = require("fs");

// INSTALL
// ----------------------------------------------------------------------------
// yarn add @transia/xrpl

describe("test hooks", function () {
  it("all", async function () {
    const WSS_RPC_URL = "wss://hooks-testnet-v3.xrpl-labs.com";
    const fromAcct = "rfdxDZK1cW6YBLcbx2BrtQUivjBXe5hqeB";
    const fromSeed = "ssYZKpUET4ZR5Q88DpYHzjnFsYgFj";
    const client = new Client(WSS_RPC_URL);
    await client.connect();
    const wallet = Wallet.fromSeed(fromSeed);

    // CreateCode
    const binary = fs
      .readFileSync("test/fixtures/starter.c.wasm")
      .toString("hex")
      .toUpperCase();

    // HookOn
    const invokeOn: Array<keyof TTS> = ["Invoke"];
    const hookOn = calculateHookOn(invokeOn);

    // NameSpace
    const namespace = await hexNamespace("starter");

    // Hook Parameters
    const parameters = [
      {
        HookParameter: {
          HookParameterName: "name1",
          HookParameterValue: "value1",
        },
      },
    ];
    const hookParameters = hexHookParameters(parameters);

    // Build Hook
    const hook = {
      Hook: {
        CreateCode: binary,
        HookOn: hookOn,
        Flags: 1,
        HookApiVersion: 0,
        HookNamespace: namespace,
        HookParameters: hookParameters,
      },
    };

    // Prepare Hook
    const tx: SetHook = {
      Account: fromAcct,
      TransactionType: "SetHook",
      Hooks: [hook],
      NetworkID: 21338,
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

// describe("test hooks rpc", function () {
//   it("ledger entry hook_definition", async function () {
//     const WSS_RPC_URL = "wss://hooks-testnet-v3.xrpl-labs.com";
//     const client = new Client(WSS_RPC_URL);
//     await client.connect();

//     const hook_hash =
//       "ACD3E29170EB82FFF9F31A067566CD15F3A328F873F34A5D9644519C33D55EB7";

//     const ledgerEntryRequest: LedgerEntryRequest = {
//       command: "ledger_entry",
//       hook_definition: hook_hash,
//     };

//     const ledgerEntryResponse = await client.request(ledgerEntryRequest);
//     console.log(ledgerEntryResponse);

//     const expectedResponse: LedgerEntryResponse = {
//       id: ledgerEntryResponse.id,
//       type: "response",
//       result: {
//         index: ledgerEntryResponse.result.index,
//         ledger_current_index: ledgerEntryResponse.result.ledger_current_index,
//         node: ledgerEntryResponse.result.node,
//         validated: false,
//       },
//     };

//     assert.equal(ledgerEntryResponse.type, "response");
//     assert.deepEqual(ledgerEntryResponse, expectedResponse);
//     await client.disconnect();
//   });
// });

// function iterateListV2(arr) {
//   let combinationArray = [] as string[][];

//   for (let i = 0; i <= arr.length; i++) {
//     let combination = [] as string[];
//     for (let j = 0; j < i; j++) {
//       combination.push(arr[j] as string);
//     }
//     combinationArray.push(combination as string[]);
//   }

//   return combinationArray;
// }

// function iterateList(list) {
//   const sublists = [] as string[][];

//   for (let i = 0; i < list.length; i++) {
//     sublists.push([list[i]]);
//     for (let j = i + 1; j < list.length; j++) {
//       sublists.push(list.slice(i, j + 1));
//     }
//   }
//   return sublists;
// }

// describe("test hooks variables", function () {
//   it("hook on", async function () {
//     const WSS_RPC_URL = "wss://hooks-testnet-v3.xrpl-labs.com";
//     const client = new Client(WSS_RPC_URL);
//     await client.connect();
//     const fullListOfLists = iterateList(TRANSACTION_TYPES);
//     const fList = [] as Record<string, any>[];
//     for (let l = 0; l < fullListOfLists.length; l++) {
//       const list = fullListOfLists[l];
//       const invokeOn: Array<keyof TTS> = list;
//       const hookOn = calculateHookOn(invokeOn);
//       const obj = {
//         list: invokeOn,
//         hookOn: hookOn,
//       };
//       fList.push(obj);
//     }
//     const jsonfString = JSON.stringify(fList);
//     fs.writeFile("./hookonMap.json", jsonfString, (err) => {
//       if (err) {
//         console.error(err);
//         return;
//       }
//     });
//     const ffList = {} as Record<string, string[]>;
//     for (let t = 0; t < TRANSACTION_TYPES.length; t++) {
//       const tt = TRANSACTION_TYPES[t];
//       for (let fl = 0; fl < fList.length; fl++) {
//         const flo = fList[fl].list;
//         if (flo.includes(tt)) {
//           if (!ffList[tt]) {
//             ffList[tt] = [fList[fl].hookOn];
//           } else {
//             ffList[tt].push(fList[fl].hookOn);
//           }
//         }
//       }
//     }
//     const jsonffString = JSON.stringify(ffList);
//     fs.writeFile("./hookonByTT.json", jsonffString, (err) => {
//       if (err) {
//         console.error(err);
//         return;
//       }
//     });
//     await client.disconnect();
//   });
//   it("reverse lookup hook on", async function () {
//     const WSS_RPC_URL = "wss://hooks-testnet-v3.xrpl-labs.com";
//     const client = new Client(WSS_RPC_URL);
//     await client.connect();
//     const hookOn =
//       "000000000000000000000000000000000000000000000000000000003E3FF5BC";
//     const ttList = calculateTTSFromHookOn(hookOn);
//     assert.equal(ttList, ["Payment", "EscrowCancel"]);
//   });
// });
