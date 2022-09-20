from shutil import ExecError
import Hidrante
import Socket
import Config
from multiprocessing import Process
import time
import os

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
            contador = 0
            print("Conexão iniciada")
            self.hidrante.ContabilizarConsumo(self.delay)

            if(contador == Config.TICKS_TO_GENERATE_PAYMENT):
                print("Gerou boleto")
                self.hidrante.GerarBoleto()
                contador = 0

            conexao_tcp = Socket.Client(host_to_connect,port_to_connect)
            try:
                conexao_tcp.connect_tcp_hidrometro(self.hidrante)
            except:
                print("Erro na conexão do hidrometro")
            print("Conexão finalzada!")
            print("Consumo Atual: "+ str(self.hidrante.consumo))
            contador = contador + 1
            time.sleep(self.delay)

    def AlterarDelay(self,delay):
        self.delay = delay

def main():
    flow = float(input("Digite a vazão do hidrometro: "))
    ip_host = input("Digite o IP do servidor do hidrometro: ")
    ip_port = int(input("Digite a Porta do servidor do hidrometro: "))

    hidrante = Hidrante.Hidrante(0,flow,False,False) #Consumo Vazao Vazamento Fechado
    hidrometro = Hidrometro(hidrante,Config.DELAY)

    connect_host = input("Digite o IP em que devemos nos conectar: ")
    connect_port = int(input("Digite a Porta em que devemos nos conectar: "))

    os.system('cls' if os.name == 'nt' else 'clear')

    print("O seu ID é: %s\nSeu endereço é %s:%s" % (str(hidrante.id),ip_host,ip_port))

    #Ter dois objetos Hidrometro

    try:
        server_process = Process(target=hidrometro.HidrometroClient, args=(connect_host,connect_port,))
        client_process = Process(target=hidrometro.HidrometroServer, args=(ip_host,ip_port,))
        server_process.start()
        client_process.start()
    except KeyboardInterrupt:
        print("Fechando os processos")   
    finally:
        server_process.join()
        client_process.join()
        print("Fechando o programa")   


if __name__ == '__main__':
    main()