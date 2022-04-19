from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_link_contract
from brownie import network, accounts, exceptions, Lottery
from scripts.run_lottery import deploy_lottery
import pytest
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    lottery_contract = deploy_lottery()

    account = get_account()

    # start lottery
    tx = lottery_contract.startLottery({"from": account})
    tx.wait(1)

    # enter lottery
    tx = lottery_contract.enter({"from": account, "value": lottery_contract.getEntranceFee()})
    tx.wait(1)

    tx2 = lottery_contract.enter({"from": account, "value": lottery_contract.getEntranceFee()})
    tx2.wait(1)


    # fund link contract
    tx4 = fund_link_contract(lottery_contract.address)
    tx4.wait(1)

    # stop lottery
    tx5 = lottery_contract.stopLottery({"from": account})
    tx5.wait(1)

    time.sleep(90)

    assert lottery_contract.winner() == account.address
    assert lottery_contract.balance() == 0