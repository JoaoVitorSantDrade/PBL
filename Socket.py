import socket
import Config
import json
from datetime import datetime
import codecs
from Hidrante import Hidrante
import asyncio

class Client:
    payload_size = Config.PAYLOAD_SIZE

    def __init__(self,host,port):
        self.host = host
        self.port = port

    def alterar_endereco(self,host,port):
        self.host = host
        self.port = port

    def connect_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        servidor = (self.host, self.port)
        print("Cliente conectando no endereço %s:%s " % servidor)
        return sock, servidor

    def connect_to_server(self,servidor,sock):
        sock.settimeout(10)
        sock.connect(servidor)
        sock.settimeout(None)
        return sock

    def connect_tcp_hidrometro(self, Hidrante):

        if Hidrante.fechado == False:
            sock,servidor = Client.connect_sock(self)
            try:
                
                sock = Client.connect_to_server(self,servidor,sock)
                x = Hidrante.getDadoJSON()
                message = x #Config.TEST_MESSAGE
                sock.sendall(message.encode())

                amount_received = 0
                amount_expected = len(message)

                dado = None
                while amount_received < amount_expected:
                    dado = sock.recv(Config.PACKET_SIZE)
                    amount_received += len(dado)

                dado = dado.decode() # Decodifica o Json (string) recebido do servidor
                dado = json.loads(dado) # Carrega a string em um Json


            except ConnectionError as e:
                print("Erro na conexão: %s" %str(e))
            except TimeoutError as te:
                print("Conexão não foi estabelecida em tempo adequado")
            finally:
                print("Fechando conexão com o servidor")
                sock.close
        else:
            print("Hidrometro fechado - Conexão não estabelecida")

    def connect_tcp_nuvem(self, Hidrante):
        sock,servidor = Client.connect_sock(self)
        try:

            sock = Client.connect_to_server(self,servidor,sock)

            x = Hidrante.getDadoJSON()
            message = x #Config.TEST_MESSAGE
            sock.sendall(message.encode())

            amount_received = 0
            amount_expected = len(message)

            dado = None
            while amount_received < amount_expected:
                dado = sock.recv(Config.PACKET_SIZE)
                amount_received += len(dado)

            dado = dado.decode() # Decodifica o Json (string) recebido do servidor
            dado = json.loads(dado) # Carrega a string em um Json
            print("Recebido: %s" %dado) #Cliente recebendo dados do servidor

        except ConnectionError as e:
            print("Erro na conexão: %s" %str(e))
        except TimeoutError as te:
            print("Conexão não foi estabelecida em tempo adequado")
        finally:
            print("Fechando conexão com o servidor")
            sock.close

class Server:
    payload_size = Config.PAYLOAD_SIZE
    hid_list = {}
    ip_list = []

    def __init__(self,host,port):
        self.host = host
        self.port = port

    def serverTCP_hidrometro(self,hidrante): #Receber requisições da Nuvem
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
                    client_adress = client.getpeername()
                    client.send(data)  #Reenviamos os bytes do Json
                    data = data.decode() #Decodificamos os bytes utf-8
                    data = json.loads(data) #Carregamos os bytes dentro de um Json
                    client_ip = {"IP":client_adress[0]}
                    data.update(client_ip)
                    print(data)
                    hidrante.setDadoJson(data)
                    #Server.add_to_list(self,data) #Passamos o Json para ser adicionado a lista de Hidrantes do servidor
                    client.close()
            
            except TimeoutError as errt: 
                print("O tempo de espera do servidor foi excedido! - %s" % errt)
                print(self.hid_list)
                break

    def serverTCP_nuvem(self): #Receber requisições dos Hidrometros
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
                    client_adress = client.getpeername()
                    client.send(data)  #Reenviamos os bytes do Json
                    data = data.decode() #Decodificamos os bytes utf-8
                    data = json.loads(data) #Carregamos os bytes dentro de um Json
                    print(client_adress)
                    #data.update()
                    Server.add_to_list(self,data) #Passamos o Json para ser adicionado a lista de Hidrantes do servidor
                    client.close()
            
            except TimeoutError as errt: 
                print("O tempo de espera do servidor foi excedido! - %s" % errt)
                print(self.hid_list)
                break

    def http_serverTCP(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        servidor = (Config.HOST_EXTERNA, Config.PORT_EXTERNA)
        sock.bind(servidor)

        print("Servidor externo iniciando no endereço %s:%s" % servidor)
        sock.listen(Config.SERVER_LISTEN)
        sock.settimeout(Config.TIMEOUT_EXTERNO)
        while True:
            try:
                print ("Aguardando mensagens de clientes...")
                client, address = sock.accept() #Espera receber algum pacote
                data = client.recv(Config.PAYLOAD_SIZE) #Recebemos bytes de uma requisição http
                if data:
                    request = Server.normalize_line_endings(data.decode()) 
                    request_head, request_body = request.split('\n\n', 1)
                    print("Head do request:\n%s " % request_head)
                    print("Body do request:\n%s" % request_body)
                    horario = datetime.now().strftime("%H:%M:%S")
                    response = Server.http_header(horario,Config.HOST_EXTERNA,"text/html; charset=utf-8")
                    html_template = codecs.open("template.html", 'r','utf-8').read()
                    response = response + html_template
                    client.sendall(response.encode("utf-8"))
                    client.close()
            except TimeoutError as errt: 
                print("O tempo de espera do servidor foi excedido! - %s" % errt)
                break

    def http_header(Date,Servidor,Content_type):
        return "HTTP/1.1 200 OK \r\nDate: "+ Date +"\r\nServer: "+ Servidor +"\r\nContent-Type: "+Content_type+"\r\n\r\n"
        
    def normalize_line_endings(s):
        return ''.join((line + '\n') for line in s.splitlines())

    def add_to_list(self,Json):
        Server.hid_list[Json["ID"]] = json.dumps(Json) # Salva o Json em formato string numa Lista
        

if __name__ == '__main__':
    servidor = Server(Config.HOST,Config.PORT)
    asyncio.run(
        servidor.serverTCP()
    ) 