# XRPL.js Playgound

In XRPL.js

Adjust main repo

If you are adjusting the binary codec, address codec or the keypairs you will need to adjust the xrpl repo package.json. You do this because the sub packages in production are pinned to the release version of the sub repo.

`cd ~/projects/xrpl-labs/xrpl.js/packages/xrpl && npm install ../ripple-binary-codec`

Build/Sync the Xrpl repo

`yarn run sync` syncs the current xrpl.js library

> Dependencies must be built before main (xrpl)

Add Xrpl Dependency

`yarn add ~/projects/xrpl-labs/xrpl.js/packages/xrpl`

Run single test

`yarn run test test/networkID.test.ts`
