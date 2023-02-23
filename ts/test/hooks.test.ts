import { assert } from 'chai'

import { Client, Wallet, getFeeEstimateXrp, SetHook } from 'xrpl';
import { encode } from 'ripple-binary-codec';

// const fs = require("fs");

describe("test hook binary", function () {
  it("all", async function () {
    const WSS_RPC_URL = "wss://hooks-testnet-v3.xrpl-labs.com"
    const fromAcct = 'rfdxDZK1cW6YBLcbx2BrtQUivjBXe5hqeB'
    const fromSeed = 'ssYZKpUET4ZR5Q88DpYHzjnFsYgFj'
    const client = new Client(WSS_RPC_URL);
    await client.connect();
    const wallet = Wallet.fromSeed(fromSeed);
    const binary = '0061736D01000000011C0460057F7F7F7F7F017E60037F7F7E017E60027F7F017F60017F017E02230303656E76057472616365000003656E7606616363657074000103656E76025F670002030201030503010002062B077F0141B088040B7F004180080B7F0041A6080B7F004180080B7F0041B088040B7F0041000B7F0041010B07080104686F6F6B00030AC4800001C0800001017F230041106B220124002001200036020C41920841134180084112410010001A410022002000420010011A41012200200010021A200141106A240042000B0B2C01004180080B254163636570742E633A2043616C6C65642E00224163636570742E633A2043616C6C65642E22'
    const hookOn = '000000000000000000000000000000000000000000000000000000003E3FF5B7'
    const hook = {
      Hook: {
        CreateCode: binary,
        HookOn: hookOn,
        Flags: 1,
        HookApiVersion: 0,
        HookNamespace: '4FF9961269BF7630D32E15276569C94470174A5DA79FA567C0F62251AA9A36B9'
      }
    }
    const tx: SetHook = {
        Account: fromAcct,
        TransactionType: "SetHook",
        Hooks: [hook],
        NetworkID: client.networkID,
    };
    const preparedTx = await client.autofill(tx);

    const copyTx = { ...preparedTx }
    copyTx.SigningPubKey = ''
    const txBlob = encode(copyTx)
    const netFeeXRP = await getFeeEstimateXrp(client, txBlob)
    preparedTx.Fee = netFeeXRP
    
    const signedTx = wallet.sign(preparedTx).tx_blob;
    const response = await client.submit(signedTx);
    assert.equal(response.result.engine_result, 'tesSUCCESS')
    await client.disconnect()
  });
});
