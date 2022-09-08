from asyncio.windows_events import NULL
import socket
import Config
import json
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

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
            message = x #Config.TEST_MESSAGE
            sock.sendall(message.encode())

            amount_received = 0
            amount_expected = len(message)

            dado = NULL
            while amount_received < amount_expected:
                dado = sock.recv(Config.PACKET_SIZE)
                amount_received += len(dado)

            dado = dado.decode() # Decodifica o Json (string) recebido do servidor
            dado = json.loads(dado) # Carrega a string em um Json
            print("Recebido: %s" %dado) #Cliente recebendo dados do servidor


        except Exception as e:
            print("Erro no envio da mensagem: %s" %str(e))

        finally:
            print("Fechando conexão com o servidor")
            sock.close

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        message = "Isso é uma chamada usando GET"
        self.wfile.write(bytes(message, "utf8"))

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.end_headers


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
                data = client.recv(Config.PAYLOAD_SIZE) #Recebemos bytes de um Json encoded em utf-8
                if data:
                    client.send(data)  #Reenviamos os bytes do Json
                    print("Mensagem recebida!")
                    data = data.decode() #Decodificamos os bytes utf-8
                    data = json.loads(data) #Carregamos os bytes dentro de um Json
                    Server.add_to_list(self,data) #Passamos o Json para ser adicionado a lista de Hidrantes do servidor
                    client.close()
                    # end connection
                    with open('hidrometro.json','w') as file:
                        json.dump(self.hid_list,file)
                        #https://flaviocopes.com/python-http-server/
                        #https://stackoverflow.com/questions/28240464/python-http-server-send-json-response
                        #https://gist.github.com/nitaku/10d0662536f37a087e1b
                        #https://stackoverflow.com/questions/45151473/returning-json-using-a-get-request-from-server
                        #Usar o dump pra salvar todos os hidrantes num arquivo Json unico. esse arquivo json unico é oq vai pra web
            except Exception as err: 
                print("O tempo de espera do servidor foi excedido! - %s" % err)
                print(self.hid_list)
                with HTTPServer(('', 8000), handler) as server:
                    server.serve_forever()
                break

    def add_to_list(self,Json):
        Server.hid_list[Json["ID"]] = json.dumps(Json) # Salva o Json em formato string numa Lista
        

if __name__ == '__main__':
    servidor = Server(Config.HOST, Config.PORT)
    servidor.rodar_servidor()