from shutil import ExecError
import Hidrante
import Socket
import Config
from multiprocessing import Process
import time
class Hidrometro:
    
    def __init__(self,hidrante,delay):   
        self.hidrante = hidrante
        self.delay = delay
        self.mes = 9
        self.ano = 2022
        self.historico = {}
        self.Server = None

    def HidrometroServer(self,host_server,port_server): #Recebe os dados do servidor (Nuvem)
        if(self.Server == None):
            servidor_hidrometro = Socket.Server(host_server,port_server)
            self.Server = servidor_hidrometro
        servidor_hidrometro.serverTCP_hidrometro(self.hidrante)
    
    def HidrometroClient(self,host_to_connect,port_to_connect): #Envia os dados para o servidor (Nuvem)
        while True:
            print("Conexão iniciada")
            self.hidrante.ContabilizarConsumo(self.delay)
            conexao_tcp = Socket.Client(host_to_connect,port_to_connect)
            conexao_tcp.connect_tcp_hidrometro(self.hidrante)
            print("Conexão finalzada!")
            print("Isso é no hidrometroClient - "+ str(self.hidrante.consumo))
            time.sleep(self.delay)

    def AlterarDelay(self,delay):
        self.delay = delay

def main():
    ip_host = input("Digite o IP do servidor do hidrometro: ")
    ip_port = int(input("Digite a Porta do servidor do hidrometro: "))

    hidrante = Hidrante.Hidrante(0,2.5,False,False) #Consumo Vazao Vazamento Fechado
    hidrometro = Hidrometro(hidrante,Config.DELAY)

    connect_host = input("Digite o IP em que devemos nos conectar: ")
    connect_port = int(input("Digite a Porta em que devemos nos conectar: "))

    #Ter dois objetos Hidrometro

    try:
        server_process = Process(target=hidrometro.HidrometroClient, args=(connect_host,connect_port,)).start()
        client_process = Process(target=hidrometro.HidrometroServer, args=(ip_host,ip_port,)).start()
    except KeyboardInterrupt:
        print("Fechando os processos")   
    finally:
        print("Fechando o programa")   


if __name__ == '__main__':
    main()