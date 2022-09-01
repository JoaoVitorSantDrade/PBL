from multiprocessing.connection import wait
import Config
import Hidrante
import Socket
from threading import Thread
import time

if __name__ == '__main__':
    servidor = Socket.Server(Config.HOST, Config.PORT)
    cliente = Socket.Client(Config.HOST,Config.PORT)
    hidrante = Hidrante.Hidrante(10,54,30)
    Thread(target=servidor.rodar_servidor).start()
    time.sleep(2)
    Thread(target=cliente.connect(hidrante)).start()
    time.sleep(4)
    Thread(target=cliente.connect(hidrante)).start()

