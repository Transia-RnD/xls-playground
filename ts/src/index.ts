import { Client, Wallet, getFeeEstimateXrp, SetHook } from 'xrpl';
import { encode } from 'ripple-binary-codec';

// -----------------------------------------------------------------------------

const toAcct = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
const toSeed = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"

const fromAcct = 'rfdxDZK1cW6YBLcbx2BrtQUivjBXe5hqeB'
const fromSeed = 'ssYZKpUET4ZR5Q88DpYHzjnFsYgFj'

const WSS_RPC_URL = "wss://hooks-testnet-v3.xrpl-labs.com"

const run = async () => {
  try {
    const client = new Client(WSS_RPC_URL);
    await client.connect();
    console.log('CONNECTED');
    console.log(client.networkID);
    await client.disconnect();
  } catch (error) {
    console.error(error);
  }
};
run();
