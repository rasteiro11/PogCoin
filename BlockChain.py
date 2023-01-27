from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import unittest

class someClass:
    string = None
    def __init__(self, mystring):
        self.string = mystring
    def __repr__(self):
        return self.string

class CBlock:
    data = None 
    previousHash = None
    previousBlock = None

    def __init__(self, data, previousBlock):
        self.data = data
        self.previousBlock = previousBlock
        if previousBlock != None:
            self.previousHash = previousBlock.computeHash()
    
    def computeHash(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data), 'utf8'))
        digest.update(bytes(str(self.previousHash), 'utf8'))
        return digest.finalize()

class CBlockTest(unittest.TestCase):
    def test_compute_hash(self):
        root = CBlock('I am root', None)
        B1 = CBlock("I am child", root)
        B2 = CBlock("I am B1s brother", root)
        B3 = CBlock(12345, B1)
        B4 = CBlock(someClass('Hi there!'), B2)
        B5 = CBlock("Top block", B4)
        
        for block in [B1, B2, B3, B4, B5]:
            self.assertEqual(block.previousBlock.computeHash(), block.previousHash, "Hashes are different")
    def test_detect_tempering(self):
        root = CBlock('I am root', None)
        B1 = CBlock("I am child", root)
        B3 = CBlock(12345, B1)
        B4 = CBlock(someClass('Hi there!'), B3)

        B3.data = 42069 
        self.assertNotEqual(B4.previousBlock.computeHash(), B4.previousHash, "Could not detect tempering")

if __name__ == "__main__":
    unittest.main()
