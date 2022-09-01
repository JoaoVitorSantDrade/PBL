from asyncio.windows_events import NULL
import socket
import Config
import json
import re

from Hidrante import Hidrante

class Client:
    host = Config.HOST
    port = Config.PORT
    payload_size = Config.PAYLOAD_SIZE

    def __init__(self,host,port):
        self.host = host
        self.port = port

    def alterar_endereco(self,host,port):
        self.host = host
        self.port = port

    def connect(self, Hidrante):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        servidor = (self.host, self.port)
        print("Cliente conectando no endereço %s:%s " % servidor)
        try:
            sock.connect(servidor)
        except Exception as e:
            print("Erro na conexão: %s" %str(e))

        try:
            x = Hidrante.getDadoJSON()
            x = json.dumps(x)
            message = x #Config.TEST_MESSAGE
            sock.sendall(message.encode())

            amount_received = 0
            amount_expected = len(message)

            dado = NULL
            while amount_received < amount_expected:
                dado = sock.recv(Config.PACKET_SIZE)
                amount_received += len(dado)

            dado = json.loads(dado)
            print("Recebido: %s" %dado) #Cliente recebendo dados do servidor


        except Exception as e:
            print("Erro no envio da mensagem: %s" %str(e))

        finally:
            print("Fechando conexão com o servidor")
            sock.close

class Server:
    host = Config.HOST
    port = Config.PORT
    payload_size = Config.PAYLOAD_SIZE
    hid_list = {}

    def __init__(self,host,port):
        self.host = host
        self.port = port

    def alterar_endereco(self,host,port):
        self.host = host
        self.port = port

    def rodar_servidor(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        servidor = (self.host, self.port)
        sock.bind(servidor)

        print("Servidor iniciando no endereço %s:%s" % servidor)
        sock.listen(Config.SERVER_LISTEN)
        sock.settimeout(Config.TIMEOUT)
        while True:
            try:
                print ("Aguardando mensagens de clientes...")
                client, address = sock.accept() #Espera receber algum pacote
                data = client.recv(Config.PAYLOAD_SIZE)        
                if data:
                    client.send(data)
                    data = data.decode()             
                    data = json.dumps(data)                        
                    Server.add_to_list(self,data)
                    #print ("Enviou %s para o endereço %s" % (data, address))
                    client.close()
                    # end connection
            except Exception as err: #ainda nao vai
                print("O tempo de espera do servidor foi excedido! - %s" % err)
                break

    def add_to_list(self,o):
        print(json.decoder(o))
        resp = ServerResponse(o[0],o[1],o[2],o[3],o[4])
        print("jason da resposta: %s" % resp.getJson())
        #Server.hid_list[ID] = resp.getJson()
        #print(Server.hid_list)

    def getNumberFromString(self,string):
        print(string)
        number = int(''.join(filter(str.isdigit, string )))
        return number

class ServerResponse:

    def __init__(self,id,vazao,consumo,vazamento,fechado):
        self.id = id
        self.vazao = vazao
        self.consumo = consumo
        self.vazamento = vazamento
        self.fechado = fechado
        print(id)

    def atualizar(self,id,consumo,vazao,vazamento,fechado):
        self.id = id
        self.vazao = vazao
        self.consumo = consumo
        self.vazamento = vazamento
        self.fechado = fechado

    def getJson(self):
        x = {
            "ID": self.id,
            "consumo": self.consumo,
            "vazao": self.vazao,
            "vazamento": self.vazamento,
            "fechado": self.fechado
        }
        x = json.dumps(x)
        return x


if __name__ == '__main__':
    servidor = Server(Config.HOST, Config.PORT)
    servidor.rodar_servidor()