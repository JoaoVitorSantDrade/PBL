import multiprocessing
import re
import socket
import Config
import json
from datetime import datetime
import codecs
from Hidrante import Hidrante
import asyncio
from multiprocessing import Process, Value, Array

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
                print(x)
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

    def connect_tcp_nuvem(self, bytes):
        sock,servidor = Client.connect_sock(self)
        try:

            bytes = bytes.decode()
            print(bytes)
            sock = Client.connect_to_server(self,servidor,sock)
            sock.sendall(bytes.encode())

            amount_received = 0
            amount_expected = len(bytes)

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
    

    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.hid_list = {} #Guarda dados dos hidrometros
        self.ip_list = []

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
                client,adress = sock.accept() #Espera receber algum pacote
                data = client.recv(Config.PAYLOAD_SIZE) #Recebemos bytes de um Json encoded em utf-8
                if data:
                    client.send(data)  #Reenviamos os bytes do Json
                    data = data.decode() #Decodificamos os bytes utf-8
                    data = json.loads(data) #Carregamos os bytes dentro de um Json
                    hidrante.setDadoJson(data)
                    client.close()
            
            except TimeoutError as errt: 
                print("O tempo de espera do servidor foi excedido! - %s" % errt)
                break

    def serverTCP_nuvem(self,num_hidrometros): #Receber requisições dos Hidrometros
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        servidor = (self.host, self.port)
        sock.bind(servidor)

        print("Servidor iniciando no endereço %s:%s" % servidor)
        sock.listen(Config.SERVER_LISTEN)
        sock.settimeout(Config.TIMEOUT)
        while True:
            try:
                print ("Aguardando requisições de clientes...")
                client,adress = sock.accept() #Espera receber algum pacote json
                data = client.recv(Config.PAYLOAD_SIZE) #Recebemos bytes de um Json encoded em utf-8
                if data:
                   
                    client_adress = client.getpeername()
                    client.send(data)  #Reenviamos os bytes do Json
                    data = data.decode() #Decodificamos os bytes utf-8
                    data = json.loads(data) #Carregamos os bytes dentro de um Json
                    client_ip = {"IP":client_adress[0]}
                    data.update(client_ip)
                    self.add_to_list(data) #Passamos o Json para ser adicionado a lista de Hidrantes do servidor
                    print(len(self.hid_list))
                    self.size = len(self.hid_list)
                    num_hidrometros.value = self.size
                    
                    client.close()
            
            except TimeoutError as errt: 
                print("O tempo de espera do servidor foi excedido! - %s" % errt)
                print(self.hid_list)
                break

    def http_serverTCP(self,num_hidrometros):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        servidor = (self.host, self.port)
        sock.bind(servidor)

        print("API iniciando no endereço %s:%s" % servidor)
        sock.listen(Config.SERVER_LISTEN)
        sock.settimeout(Config.TIMEOUT_EXTERNO)
        while True:
            try:
                print ("Aguardando requisições http...\n\n")
                client, address = sock.accept() #Espera receber algum pacote
                data = client.recv(Config.PAYLOAD_SIZE) #Recebemos bytes de uma requisição http
                if data:
                    request = Server.normalize_line_endings(data.decode()) 
                    request_head, request_body = request.split('\n\n', 1)
                    print("Head do request:\n%s " % request_head)
                    print("Body do request:\n%s" % request_body)
                    self.size = num_hidrometros.value
                    print("O tamanho eh: " + str(self.size))

                    if self.size > 0:
                        if "GET" in request_head:
                            self.GET_response(request_head)
                        elif "POST" in request_head:
                            self.POST_response(request_head)
                        elif "PUT" in request_head:
                            self.PUT_response(request_head)
                        elif "PATCH" in request_head:
                            self.PATCH_response(request_head)
                        elif "DELETE" in request_head:
                            self.DELETE_response()

                        for x in range(len(Server.hid_list)):
                            obj = self.hid_list[x]
                            js = json.loads(obj)
                            print(js["consumo"])

                    horario = datetime.now().strftime("%H:%M:%S")
                    response = Server.http_header(horario,Config.HOST_EXTERNA,"text/html; charset=utf-8")
                    html_template = codecs.open("template.html", 'r','utf-8').read()
                    response = response + html_template
                    client.sendall(response.encode("utf-8"))
                    client.close()

            except TimeoutError as errt: 
                print("O tempo de espera do servidor HTTP foi excedido! - %s" % errt)
                break

    def http_header(Date,Servidor,Content_type):
        return "HTTP/1.1 200 OK \r\nDate: "+ Date +"\r\nServer: "+ Servidor +"\r\nContent-Type: "+Content_type+"\r\n\r\n"
        
    def normalize_line_endings(s):
        return ''.join((line + '\n') for line in s.splitlines())

    def particionarReferer(self,request):
        aft = request.partition("Vazao=")[2]
        vazao,at,aft = aft.partition("&")
        aft = aft.partition("Vazamento=")[2]
        vazamento,at,aft = aft.partition("&")
        aft = aft.partition("Fechado=")[2]
        fechado,at,aft = aft.partition("\n")

        turple = (vazao,vazamento,fechado)

        return turple

    def GET_response(self,request):

        turple = self.particionarReferer(request)
        return turple


    def POST_response(self,request):
        pass

    def PUT_response(self,request):
        pass

    def PATCH_response(self,request):
        pass

    def DELETE_response(self,request):
        pass

    def add_to_list(self,Json):
        self.hid_list[Json["ID"]] = json.dumps(Json) # Salva o Json em formato string numa Lista
        

if __name__ == '__main__':
    servidor = Server(Config.HOST,Config.PORT)
    asyncio.run(
        servidor.serverTCP()
    ) 