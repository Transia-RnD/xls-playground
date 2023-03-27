// XRPL
// ---------------------------------------------------------------------------

import { Client, Wallet } from "xrpl";

const {
  Account,
  ICXRP,
  IC,
  fund,
  trust,
  pay,
  balance,
} = require("../dist/npm/src");

describe("test tools", function () {
  it("all", async function () {
    const WSS_RPC_URL = "ws://127.0.0.1:6006";
    const client = new Client(WSS_RPC_URL);
    const wallet = Wallet.fromSeed("snoPBrXtMeMyMHUVTgbuqAfg1SUTb");

    await client.connect();

    // INIT ACCOUNTS
    const alice = new Account("alice");
    expect(alice.name).toEqual("alice");
    const bob = new Account("bob");
    expect(bob.name).toEqual("bob");

    const gw = new Account("gw");
    expect(gw.name).toEqual("gw");

    // INIT XRP
    const _ICXRP = new ICXRP(100);
    expect(_ICXRP.currency).toEqual("XRP");
    expect(_ICXRP.value).toEqual(100);
    expect(_ICXRP.amount).toEqual("100000000");

    // INIT IC
    const USD = IC.gw("USD", gw);
    USD.set(100);
    expect(USD.currency).toEqual("USD");
    expect(USD.issuer).toEqual(gw.account);
    expect(USD.value).toEqual(100);

    await fund(client, wallet, new ICXRP(2000), gw, alice, bob);
    await trust(client, USD.set(2000), alice);
    await pay(client, USD.set(20), gw, alice);

    console.log(await balance(client, alice));
    console.log(await balance(client, alice, USD));
    await client.disconnect();
  });
});
