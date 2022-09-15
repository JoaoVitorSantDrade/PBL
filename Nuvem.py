import Hidrante
import Socket
import Config
from multiprocessing import Process
import time
class Hidrometro:
    
    def __init__(self,hidrante,delay):
        self.hidrante = hidrante
        self.delay = delay

    def NuvemServer(self,host_server,port_server): #Recebe dados do Hidrometro
        servidor_hidrometro = Socket.Server(host_server,port_server)
        self.Server = servidor_hidrometro
        servidor_hidrometro.serverTCP()
    
    def NuvemClient(self,host_to_connect,port_to_connect): #Envia dados para hidrometros
        while True:
            print("Conexão iniciada")
            conexao_tcp = Socket.Client(host_to_connect,port_to_connect)
            conexao_tcp.connect_tcp(self.hidrante)
            print("Conexão finalzada!")
            time.sleep(self.delay)

    def NuvemServerHTTP(self,host_server,port_server): #Recebe requisições e responde
        servidor_hidrometro = Socket.Server(host_server,port_server)
        self.Server = servidor_hidrometro
        servidor_hidrometro.serverTCP()

    def NuvemClientHTTP(self,host_to_connect,port_to_connect): # Não sei
        while True:
            print("Conexão iniciada")
            conexao_tcp = Socket.Client(host_to_connect,port_to_connect)
            conexao_tcp.connect_tcp(self.hidrante)
            print("Conexão finalzada!")
            time.sleep(self.delay)
            
    def AlterarDelay(self,delay):
        self.delay = delay

def main():
    ip_host = input("Digite o IP do servidor do hidrometro: ")
    ip_port = int(input("Digite a Porta do servidor do hidrometro: "))

    hidrante = Hidrante.Hidrante(100,100,False,False) #Consumo Vazao Vazamento Fechado
    hidrometro = Hidrometro(hidrante,Config.DELAY)

    connect_host = input("Digite o IP em que devemos nos conectar: ")
    connect_port = int(input("Digite a Porta em que devemos nos conectar: "))



    try:
        server_process = Process(target=hidrometro.HidrometroClient, args=(connect_host,connect_port,)).start()
        client_process = Process(target=hidrometro.HidrometroServer, args=(ip_host,ip_port,)).start()
    except KeyboardInterrupt:
        pass 
    finally:
        print("Fechando o programa")   


if __name__ == '__main__':
    main()