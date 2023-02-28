from BlockChain import CBlock
from Transaction import Tx
from Signatures import generate_keys, sign, verify
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import unittest
import pickle
import time
import random

reward = 25.0
leading_zeros = 2
next_char_limit = 100

class TxBlock(CBlock):
    nonce = "AAAA"
    def __init__(self, previousBlock):
        super(TxBlock, self).__init__([], previousBlock)
    def addTx(self, Tx_in):
        self.data.append(Tx_in)

    def removeTx(self, Tx_in):
        if Tx_in in self.data:
            self.data.remove(Tx_in)
            return True
        return False

    def count_totals(self):
        total_in = 0
        total_out = 0

        for tx in self.data:
            for addr, amt  in tx.inputs:
                total_in += amt
            for addr, amt  in tx.outputs:
                total_out += amt

        return total_in, total_out

    def check_size(self):
        savePrev = self.previousBlock
        self.previousBlock = None
        this_size = len(pickle.dumps(self))
        self.previousBlock = savePrev
        if this_size > 10000:
            return False
        return True
            
    def is_valid(self):
        if not super(TxBlock, self).is_valid():
            return False
        for tx in self.data:
            if not tx.is_valid():
                return False
        total_in, total_out = self.count_totals()
        if total_out - total_in - reward > 0.000000000001:
            return False
        if not self.check_size():
            return False

        return True

    def good_nonce(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data),'utf8'))
        digest.update(bytes(str(self.previousHash),'utf8'))
        digest.update(bytes(str(self.nonce),'utf8'))
        this_hash = digest.finalize()
       
        if this_hash[:leading_zeros] != bytes(''.join([ '\x4f' for i in range(leading_zeros)]),'utf8'):
            return False
        return int(this_hash[leading_zeros]) < next_char_limit

    def find_nonce(self, n_tries=1000000):
        for i in range(n_tries):
            self.nonce = ''.join([ 
                   chr(random.randint(0,255)) for i in range(10*leading_zeros)])
            if self.good_nonce():
                return self.nonce  
        return None

def findLongestBlockchain(head_blocks):
    longest = -1
    long_head = None
    for b in head_blocks:
        current = b
        this_len = 0
        while current != None:
            this_len = this_len + 1
            current = current.previousBlock
        if this_len > longest:
            long_head = b
            longest = this_len
    return long_head

def saveBlocks(block_list, filename):
    fp = open(filename, "wb")
    pickle.dump(block_list, fp)
    fp.close()
    return True

def loadBlocks(filename):
    fin = open(filename, "rb")
    ret = pickle.load(fin)
    fin.close()
    return ret
    
