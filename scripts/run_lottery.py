from brownie import accounts, Lottery, network, config
from scripts.helpful_scripts import get_account, get_contract, fund_link_contract
import time

def deploy_lottery():
    account = get_account()
    print(f"current network is {network.show_active()}")
    eth_usd_address = get_contract("eth_usd_address").address
    vrf_coordinator_address = get_contract("vrf_coordinator").address
    link_address =  get_contract("link_token").address    
    
    key_hash = config["networks"][network.show_active()]["key_hash"]
    chainlink_fee = config["networks"][network.show_active()]["fee"]
      
    publish = config["networks"][network.show_active()].get("verify", False)
    print(f"current eth-usd address is {eth_usd_address}")
    print(f"current vrf address is {vrf_coordinator_address}")
    print(f"current link address is {link_address}")
    print(f"current key hash is {key_hash}")
    print(f"current publish state is {publish}")
    print(f"current chainlink fee is {chainlink_fee}")
    
    if len(Lottery) <= 0:
        lottery_contract = Lottery.deploy(50, eth_usd_address, vrf_coordinator_address, link_address, chainlink_fee, key_hash,  {"from": account}, publish_source=publish)
        print("Deployed lottery contract")

    else:
        lottery_contract = Lottery[-1]

    return lottery_contract

def start_lottery():
    account = get_account()
    lottery_contract = Lottery[-1]

    print('account address:')
    print(account.address)
 
    print('lottery address:')
    print(lottery_contract.address)

    print('starting lottery')
    lottery_contract.startLottery({"from": account})
    print('start lottery contract deployed')

def enter_lottery():
    account = get_account()
    lottery_contract = Lottery[-1]
    entry_fee = lottery_contract.getEntranceFee() + 10000000000
    tx = lottery_contract.enter({"from": account, "value":entry_fee })
    tx.wait(1)
    print('You entered lottery')


def end_lottery():
    account = get_account()
    lottery_contract = Lottery[-1]
    print('fund link contract initiated')
    fund_tx = fund_link_contract(lottery_contract.address)
    fund_tx.wait(1)
    print('link contract funded')

    print('stop lottery initiated')
    tx = lottery_contract.stopLottery({"from": account})
    tx.wait(1)

    # sleep for 60 seconds until we generate verified random number
    # since this comes out of the 
    time.sleep(60)
    print('stop lottery completed')

    print(f'winner of lottery is ${lottery_contract.winner}')
    print("lottery has stopped")

def main():
    deploy_lottery() 
    start_lottery()
    enter_lottery()
    end_lottery()