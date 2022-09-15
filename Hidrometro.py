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

    def HidrometroServer(self,host_server,port_server): #Recebe os dados do servidor (Nuvem)
        servidor_hidrometro = Socket.Server(host_server,port_server)
        self.Server = servidor_hidrometro
        servidor_hidrometro.serverTCP_hidrometro(self.hidrante)
    
    def HidrometroClient(self,host_to_connect,port_to_connect): #Envia os dados para o servidor (Nuvem)
        while True:
            print("Conexão iniciada")
            conexao_tcp = Socket.Client(host_to_connect,port_to_connect)
            conexao_tcp.connect_tcp_hidrometro(self.hidrante)
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

    #Ter dois objetos Hidrometro

    try:
        server_process = Process(target=hidrometro.HidrometroClient, args=(connect_host,connect_port,)).start()
        client_process = Process(target=hidrometro.HidrometroServer, args=(ip_host,ip_port,)).start()
    except KeyboardInterrupt:
        server_process.join()
        client_process.join()
        print("Fechando os processos")   
    except Exception as Err:
        print(Err)
    finally:
        print("Fechando o programa")   


if __name__ == '__main__':
    main()