from Signatures import generate_keys, savePublic, loadPublic, loadKeys
from Wallet import my_pu, my_pr, walletServer, loadKeys
from Miner import minerServer, nonceFinder
import time
import threading
import Wallet
import Miner

wallets = []
miners = []
my_ip = 'localhost'

wallets.append((my_ip, 5006))
miners.append((my_ip, 5005))

tMS = None
tNF = None
tWS = None

def startMiner():
    global tMS, tNF
    
    try:
        Wallet.my_pu = loadPublic("public.key")
    except:
        print("No public.key. Need to generate?")
        pass # THINK

    tMS = threading.Thread(target=minerServer, args=((my_ip, 5005), ))
    tNF = threading.Thread(target=nonceFinder, args=(wallets, Wallet.my_pu))
    
    tMS.start()
    tNF.start()
    return True

def startWallet():
    global tWS
    Wallet.my_pr, Wallet.my_pu = loadKeys("private.key", "public.key")
    tWS = threading.Thread(target=walletServer, args=((my_ip, 5006),))
    tWS.start()
    return True

def stopMiner():
    print("Stopping miner")
    global tMS, tNF
    Miner.StopAll()
    if tMS: tMS.join()
    if tNF: tNF.join()
    tMS = None
    tNF = None
    return True

def stopWallet():
    print("Stopping wallet")
    global tWS
    Wallet.StopAll()
    if tWS: tWS.join()
    tWS = None
    return True

def getBalance(pu_key):
    if not tWS:
        print("Start the server by calling startWallet before checking balances")
        return 0.0
    return Wallet.getBalance(pu_key)

def sendCoins(pu_recv, amt, tx_fee):
 Wallet.sendCoins(Wallet.my_pu, amt+tx_fee, Wallet.my_pr, pu_recv,
                     amt, miners)
 return True


def printBalances(other_public, my_public):
    while not Wallet.break_now:
        print("OTHER FUKCER BALANCE: ", getBalance(other_public))
        print("MY BALANCE", getBalance(Wallet.my_pu))
        time.sleep(5)

def makeNewKeys():
    return None, None

if __name__ == "__main__":
    startMiner()
    startWallet()
    
    other_public = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtgVDX501+HzGJxusVfOJ\n8V7VXUlCs1sDgIXxq2uc38fC3fO8GmYMVVeMZ34KAZ3HMBKwMKVbN1tIPVNBz22m\n54tP+3RS8xN2lDNByiSKIFsmtDMO7JpP/hl13Lj+IiVs3bI0n1uShlOIJ8QozEud\nlwkMz39xfrvX0NN6MYl/OibIkPW6cle8hwKWE6kxiUz4nLDB4i9YuRcjWsSSW/a/\n9oU4TZWk128O4BWnqru8XNyz2km4vsq5k07WCVSCqlpyF26v85sWqDTGCHXIeZre\nEKuKiZpgAVCjgHAbYkin1BGWRVXohPnEZECrZqoTjVVEl5wAdGXntjrsWIXaumG5\nhQIDAQAB\n-----END PUBLIC KEY-----\n'
    
    time.sleep(2)
    
    sendCoins(other_public, 1.0, 0.1)
    
    time.sleep(20)
    
    t = threading.Thread(target=printBalances, args=(other_public, Wallet.my_pu))
    t.start()

    time.sleep(20)
    stopWallet()
    stopMiner()

 

