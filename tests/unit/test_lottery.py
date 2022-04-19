from brownie import accounts, network, config, Lottery, exceptions
import pytest;
from web3 import Web3
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_link_contract, get_contract;
from scripts.run_lottery import deploy_lottery
import time

def test_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #Arrange
    lottery_contract = deploy_lottery()
    
    #Act
    entrance_fee = lottery_contract.getEntranceFee()

    #Assert
    # in our MockV3Aggregator.sol, we have mock Eth price as 2000
    # 50/2000 will be the price in eth (as entrance fee we had given was 50)
    assert entrance_fee ==  Web3.toWei(0.025, "ether")
 
def test_cant_enter_unless_start():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    lottery_contract = deploy_lottery()
    account = get_account()
    entry_fee = lottery_contract.getEntranceFee() + 100000000000
    with pytest.raises(exceptions.VirtualMachineError):
        lottery_contract.enter({"from": account, "value": entry_fee})

def test_can_start_and_enter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    lottery_contract = deploy_lottery()
    account = get_account()
    entry_fee = lottery_contract.getEntranceFee()

    # start the lottery
    tx = lottery_contract.startLottery({"from": account})
    tx.wait(1)

    tx = lottery_contract.enter({"from": account, "value": entry_fee})
    tx.wait(1)

    # lottery should have atleast one participant
    assert lottery_contract.participants(0) == account

def test_cannot_end_lottery():
    # can end lottery only once lottery is started
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    lottery_contract = deploy_lottery()

    account = get_account()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = lottery_contract.stopLottery({"from": account})

def test_can_end_lottery():
    # can end lottery that has started

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    lottery_contract = deploy_lottery()

    account = get_account()
    tx = lottery_contract.startLottery({"from": account})
    tx.wait(1)

    tx = lottery_contract.enter({"from": account, "value": lottery_contract.getEntranceFee()})
    tx.wait(1)

    fund_tx = fund_link_contract(lottery_contract.address)
    fund_tx.wait(1)

    tx = lottery_contract.stopLottery({"from": account})
    assert lottery_contract.lotteryState() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
        
    #ARRANGE
    lottery_contract = deploy_lottery()                
    account = get_account()

    # start lottery    
    lottery_contract.startLottery()

    # enter lottery
    lottery_contract.enter({"from": account, "value": lottery_contract.getEntranceFee()})
    lottery_contract.enter({"from": get_account(index=1), "value": lottery_contract.getEntranceFee()})
    lottery_contract.enter({"from": get_account(index=3), "value": lottery_contract.getEntranceFee()})
    # fund transaction
    fund_tx = fund_link_contract(lottery_contract.address)
    fund_tx.wait(1)

    # ACT    
    # stop lottery 
    tx = lottery_contract.stopLottery({"from": account})
    tx.wait(1)
    request_Id = tx.events["RandomeEmitter"]["requestId"]

    RANDOM_NUM = 556

    get_contract("vrf_coordinator").callBackWithRandomness(request_Id, RANDOM_NUM, lottery_contract.address, {"from": account})

    starting_balance_of_account = get_account(index=1).balance()
    balance_of_lottery = lottery_contract.balance()

    #ASSERT
    assert lottery_contract.winner() == get_account(index=1).address
    assert lottery_contract.balance() == 0

    assert get_account(index=1).balance() ==  starting_balance_of_account + balance_of_lottery



