from terra_sdk.client.lcd import LCDClient
import asyncio
from terra_sdk.core.market import MsgSwap
from terra_sdk.core.coins import Coins
from terra_sdk.core.coins import Coin
from terra_sdk.core.wasm import MsgStoreCode, MsgInstantiateContract, MsgExecuteContract
from terra_sdk.core.bank import MsgSend
from terra_sdk.key.mnemonic import MnemonicKey
from terra_sdk.client.lcd.api.tx import CreateTxOptions
import requests
from terra_sdk.core.fee import Fee
import time
terra = LCDClient(chain_id="columbus-5", url="https://lcd.terra.dev")

mk = MnemonicKey(mnemonic='YOUR MNEMONIC KEY')

# Creating the msg to execute
amount = 1000000
astroport_address = 'terra1esle9h9cjeavul53dqqws047fpwdhj6tynj5u4'
wallet = terra.wallet(mk)
bluna_luna_pair_address = 'terra1jxazgm67et0ce260kvrpfv50acuushpjsz2y0p'
luna_bluna_pair_address = "terra1j66jatn3k50hjtg2xemnjm8s7y8dws9xqa5y8w"
swap = (
    MsgExecuteContract(
        sender=mk.acc_address,
        contract=luna_bluna_pair_address,
        execute_msg={
            "swap": {
                "offer_asset": {
                    "max_spread":"0.001", # Optional
                    "info": {"native_token": {"denom": "uluna"}},
                    "amount": str(int(amount)),
                },
                "to": mk.acc_address,
            }
        },
        coins=coins,
    ),
)

# Specify how much LUNA to send to the swap function
blockheight = 0
while True:
    if int(terra.tendermint.block_info()['block']['header']['height']) > blockheight:
        blockheight = int(terra.tendermint.block_info()['block']['header']['height'])
        amount = 1000000
        coin = Coin("uluna", amount).to_data()
        coins = Coins.from_data([coin])
    #Start query data
        terra_swap_endpoint = 'https://fcd.terra.dev'
        contract_address = 'terra1j66jatn3k50hjtg2xemnjm8s7y8dws9xqa5y8w'
        query_msg = '{"simulation":{"offer_asset":{"amount":"1000000","info":{"native_token":{"denom":"uluna"}}}}}'
        response = requests.get(terra_swap_endpoint + '/wasm/contracts/' + contract_address + '/store', params={'query_msg': query_msg})
        if response.status_code == 200:
                return_amount = int(response.json().get('result').get('return_amount'))
                commission_amount = int(response.json().get('result').get('commission_amount'))
                spread_amount = int(response.json().get('result').get('spread_amount'))
                luna_amount = 1000000
                percent_diff = (return_amount - luna_amount) / luna_amount * 100
                if percent_diff > 0.35: #adjust to your preferred threshold
                    tx = wallet.create_and_sign_tx(CreateTxOptions(
                    msgs=swap,
                ))
                    result = terra.tx.broadcast(tx)
                    print(result.txhash,'trade executed at', percent_diff, '@', blockheight)
                else:
                    print('no trade, difference is too small at:', percent_diff)
