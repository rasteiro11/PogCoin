from BlockChain import CBlock
from Transaction import Tx
from Signatures import generate_keys, sign, verify
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import unittest
import pickle

class TxBlock(CBlock):
    def __init__(self, previousBlock):
        super(TxBlock, self).__init__([], previousBlock)
    def addTx(self, Tx_in):
        self.data.append(Tx_in)
    def is_valid(self):
        if not super(TxBlock, self).is_valid():
            return False
        for tx in self.data:
            if not tx.is_valid():
                return False
        return True


class TxBlockTest(unittest.TestCase):
    def test_block(self):
        pr1, pu1 = generate_keys()
        pr2, pu2 = generate_keys()
        pr3, pu3 = generate_keys()

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
        root.addTx(Tx1)

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

        savefile = open("block.dat", "wb")
        pickle.dump(B1, savefile)
        savefile.close()

        loadfile = open("block.dat" ,"rb")
        load_B1 = pickle.load(loadfile)

        for b  in [root, B1, load_B1, load_B1.previousBlock]:
            self.assertTrue(b.is_valid(), "Blocks should be valid blocks")

        B2 = TxBlock(B1)
        Tx5 = Tx()
        Tx5.add_input(pu3, 1)
        Tx5.add_output(pu1, 100)
        Tx5.sign(pr3)
        B2.addTx(Tx5)

        load_B1.previousBlock.addTx(Tx4)
        for b in [B2, load_B1]:
            self.assertFalse(b.is_valid(), "This Blocks should be invalid")


if __name__ == "__main__":
        unittest.main()
