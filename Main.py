from multiprocessing.connection import wait
import Config
import Hidrante
import Socket
from threading import Thread
import time

if __name__ == '__main__':

    cliente = Socket.Client(Config.HOST,Config.PORT)
    hidrante1 = Hidrante.Hidrante(10,54,False,False)
    hidrante2 = Hidrante.Hidrante(26,21,False,False)
    hidrante3 = Hidrante.Hidrante(17,14,False,False)

    time.sleep(2)

    Thread(target=cliente.connect(hidrante1)).start()
    Thread(target=cliente.connect(hidrante2)).start()
    Thread(target=cliente.connect(hidrante3)).start()

    time.sleep(3)
    Thread(target=cliente.connect(hidrante2)).start()

