from shutil import ExecError
import Hidrante
import Socket
import Config
from multiprocessing import Process, Value
import time
import os

class Nuvem:
    
    def __init__(self):
        self.Server = None

    def NuvemServer(self,host_server,port_server,num_hidrometros): #Recebe dados do Hidrometro - recebe dados do TCP_hidrometro
        if(self.Server == None):
            servidor_nuvem = Socket.Server(host_server,port_server)
            self.Server = servidor_nuvem
        self.Server.serverTCP_nuvem(num_hidrometros)

    def NuvemServerHTTP(self,host_server,port_server,num_hidrometros): #Recebe requisições e responde - recebe dados do HTTP (Nossa API)
        if(self.Server == None):
            servidor_hidrometro = Socket.Server(host_server,port_server)
            self.Server = servidor_hidrometro
        self.Server.http_serverTCP(num_hidrometros)


def main():
    ip_host = input("Digite o IP do servidor da nuvem: ")
    ip_port = int(input("Digite a Porta do servidor da nuvem: "))
    ip_api = input("Digite o IP para a API da nuvem: ")

    servidor_nuvem = Nuvem()
    os.system('cls' if os.name == 'nt' else 'clear')
    num_hidrometros = Value('i',0)
    try:
        server_process = Process(target=servidor_nuvem.NuvemServer, args=(ip_host,ip_port,num_hidrometros,)).start() #95
        time.sleep(1)
        server_http_process = Process(target=servidor_nuvem.NuvemServerHTTP, args=(ip_api,Config.PORT_EXTERNA,num_hidrometros,)).start() #120
    except KeyboardInterrupt:
        print("Teste")
    except Exception as err:
        print("Erro: " + err)
    finally:
        print("Iniciando o servidor")
        print("A porta para a API lida nos arquivos de configurações foi: " + str(Config.PORT_EXTERNA))
 


if __name__ == '__main__':
    main()