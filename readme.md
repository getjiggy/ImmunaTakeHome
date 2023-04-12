# TakeHome 

# TXN: https://etherscan.io//tx/0x6200bf5c43c214caa1177c3676293442059b4f39eb5dbae6cfd4e6ad16305668#eventlog

## Steps taken

1. Attacker requests a flashloan of 139039.729301264180297254 WETH to his exploit contract. 
2. attacker swaps 104 weth to the Univ2 TINU pool through the univ2 router (holds 22.1445 weth and 1781945970074.638149262 TINU before swap). 
    - after swap, v2 pool has reserves of 126.994561461014981232 WETH and 316871513264.115731249 TINU 
3. Attacker calls deliver() to TINU, which forces an update to _tFeeTotal and _rTotal. 
4. attacker calls skim() which forces the token balances of the v2 pool to match its reserves, and receives 1595069238022.872354042 TINU, because the rebasing token will have paid the v2 pool a fee because of the transfers, causing balances to not match reserves. 
5. attacker calls deliver() again, forcing updates, meaning when the v2pool calls balanceOf(), reflection fees will have been added to its balance.
6. attack directly calls the pools swap function to swap out 126.990751624171150782 weth, the vast majority of its weth balance. 
    - because the swap function does a .balanceOf call to the TINU token, this updates the pools balance of INU to 11191855315120216.048899805 from 316871513264.115731249 due to rebasing fees, meaning the attacker did not have to transfer any TINU to the pool to complete the swap.
5. having emptied the pool of most of its WETH, the attacker repays the balancer flashloan
6. attacker unwraps weth into eth and self destructs exploit contract, sending 22.110751624171150782 eth to his EOA. 

## What was the state of involved tokens/pools/protocols

- TINU is a reflection token that took a fee on transactions
-UniswapV2 Pool 

## Who ended up losing assets

- The liquidity providers of the UniswapV2 TINU pool lost their assets
- in its lifetime, there are only 2 mint events emitted. The first is the protocol itself and deposited the vast majority of liquidity.

## How could they have protected themselves from losing the assets

- I think that perhaps a code change preventing the uniswapv2 pair from collecting rebasing fees would have prevented this txn. This would have prevented the attacker from being able to call .swap() on the pair w/o transferring in tokens. This also would have likely prevented the initial swap from being able to break away from the k formula. I would need to actually test a code change to be confident this would prevented the attack. 

- Alternatively, they could have monitored the mempool for   transactions which would leave the uniswapv2 pool w/ large balance changes. Upon detection, they would have sent a txn to  a smart contract which would act as a wrapper for liquidity providers wanting to deposit into the pool, and triggered an emergency withdraw, sending assets to their rightful owners. This txn would essentially need to frontrun the malicious transaction in order to be included in the block ahead of the malicious transaction and force it to revert. 
