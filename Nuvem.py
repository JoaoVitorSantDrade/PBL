from shutil import ExecError
import Hidrante
import Socket
import Config
from multiprocessing import Process, Manager
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
        self.Server.http_serverTCP(num_hidrometros,host_server)


def main():
    ip_host = input("Digite o IP do servidor da nuvem e da API: ")
    ip_port = int(input("Digite a Porta do servidor da nuvem: "))

    servidor_nuvem = Nuvem()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("A porta para a API lida nos arquivos de configurações foi: " + str(Config.PORT_EXTERNA) + "\n")

    with Manager() as manager:
        try:
            lista_hidrometros_conectados = manager.dict()
            server_process = Process(target=servidor_nuvem.NuvemServer, args=(ip_host,ip_port,lista_hidrometros_conectados,)) #95
            server_http_process = Process(target=servidor_nuvem.NuvemServerHTTP, args=(ip_host,Config.PORT_EXTERNA,lista_hidrometros_conectados,)) #120

            server_process.start()
            time.sleep(1)
            server_http_process.start()
            
        except KeyboardInterrupt:
            pass
        except Exception as err:
            print("Erro: " + str(err))
        finally:
            server_process.join()
            server_http_process.join()
            print("Fechando o servidor")


if __name__ == '__main__':
    main()