import socket
import Config
import time
import Hidrante
import json
import requests

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

            while amount_received < amount_expected:
                dado = sock.recv(Config.PACKET_SIZE)
                amount_received += len(dado)

        except Exception as e:
            print("Erro no envio da mensagem: %s" %str(e))

        finally:
            print("Fechando conexão com o servidor")
            sock.close


class Server:
    host = Config.HOST
    port = Config.PORT
    payload_size = Config.PAYLOAD_SIZE

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
                client, address = sock.accept()
                data = client.recv(Config.PAYLOAD_SIZE)            
                if data:
                    print ("Dado: %s" %data)
                    client.send(data)
                    print ("Enviou %s bytes para o endereço %s" % (data, address))
                    # end connection
                    timelapsed = time.time()
                    client.close()
            except requests.Timeout as err:
                print("O tempo de espera do servidor foi excedido!")