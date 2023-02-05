import socket 
import unittest
import pickle
import select 

TCP_PORT = 42069
BUFFER_SIZE = 1024

def newServerConnection(ip_addr, port=TCP_PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip_addr,TCP_PORT))
    s.listen()
    return s

def recvObj(socket):
    inputs, outputs, errs = select.select([socket], [], [socket], 6)
    if socket in inputs:
        new_sock,addr = socket.accept()
        all_data = b''
        while True:
            data = new_sock.recv(BUFFER_SIZE)
            if not data: break
            all_data = all_data + data
        return pickle.loads(all_data)
    return None

def sendObj(ip_addr, inObj, port=TCP_PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_addr, TCP_PORT))
    data = pickle.dumps(inObj)
    s.send(data)
    s.close()
    return False



class TransactionTest(unittest.TestCase):
    def test(self):
        server = newServerConnection("127.0.0.1")
        O = recvObj(server)
        print("Success")
        server.close()
        
if __name__ == "__main__":
    unittest.main()
