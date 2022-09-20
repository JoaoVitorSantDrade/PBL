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

    def connect_sock(self): # Cria e configura um socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        servidor = (self.host, self.port)
        print("Cliente conectando no endereço %s:%s " % servidor)
        return sock, servidor

    def connect_to_server(self,servidor,sock): # Conecta o socket em um servidor
        sock.settimeout(10) 
        sock.connect(servidor)
        sock.settimeout(None)
        return sock

    def connect_tcp_hidrometro(self, Hidrante):

        if Hidrante.fechado == False:
            sock,servidor = Client.connect_sock(self)
            try:
                
                sock = Client.connect_to_server(self,servidor,sock)
                message = Hidrante.getDadoJSON()
                sock.sendall(message.encode())

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

    def serverTCP_nuvem(self,lista_hidrometros): #Receber requisições dos Hidrometros
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
                    data = data.decode() #Decodificamos os bytes utf-8
                    data = json.loads(data) #Carregamos os bytes dentro de um Json
                    client_ip = {"IP":client_adress[0]}
                    data.update(client_ip)
                    lista_hidrometros[data["ID"]] = json.dumps(data)
                    client.close()
            
            except TimeoutError as errt: 
                print("O tempo de espera do servidor foi excedido! - %s" % errt)
                break

    def http_serverTCP(self,lista_hidrometros,host_server):
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

                    horario = datetime.now().strftime("%H:%M:%S")
                    response = Server.http_header(horario,host_server,"application/json; charset=utf-8")

                    if len(lista_hidrometros) > 0:
                        jsonDict = lista_hidrometros._getvalue() #Pega o valor do dictProxy
                        if "GET" in request_head: #Se for uma GET
                            url = self.particionarRequest(request_head) #Separa os valores da url
                            if self.has_numbers(url): #Se tiver um numero = ID
                                if "historico" in url: #Pega o historico do hidrometro especifico
                                    pass
                                elif "boleto" in url: #Pega o boleto do hidrometro especifico
                                    pass
                                else: #Pega o hidrometro em geral
                                    jsonDoc = self.build_json_only(jsonDict,url)
                            else:
                                jsonDoc = self.build_json(jsonDict)

                        elif "POST" in request_head:
                            self.POST_response(request_head)
                        elif "PUT" in request_head:
                            self.PUT_response(request_head)
                        elif "PATCH" in request_head:
                            self.PATCH_response(request_head)
                        elif "DELETE" in request_head:
                            self.DELETE_response()
                    
                    response = response + jsonDoc #Concatena o header com o json criado e o envia para quem fez a requisição

                    client.sendall(response.encode("utf-8"))
                    client.close()

            except TimeoutError as errt: 
                print("O tempo de espera do servidor HTTP foi excedido! - %s" % errt)
                break

    def has_numbers(self,inputString):
        return any(char.isdigit() for char in inputString)

    def build_json_only(self,dict,key_number):
        jsonDoc = "["
        for key, value in dict.items(): #Itera sobre os elementos do dicionario e os adiciona no json
            doc = json.loads(value) # Carrega o json de uma string
            if key_number == str(doc["ID"]): #Compara a URL cm o ID de um json, se for igual, adiciona esse Json no texto
                jsonDoc = jsonDoc + value
                break
        jsonDoc = jsonDoc + "]"
        return jsonDoc

    def build_json(self,dict):
        jsonDoc = "["
        for key, value in dict.items(): #Itera sobre os elementos do dicionario e os adiciona no json
            jsonDoc = jsonDoc + value
            jsonList = list(dict)
            if jsonList[-1] != key: #Adicionar virgula somente se não for o ultimo elemento do dicionario
                jsonDoc = jsonDoc + ","
        jsonDoc = jsonDoc + "]"
        return jsonDoc

    def http_header(Date,Servidor,Content_type):
        return "HTTP/1.1 200 OK \r\nDate: "+ Date +"\r\nServer: "+ Servidor +"\r\nContent-Type: "+Content_type+"\r\nConnection: Keep-Alive" + "\r\n\r\n"
        
    def normalize_line_endings(s):
        return ''.join((line + '\n') for line in s.splitlines())

    def particionarRequest(self,request):
        aft = request.partition("/")[2]
        link_html,at,aft = aft.partition(" HTTP")
        if link_html != None:
            return link_html

    def GET_response(self,request):

        resp = self.particionarRequest(request)
        return resp


    def POST_response(self,request):
        pass

    def PUT_response(self,request):
        pass

    def PATCH_response(self,request):
        pass

    def DELETE_response(self,request):
        pass

if __name__ == '__main__':
    servidor = Server(Config.HOST,Config.PORT)
    asyncio.run(
        servidor.serverTCP()
    ) 