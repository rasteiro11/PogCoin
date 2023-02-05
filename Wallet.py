import unittest
from Transaction import Tx
from Signatures import generate_keys
from SocketUtils import recvObj, sendObj, newServerConnection

head_blocks = [None]

pr1,pu1 = generate_keys()
pr2,pu2 = generate_keys()
pr3,pu3 = generate_keys()

Tx1 = Tx()
Tx2 = Tx()

Tx1.add_input(pu1, 4.0)
Tx1.add_input(pu2, 1.0)
Tx1.add_input(pu3, 4.8)
Tx2.add_input(pu3, 4.0)
Tx2.add_output(pu2, 4.0)
Tx2.add_reqd(pu1)

Tx1.sign(pr1)
Tx1.sign(pr2)
Tx2.sign(pr3)
Tx2.sign(pr1)


class TransactionTest(unittest.TestCase):
    def test(self):
        try:
            sendObj('localhost',Tx1)
            sendObj('localhost',Tx2)
        except:
            print ("Error! Connection unsuccessful")
        server = newServerConnection('localhost', 5006)
        for i in range(10):
            newBlock = recvObj(server)
            if newBlock:
                break
        server.close()
            
        self.assertTrue(newBlock.is_valid(), "This block must be valid")
        self.assertTrue(newBlock.good_nonce(), "This nonce must be valid")

        for tx in newBlock.data:
            try:
                if tx.inputs[0][0] == pu1 and tx.inputs[0][1] == 4.0:
                    print("Tx1 is present")
                if tx.inputs[0][0] == pu3 and tx.inputs[0][1] == 4.0:
                    print("Tx2 is present")
            except:
                print("Something went terribly wrong")

        for b in head_blocks:
            if newBlock.previousHash == b.computeHash():
                newBlock.previousBlock = b
                head_blocks.remove(b)
                head_blocks.append(newBlock)

if __name__ == "__main__":
    unittest.main()
