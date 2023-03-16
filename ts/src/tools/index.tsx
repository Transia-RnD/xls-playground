import {
  Client,
  Wallet,
  Payment,
  TrustSet,
  AccountSet,
  AccountSetAsfFlags,
  xrpToDrops,
  decodeAccountID,
  TxRequest,
  LedgerEntryRequest,
  AccountInfoRequest,
  TxResponse,
  convertStringToHex,
} from "xrpl";
// import { symbolToHex } from "xrpl-helpers";
import { IssuedCurrencyAmount } from "xrpl/dist/npm/models/common";
import { RippleState } from "xrpl/dist/npm/models/ledger";
import { BaseRequest } from "xrpl/dist/npm/models/methods/baseMethod";

const LEDGER_ACCEPT_REQUEST = { command: "ledger_accept" } as BaseRequest;

export class Account {
  name: string;
  account: string | undefined;
  wallet: Wallet;

  constructor(name?: string, seed?: string) {
    this.wallet = Wallet.generate();
    this.account = this.wallet.classicAddress;
    if (seed) {
      this.wallet = Wallet.fromSeed(seed);
      this.account = this.wallet.classicAddress;
    }

    this.name = name as string;
    if (name === "gw") {
      this.wallet = Wallet.fromSeed("sEdSmmFciyvxYaQcdRCv4FhYEJ1aqpn");
      this.account = this.wallet.classicAddress;
    }
    if (name === "alice") {
      this.wallet = Wallet.fromSeed("sEd7mHoS84UWye8epfNvHXkeET1Btfd");
      this.account = this.wallet.classicAddress;
    }
    if (name === "bob") {
      this.wallet = Wallet.fromSeed("sEdTQgHLuZVjcYGoBRV2hvq2iDXUDWZ");
      this.account = this.wallet.classicAddress;
    }
    if (name === "carol") {
      this.wallet = Wallet.fromSeed("sEdSbbjTvsKZ8xNkJSyHVBYPNY3jkR9");
      this.account = this.wallet.classicAddress;
    }
    if (name === "dave") {
      this.wallet = Wallet.fromSeed("sEdSmJx74N6UiDm2uwVzLBmkVuR3HTy");
      this.account = this.wallet.classicAddress;
    }
    if (name === "elsa") {
      this.wallet = Wallet.fromSeed("sEdTeiqmPdUob32gyD6vPUskq1Z7TP3");
      this.account = this.wallet.classicAddress;
    }
  }
}

export class ICXRP {
  issuer: string | undefined;
  currency: string = "XRP";
  value: number;
  amount: string;

  constructor(value: number) {
    this.value = value;
    this.amount = xrpToDrops(value);
  }
}

export class IC {
  issuer: string | undefined;
  currency: string | undefined;
  value: number | undefined;
  amount: Record<string, any> | undefined;

  static gw(name: string, gw: Account): IC {
    const self = new IC();
    self.issuer = gw.account;
    // self.currency = symbolToHex(name);
    self.currency = name;
    return self;
  }

  constructor() {}

  set(value: number): IC {
    this.value = value;
    this.amount = {
      issuer: this.issuer,
      currency: this.currency,
      value: String(this.value),
    };
    return this;
  }
}

export async function xrpBalance(
  ctx: Client,
  account: Account
): Promise<number> {
  const request: AccountInfoRequest = {
    command: "account_info",
    account: account.account as string,
  };
  const response = await ctx.request(request);
  if (
    "error" in response.result &&
    response.result["error"] === "actNotFound"
  ) {
    return 0;
  }
  return parseFloat(response.result["account_data"]["Balance"]);
}

export async function icBalance(
  ctx: Client,
  account: Account,
  ic: IC
): Promise<number> {
  const request: LedgerEntryRequest = {
    command: "ledger_entry",
    ripple_state: {
      currency: ic.currency as string,
      accounts: [account.account as string, ic.issuer as string],
    },
  };
  const response = await ctx.request(request);
  if ("error" in response.result) {
    return 0;
  }
  const node = response.result.node as RippleState;
  return Math.abs(parseFloat(node.Balance.value));
}

export async function balance(
  ctx: Client,
  account: Account,
  ic?: IC
): Promise<number> {
  if (!ic) {
    return await xrpBalance(ctx, account);
  }
  return await icBalance(ctx, account, ic);
}

export async function limit(
  ctx: Client,
  account: Account,
  ic: IC
): Promise<number> {
  const request: LedgerEntryRequest = {
    command: "ledger_entry",
    ripple_state: {
      currency: ic.currency as string,
      accounts: [account.account as string, ic.issuer as string],
    },
  };
  const isHighLimit =
    decodeAccountID(account.account as string) >
    decodeAccountID(ic.issuer as string);
  console.log(isHighLimit);
  const response = await ctx.request(request);
  if ("error" in response.result) {
    return 0;
  }
  const node: any = response.result.node as RippleState;
  return parseFloat(isHighLimit ? node.HighLimit.value : node.LowLimit.value);
}

