import unittest
import pickle
import time
import threading
from SocketUtils import newServerConnection, recvObj, sendObj
from Transaction import Tx
from TxBlock import TxBlock, findLongestBlockchain
from Signatures import generate_keys

wallets = [('localhost', 5006)]
tx_list = []
head_blocks = [None]
break_now = False
verbose = True

def StopAll():
    global break_now
    break_now = True
    
def minerServer(my_addr):
    global tx_list
    global break_now
    head_blocks=[None]
    my_ip, my_port = my_addr
    server = newServerConnection(my_ip, my_port)
    # Get Txs from wallets
    while not break_now:
        newTx = recvObj(server)
        if isinstance(newTx,Tx):
            tx_list.append(newTx)
            if verbose: print ("Recd tx")
    return False

def nonceFinder(wallet_list, miner_public):
    global break_now
    # add Txs to new block
    while not break_now:
        newBlock = TxBlock(findLongestBlockchain(head_blocks))
        for tx in tx_list:
            newBlock.addTx(tx)
        # Compute and add mining reward
        total_in,total_out = newBlock.count_totals()
        mine_reward = Tx()
        mine_reward.add_output(miner_public,25.0+total_in-total_out)
        newBlock.addTx(mine_reward)
        # Find nonce
        if verbose: print ("Finding Nonce...")
        newBlock.find_nonce(10000)
        if newBlock.good_nonce():
            if verbose: print ("Good nonce found")
            # Send new block
            savePrev = newBlock.previousBlock
            newBlock.previousBlock = None
            for ip_addr,port in wallet_list:
                if verbose: print ("Sending to " + ip_addr + ":" + str(port))
                sendObj(ip_addr,newBlock,5006)
            newBlock.previousBlock = savePrev
            # Remove used txs from tx_list
            for tx in newBlock.data:
                if tx != mine_reward:
                    tx_list.remove(tx)
    return True

def loadTxList(filename):
    fin = open(filename, "rb")
    ret = pickle.load(fin)
    fin.close()
    return ret

def saveTxList(the_list, filename):
    fp = open(filename, "wb")
    pickle.dump(the_list, fp)
    fp.close()
    return True

class TestMiner(unittest.TestCase):
    def test(self):
        my_pr, my_pu = generate_keys()
        t1 = threading.Thread(target=minerServer, args=(('localhost', 5005), ))
        t2 = threading.Thread(target=nonceFinder, args=(wallets, my_pu))
        server = newServerConnection('localhost', port=5006)
        t1.start()
        t2.start()
        pr1,pu1 = generate_keys()
        pr2,pu2 = generate_keys()
        pr3,pu3 = generate_keys()
        
        Tx1 = Tx()
        Tx2 = Tx()
        
        Tx1.add_input(pu1, 4.0)
        Tx1.add_input(pu2, 1.0)
        Tx1.add_output(pu3, 4.8)
        Tx2.add_input(pu3, 4.0)
        Tx2.add_output(pu2, 4.0)
        Tx2.add_reqd(pu1)

        Tx1.sign(pr1)
        Tx1.sign(pr2)
        Tx2.sign(pr3)
        Tx2.sign(pr1)

        new_tx_list = [Tx1, Tx2]
        saveTxList(new_tx_list, "Txs.dat")
        new_new_tx_list = loadTxList("Txs.dat")

        for tx in new_new_tx_list:
            try:
                sendObj('localhost', tx)
                print("Sent tx")
            except:
                print("Error COnnection unsuccessful")
        
        for i in range(30):
            newBlock = recvObj(server)
            if newBlock:
                break
        if newBlock.is_valid():
            print("Success! Block is valid")
        if newBlock.good_nonce():
            print("Success! Nonce is valid")
            
        # self.assertTrue(newBlock.is_valid(), "This block must be valid")
        # self.assertTrue(newBlock.good_nonce(), "This nonce must be valid")

        for tx in newBlock.data:
            try:
                if tx.inputs[0][0] == pu1 and tx.inputs[0][1] == 4.0:
                    print("Tx1 is present")
            except:
                pass
            try:
                if tx.inputs[0][0] == pu3 and tx.inputs[0][1] == 4.0:
                    print("Tx2 is present")
            except:
                pass
        time.sleep(20)
        break_now = True
        time.sleep(3)

        t1.join()
        t2.join()

        print("Done !")

if __name__ == "__main__":
   unittest.main() 
