from tws_signals import TWSApp

if __name__ == '__main__':
    front = TWSApp()
    front.connect("127.0.0.1", 7496, clientId=2)
    front.run()