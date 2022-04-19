from brownie import Contract, accounts, network, config, MockV3Aggregator, VRFCoordinatorMock, LinkToken, interface
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ['development', 'ganache-local']
FORKED_LOCAL_ENVIRONMENTS = ['mainnet-fork', 'mainnet-fork-dev']
DECIMALS = 8
STARTING_PRICE = 200000000000

contract_to_mock = {"eth_usd_address": MockV3Aggregator, "vrf_coordinator": VRFCoordinatorMock, "link_token": LinkToken }

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])

def deploy_mock_aggregator():
    account = get_account()
    link_token = None
    if len(MockV3Aggregator) <= 0:
        print("Deploying Mock Aggregator...")
        MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": account})
        print("Mock aggregator deployed")

    if len(LinkToken) <= 0:
        print("Deploy Link Token Mock..")
        link_token = LinkToken.deploy({"from": account})
        print(" Mock Link Token deployed")

    if len(VRFCoordinatorMock) <= 0:
        print("Deploying Mock VRF Coordinator")
        VRFCoordinatorMock.deploy(link_token.address, {"from": account})
        print(" Mock VRF Integrator deployed")


def get_contract_address():
    current_network = network.show_active()
    
    if current_network not in  LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        price_feed_address = config["networks"][current_network]["eth_usd_address"]
    else:
        # if ganache development environment (local), then
        # we first deploy mock aggregator contract
        # we then assign address of mock aggregator contract to fund me contract price aggregator
        deploy_mock_aggregator()
        price_feed_address = MockV3Aggregator[-1].address
    
    return price_feed_address

def get_contract(contract_name):
    """
        This function gets the contract address from config file for testnet/mainnet networks
        and mocks a contract for development and ganache-local networks

        Args:
            contract_name: string

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed version of contract
    """
    contract_type = contract_to_mock[contract_name]
    print('current contract')
    print(contract_type)

    current_network = network.show_active()

    if current_network in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if (len(contract_type) <= 0):
            deploy_mock_aggregator()
        return contract_type[-1]
    else:
        contract_address = config["networks"][current_network][contract_name]
        return Contract.from_abi(contract_type._name, contract_address,contract_type.abi)

def fund_link_contract(contract_address, account=None, link_token = None, amount = 100000000000000000):
    usable_account = account if account else get_account() 
    usable_link_token_contract = link_token if link_token else get_contract("link_token")

    # link contract that basically transfers link gas fee from user account to specific contract address
    tx = usable_link_token_contract.transfer( contract_address, amount, {"from": usable_account})


    # using interfaces 
    # tx = interface.LinkTokenInterface(usable_link_token_contract.address)
    # tx.transfer(contract_address, amount, {"from": usable_account})

    tx.wait(1)
    print("funding link contract")
    return tx