export async function fund(
  ctx: Client,
  wallet: Wallet,
  uicx: IC | ICXRP,
  ...accts: Account[]
): Promise<void> {
  for (const acct of accts) {
    try {
      const preparedTx: Payment = {
        TransactionType: "Payment",
        Account: wallet.classicAddress,
        Destination: acct.account as string,
        Amount: uicx.amount as IssuedCurrencyAmount,
      };
      const response = await ctx.submit(preparedTx, { wallet });
      if ("error" in response.result) {
        console.log(response.result["error"]);
      }
      const txResult: string = response.result["engine_result"];
      if (txResult !== "tesSUCCESS") {
        console.log(`FUND FAILED: ${txResult}`);
      }
      const txHash = response.result["tx_json"]["hash"] as string;
      waitForResult(ctx, txHash);
    } catch (error: any) {
      console.log(error);
      if (error.data) {
        console.log(error.data.decoded);
        console.log(error.data.tx);
      }
      // throw error;
    }
  }
}

export async function pay(
  ctx: Client,
  uicx: IC | ICXRP,
  signer: Account,
  ...accts: Account[]
): Promise<void> {
  for (const acct of accts) {
    try {
      const preparedTx: Payment = {
        TransactionType: "Payment",
        Account: signer.wallet.classicAddress,
        Destination: acct.account as string,
        Amount: uicx.amount as IssuedCurrencyAmount,
      };
      const response = await ctx.submit(preparedTx, { wallet: signer.wallet });
      if ("error" in response.result) {
        console.log(response.result["error"]);
      }
      const txResult: string = response.result["engine_result"];
      if (txResult !== "tesSUCCESS") {
        console.log(`PAY FAILED: ${txResult}`);
      }
      const txHash = response.result["tx_json"]["hash"] as string;
      waitForResult(ctx, txHash);
    } catch (error: any) {
      console.log(error);
      if (error.data) {
        console.log(error.data.decoded);
        console.log(error.data.tx);
      }
      // throw error;
    }
  }
}

export async function trust(
  ctx: Client,
  uicx: IC | ICXRP,
  ...accts: Account[]
): Promise<void> {
  for (const acct of accts) {
    try {
      const preparedTx: TrustSet = {
        TransactionType: "TrustSet",
        Account: acct.account as string,
        LimitAmount: uicx.amount as IssuedCurrencyAmount,
      };
      const response = await ctx.submit(preparedTx, { wallet: acct.wallet });
      if ("error" in response.result) {
        console.log(response.result["error"]);
      }
      const txResult: string = response.result["engine_result"];
      if (txResult !== "tesSUCCESS") {
        console.log(`TRUST FAILED: ${txResult}`);
      }
      const txHash = response.result["tx_json"]["hash"] as string;
      waitForResult(ctx, txHash);
    } catch (error: any) {
      console.log(error);
      if (error.data) {
        console.log(error.data.decoded);
        console.log(error.data.tx);
      }
      // throw error;
    }
  }
}

export async function accountSet(ctx: Client, account: Account): Promise<void> {
  const preparedTx: AccountSet = {
    TransactionType: "AccountSet",
    Account: account.account as string,
    TransferRate: 0,
    Domain: convertStringToHex("https://usd.transia.io"),
    SetFlag: AccountSetAsfFlags.asfDefaultRipple,
  };
  const response = await ctx.submit(preparedTx, { wallet: account.wallet });
  if ("error" in response.result) {
    console.log(response.result["error"]);
  }
  const txResult: string = response.result["engine_result"];
  if (txResult !== "tesSUCCESS") {
    console.log(`FUND FAILED: ${txResult}`);
  }
  const txHash = response.result["tx_json"]["hash"] as string;
  waitForResult(ctx, txHash);
}

export async function rpc(
  ctx: Client,
  account: Account,
  txjson: any
): Promise<void> {
  const response = await ctx.submit(txjson, { wallet: account.wallet });
  if ("error" in response.result) {
    console.log(response.result["error"]);
  }
  const txResult: string = response.result["engine_result"];
  if (txResult !== "tesSUCCESS") {
    console.log(`FUND FAILED: ${txResult}`);
  }
  const txHash = response.result["tx_json"]["hash"] as string;
  waitForResult(ctx, txHash);
}

export async function close(ctx: Client): Promise<void> {
  await ctx.request(LEDGER_ACCEPT_REQUEST);
}

export async function waitForResult(
  ctx: Client,
  txHash: string
): Promise<TxResponse> {
  let timeout = 0;
  while (timeout <= 8) {
    ctx.request(LEDGER_ACCEPT_REQUEST);
    const request: TxRequest = {
      command: "tx",
      transaction: txHash,
    };
    const response = await ctx.request(request);
    if (
      "validated" in response.result &&
      response.result["validated"] === true
    ) {
      return response;
    }
    setTimeout(() => {}, 1000);
    timeout += 1;
  }
  throw new Error("test transaction timeout");
}
