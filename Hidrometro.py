from shutil import ExecError
import Hidrante
import Socket
import Config
from multiprocessing import Process, Manager
import time
import os
import json

class Hidrometro:
    
    def __init__(self,hidrante):   
        self.hidrante = hidrante
        self.mes = 9
        self.ano = 2022
        self.historico = {}
        self.Server = None

    def HidrometroServer(self,host_server,port_server,hidrometro_conectado): #Recebe os dados do servidor (Nuvem)
        if(self.Server == None):
            servidor_hidrometro = Socket.Server(host_server,port_server)
            self.Server = servidor_hidrometro
        servidor_hidrometro.serverTCP_hidrometro(self.hidrante,hidrometro_conectado) #Passa um HidroProxy
    
    def HidrometroClient(self,host_to_connect,port_to_connect,hidrometro_conectado): #Envia os dados para o servidor (Nuvem)
        while True: 
            print("Conexão iniciada")
            if(self.hidrante.fechado == False):
                self.hidrante.ContabilizarConsumo()
            else:
                print("Hidrometro fechado - consumo não contabilizado")

            conexao_tcp = Socket.Client(host_to_connect,port_to_connect)
            try:
                conexao_tcp.connect_tcp_hidrometro(self.hidrante,hidrometro_conectado)
            except Exception as err:
                print("Erro na conexão do hidrometro - " + err)
            print("Conexão finalzada!")
            
            lista = hidrometro_conectado._getvalue()
            Json = json.loads(lista[0])
            self.hidrante.vazamento_valor = Json["vazamento_valor"]
            self.hidrante.consumo = Json["consumo"]
            self.hidrante.vazao = Json["vazao"]
            self.hidrante.vazamento = Json["vazamento"]
            self.hidrante.fechado = Json["fechado"]
            self.hidrante.delay = Json["delay"]

            print("Consumo Atual: %s | Vazão Atual: %s | Vazamento Atual: %s" % (str(self.hidrante.consumo),str(self.hidrante.vazao),str(self.hidrante.vazamento_valor)))
            time.sleep(self.hidrante.delay)

def main():

    ip_host = input("Digite o IP do servidor do hidrometro: ")
    ip_port = int(input("Digite a Porta do servidor do hidrometro: "))
    connect_host = input("Digite o IP em que devemos nos conectar: ")
    connect_port = int(input("Digite a Porta em que devemos nos conectar: "))


    os.system('cls' if os.name == 'nt' else 'clear')

    hidro = Hidrante.Hidrante(0,0,False,0.0,True,0.5)

    hidrometro = Hidrometro(hidro)


    print("O seu ID é: %s\nSeu endereço é %s:%s" % (str(hidro.id),ip_host,ip_port))

    with Manager() as manager:
        try:
            hidrometro_conectado = manager.dict()
            hidrometro_conectado[0] = hidrometro.hidrante.getDadoJSON()
            server_process = Process(target=hidrometro.HidrometroClient, args=(connect_host,connect_port,hidrometro_conectado,))
            client_process = Process(target=hidrometro.HidrometroServer, args=(ip_host,ip_port,hidrometro_conectado,))
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