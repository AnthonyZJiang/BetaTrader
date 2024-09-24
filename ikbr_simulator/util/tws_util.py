import time
from ibapi.client import *
from ibapi.wrapper import *

class TWSApp(EWrapper, EClient):
    
    def __init__(self):
        EClient.__init__(self, self)
        
    def nextValidId(self, orderId: int):
        self.request_scanner_parameters()
     
    def request_scanner_parameters(self):
        self.reqScannerParameters()
        print("Requested ScannerParameters.")
    
    def scannerParameters(self, xml: str):
        with open('scanner.xml', 'w') as f:
            f.write(xml)
        print("ScannerParameters received.")
        

if __name__ == '__main__':
    app = TWSApp()
    app.connect("127.0.0.1", 7496, clientId=1)
    print("Connected to TWS.")
    app.run()