class TxBlockTest(unittest.TestCase):
    def test_block(self):
        pr1, pu1 = generate_keys()
        pr2, pu2 = generate_keys()
        pr3, pu3 = generate_keys()
        pr4, pu4 = generate_keys()

        Tx1 = Tx()
        Tx1.add_input(pu1, 1)
        Tx1.add_output(pu2, 1)
        Tx1.sign(pr1)

        self.assertTrue(Tx1.is_valid(), "Transaction should be valid")

        savefile = open("tx.dat", "wb")
        pickle.dump(Tx1, savefile)
        savefile.close()

        loadfile = open("tx.dat", "rb")
        newTx = pickle.load(loadfile)
        loadfile.close()

        self.assertTrue(newTx.is_valid(), "Transaction should be valid")

        loadfile.close()

        root = TxBlock(None)
        mine1 = Tx()
        mine1.add_output(pu1, 8.0)
        mine1.add_output(pu2, 8.0)
        mine1.add_output(pu3, 8.0)

        root.addTx(Tx1)
        root.addTx(mine1)

        Tx2 = Tx()
        Tx2.add_input(pu2,1.1)
        Tx2.add_output(pu3, 1)
        Tx2.sign(pr2)
        root.addTx(Tx2)

        B1 = TxBlock(root)
        Tx3 = Tx()
        Tx3.add_input(pu3,1.1)
        Tx3.add_output(pu1, 1)
        Tx3.sign(pr3)
        B1.addTx(Tx3)
        
        Tx4 = Tx()
        Tx4.add_input(pu1,1)
        Tx4.add_output(pu2, 1)
        Tx4.add_reqd(pu3)
        Tx4.sign(pr1)
        Tx4.sign(pr3)
        B1.addTx(Tx4)
        start = time.time()
        print(B1.find_nonce())
        elapsed = time.time() - start
        print("elapsed time: " + str(elapsed) + " s.")
        self.assertTrue(elapsed < 60, "Mining is too fast increase leading_zeros")
        self.assertTrue(B1.good_nonce(), "Nonce is Good")

        savefile = open("block.dat", "wb")
        pickle.dump(B1, savefile)
        savefile.close()

        loadfile = open("block.dat" ,"rb")
        load_B1 = pickle.load(loadfile)
        loadfile.close()

        for b  in [root, B1, load_B1, load_B1.previousBlock]:
            self.assertTrue(b.is_valid(), "Blocks should be valid blocks")

        self.assertTrue(B1.good_nonce(), "Nonce is Good after save and load")

        B2 = TxBlock(B1)
        Tx5 = Tx()
        Tx5.add_input(pu3, 1)
        Tx5.add_output(pu1, 100)
        Tx5.sign(pr3)
        B2.addTx(Tx5)

        load_B1.previousBlock.addTx(Tx4)
        for b in [B2, load_B1]:
            self.assertFalse(b.is_valid(), "This Blocks should be invalid")

        # Test mining rewards and tx fees
        B3 = TxBlock(B2)
        B3.addTx(Tx2)
        B3.addTx(Tx3)
        B3.addTx(Tx4)
        Tx6 = Tx()
        Tx6.add_output(pu4, 25)
        B3.addTx(Tx6)
        self.assertTrue(B3.is_valid(), "Block reward failed")

        B4 = TxBlock(B3)
        B4.addTx(Tx2)
        B4.addTx(Tx3)
        B4.addTx(Tx4)
        Tx7 = Tx()
        Tx7.add_output(pu4, 25.2)
        B4.addTx(Tx7)
        self.assertTrue(B4.is_valid(), "Tx fee fail")

        # Greedy miner
        B5 = TxBlock(B4)
        B5.addTx(Tx2)
        B5.addTx(Tx3)
        B5.addTx(Tx4)
        Tx8 = Tx()
        Tx8.add_output(pu4, 26.2)
        B5.addTx(Tx8)
        self.assertFalse(B5.is_valid(), "Greedy miner not detected")

        B6 = TxBlock(B4)
        this_pu = pu4
        this_pr = pr4
        for i in range(30):
            newTx = Tx()
            new_pr, new_pu = generate_keys()
            newTx.add_input(this_pu,0.3)
            newTx.add_output(new_pu,0.3)
            newTx.sign(this_pr)
            B6.addTx(newTx)
            this_pu, this_pr = new_pu, new_pr
            savePrev = B6.previousBlock
            B6.previousBlock = None
            this_size = len(pickle.dumps(B6))
            print("Size = " + str(this_size))
            B6.previousBlock = savePrev
            self.assertTrue(B6.is_valid(), "Block is not valid")
            self.assertTrue(this_size < 10000, "Big block detected")

            overspend = Tx()
            overspend.add_input(pu1,45.0)
            overspend.add_output(pu2,44.5)
            overspend.sign(pr1)
            B7 = TxBlock(B4)
            B7.addTx(overspend)
            if B7.is_valid():
                print("Error! Overspend not detected")
            else:
                print("Success! Overspend detected")

            overspend1 = Tx()
            overspend1.add_input(pu1,5.0)
            overspend1.add_output(pu2,4.5)
            overspend1.sign(pr1)
            overspend2 = Tx()
            overspend2.add_input(pu1,15.0)
            overspend2.add_output(pu3,14.5)
            overspend2.sign(pr1)
            overspend3 = Tx()
            overspend3.add_input(pu1,5.0)
            overspend3.add_output(pu4,4.5)
            overspend3.sign(pr1)
            overspend4 = Tx()
            overspend4.add_input(pu1,8.0)
            overspend4.add_output(pu2,4.5)
            overspend4.sign(pr1)
            B8 = TxBlock(B4)
            B8.addTx(overspend1)
            B8.addTx(overspend2)
            B8.addTx(overspend3)
            B8.addTx(overspend4)
            if B8.is_valid():
                print("Error! Overspend not detected")
            else:
                print("Success! Overspend detected")

if __name__ == "__main__":
        unittest.main()
