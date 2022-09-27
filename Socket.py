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
from time import localtime, strftime


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
        servidor = (self.host, self.port) # Endereço e Portas para se conectar
        print("Cliente conectando no endereço %s:%s " % servidor)
        return sock, servidor

    def connect_to_server(self,servidor,sock): # Conecta o socket em um servidor
        sock.settimeout(10) 
        sock.connect(servidor)
        sock.settimeout(None)
        return sock

    def connect_tcp_hidrometro(self, Hidrante, Hidrometro_conectado):

        sock,servidor = Client.connect_sock(self)
        try:
            
            sock = Client.connect_to_server(self,servidor,sock)
            message = Hidrante.getDadoJSON()
            sock.sendall(message.encode()) # Envia mensagem

            data = sock.recv(1024).decode()
            data = json.loads(data)
            Hidrometro_conectado[0] = json.dumps(data)
            
        except ConnectionError as e:
            print("Erro na conexão: %s" %str(e))
        except TimeoutError as te:
            print("Conexão não foi estabelecida em tempo adequado")
        finally:
            sock.close

class Server:
    payload_size = Config.PAYLOAD_SIZE
    

    def __init__(self,host,port):
        self.host = host
        self.port = port

    def serverTCP_nuvem(self,lista_hidrometros): #Receber requisições dos Hidrometros
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        servidor = (self.host, self.port)
        sock.bind(servidor)

        #print("Servidor iniciando no endereço %s:%s" % servidor)
        sock.listen(Config.SERVER_LISTEN) #escuta até 32 hidrometros diferentes
        sock.settimeout(Config.TIMEOUT) 
        while True:
            try:
                #print ("Aguardando requisições de clientes...")
                client,adress = sock.accept() #Espera receber algum pacote json
                data = client.recv(Config.PAYLOAD_SIZE) #Recebemos bytes de um Json encoded em utf-8
                if data:
                    
                    client_adress = client.getpeername()
                    client_ip = {"IP":client_adress[0]}

                    data = data.decode() #Decodificamos os bytes utf-8
                    data = json.loads(data) #Carregamos os bytes dentro de um Json
                    data.update(client_ip)

                    #Atualiza e sincroniza os dados dos hidrometros com o servidor 
                    if data["ID"] in lista_hidrometros._getvalue():
                        Json = lista_hidrometros._getvalue()[data["ID"]]
                        Json = json.loads(Json)
                        estado = {"fechado":Json["fechado"]}
                        estado2 = {"vazao":Json["vazao"]}
                        estado3 = {"vazamento":Json["vazamento"]}
                        estado4 = {"delay":Json["delay"]}
                        estado5 = {"vazamento_valor":Json["vazamento_valor"]}
                        data.update(estado)
                        data.update(estado2)
                        data.update(estado3)
                        data.update(estado4)
                        data.update(estado5)
                        self.SaveHistorico(data)



                    lista_hidrometros[data["ID"]] = json.dumps(data)
                    data = json.dumps(data)                     

                    client.sendall(data.encode()) #Envia os dados para o hidrometro
                    client.close()

            except TimeoutError as errt: 
                print("O tempo de espera do servidor foi excedido! - %s" % errt)
                break

    def SaveHistorico(self,Json): #Salva o histórico num arquivo txt
        title = str(Json["ID"])
        x = {
            "ID": Json["ID"],
            "date": strftime("%d-%m-%Y %H:%M:%S", localtime()),
            "consumo": Json["consumo"],
            "vazao": Json["vazao"],
            "vazamento": Json["vazamento"],
            "vazamento_vazao": Json["vazamento_valor"],
            "fechado": Json["fechado"],
            "delay": Json["delay"],
        }
        x = json.dumps(x)
        file = open('historico/hidrometro-'+ title + '.txt', 'ab')
        file.write((x+"\n").encode())
        file.close()

    def http_serverTCP(self,lista_hidrometros,host_server): #Servidor da API
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        servidor = (self.host, self.port)
        sock.bind(servidor)

        sock.listen(Config.SERVER_LISTEN)
        sock.settimeout(Config.TIMEOUT_EXTERNO)
        while True:
            try:
                client, address = sock.accept() #Espera receber algum pacote
                data = client.recv(Config.PAYLOAD_SIZE) #Recebemos bytes de uma requisição http
                if data:
                    request = Server.normalize_line_endings(data.decode()) 
                    request_head, request_body = request.split('\n\n', 1) #Separamos a requisição em Header e body

                    horario = datetime.now().strftime("%H:%M:%S")
                    response = Server.http_header(horario,host_server,"application/json; charset=utf-8")

                    if len(lista_hidrometros) > 0:
                        jsonDict = lista_hidrometros._getvalue() #Pega o valor do dictProxy
                        jsonDoc = '{}'
                        if "GET" in request_head: #Se for uma GET
                            url = self.particionarRequest(request_head) #Separa os valores da url
                            url2 = self.particionarRequest2(url)

                            if self.has_numbers(url2[0]): #Se tiver um numero = ID

                                if "historico" in url2[1]: #Pega o historico do hidrometro especifico
                                    jsonDoc = self.build_json_historico(url2[0])

                                elif "boleto" in url2[1]: #Pega o boleto do hidrometro especifico
                                    jsonDoc = self.build_json_boleto(jsonDict,url2[0])

                                elif "fechar" in url2[1]: #Fecha um hidrometro específico
                                    if int(url2[0]) in lista_hidrometros._getvalue():
                                        Json = lista_hidrometros._getvalue()[int(url2[0])]
                                        Json = json.loads(Json)
                                        estado = {"fechado":True}
                                        Json.update(estado)
                                        lista_hidrometros[int(url2[0])] = json.dumps(Json)
                                        jsonDoc = json.dumps(Json)

                                elif "abrir" in url2[1]: #Abre um hidrometro específico
                                    if int(url2[0]) in lista_hidrometros._getvalue():
                                        Json = lista_hidrometros._getvalue()[int(url2[0])]
                                        Json = json.loads(Json)
                                        estado = {"fechado":False}
                                        Json.update(estado)
                                        lista_hidrometros[int(url2[0])] = json.dumps(Json)
                                        jsonDoc = json.dumps(Json)

                                elif "vazao" in url2[1]: #Altra a vazao de um hidrometro específico
                                    url3 = self.particionarRequest2(url2[1])
                                    try:
                                        v = float(url3[1])
                                        if int(url2[0]) in lista_hidrometros._getvalue():
                                            Json = lista_hidrometros._getvalue()[int(url2[0])]
                                            Json = json.loads(Json)
                                            estado = {"vazao":v}
                                            Json.update(estado)
                                            lista_hidrometros[int(url2[0])] = json.dumps(Json)
                                            jsonDoc = json.dumps(Json)
                                    except ValueError:
                                        pass

                                elif "intervalo" in url2[1]: #Altera o intervalo de envio de mensagens de um hidrometro específico
                                    url3 = self.particionarRequest2(url2[1])
                                    try:
                                        v = float(url3[1])
                                        if int(url2[0]) in lista_hidrometros._getvalue():
                                            Json = lista_hidrometros._getvalue()[int(url2[0])]
                                            Json = json.loads(Json)
                                            estado = {"delay":v}
                                            Json.update(estado)
                                            lista_hidrometros[int(url2[0])] = json.dumps(Json)
                                            jsonDoc = json.dumps(Json)
                                    except ValueError:
                                        pass
                                else: #Pega o hidrometro em geral
                                    jsonDoc = self.build_json_only(jsonDict,url)
                            else:
                                jsonDoc = self.build_json(jsonDict)

                        response = response + jsonDoc #Concatena o header com o json criado e o envia para quem fez a requisição

                    client.sendall(response.encode("utf-8")) #Envia a nossa resposta a requisição http
                    client.close()

            except TimeoutError as errt: 
                print("O tempo de espera do servidor HTTP foi excedido! - %s" % errt)
                break

    def has_numbers(self,inputString): #Verifica se na string existe numeros
        return any(char.isdigit() for char in inputString)

    def build_json_boleto(self,dict,key_number): #Cria um json com o valo do consumo do hidrometro
        jsonDoc = "["
        for key, value in dict.items(): #Itera sobre os elementos do dicionario e os adiciona no json
            doc = json.loads(value) # Carrega o json de uma string
            if key_number == str(doc["ID"]): #Compara a URL cm o ID de um json, se for igual, adiciona esse Json no texto
                x = {
                    "ID": doc["ID"],
                    "consumo": doc["consumo"],
                    "valor": (doc["consumo"]*0.132),
                }
                x = json.dumps(x)
                jsonDoc = jsonDoc + x
                break
        jsonDoc = jsonDoc + "]"
        return jsonDoc

    def build_json_historico(self,key_number): #Cria um json com o histórico de um hidrometro especifico
        contador = 0
        jsonDoc = "["
        try:
            f = open("historico/hidrometro-"+key_number+".txt","rb")
            contador = 1
            while True:
                Json = f.readline()
                if not Json:
                    break
                else:
                    Json = json.loads(Json)
                    jsonDoc = jsonDoc + str(contador) +" = " + json.dumps(Json) + ","
                    contador = contador + 1
            f.close()
        except FileNotFoundError as fnfe:
            pass
            #ler aquivo com o ID
            #Salvar cada linha lida como um json diferente
            #Concatenar tudo no json final
        jsonDoc = jsonDoc + "]"
        return jsonDoc

    def build_json_only(self,dict,key_number): # Cria o json de um unico hidrometro
        jsonDoc = "["
        for key, value in dict.items(): #Itera sobre os elementos do dicionario e os adiciona no json
            doc = json.loads(value) # Carrega o json de uma string
            if key_number == str(doc["ID"]): #Compara a URL cm o ID de um json, se for igual, adiciona esse Json no texto
                jsonDoc = jsonDoc + value
                break
        jsonDoc = jsonDoc + "]"
        return jsonDoc

    def build_json(self,dict): # Cria um json cm todos os hidrometros que já se conectaram
        jsonDoc = "["
        for key, value in dict.items(): #Itera sobre os elementos do dicionario e os adiciona no json
            jsonDoc = jsonDoc + value
            jsonList = list(dict)
            if jsonList[-1] != key: #Adicionar virgula somente se não for o ultimo elemento do dicionario
                jsonDoc = jsonDoc + ","
        jsonDoc = jsonDoc + "]"
        return jsonDoc

    def http_header(Date,Servidor,Content_type): # Cria um header de resposta http
        return "HTTP/1.1 200 OK \r\nDate: "+ Date +"\r\nServer: "+ Servidor +"\r\nContent-Type: "+Content_type+"\r\nConnection: Keep-Alive" + "\r\n\r\n"
        
    def normalize_line_endings(s):
        return ''.join((line + '\n') for line in s.splitlines())

    def particionarRequest(self,request):
        aft = request.partition("/")[2]
        link_html,at,aft = aft.partition(" HTTP")
        if link_html != None:
            return link_html

    def particionarRequest2(self,request):
        number,barra,nome = request.partition("/")
        if number != None:
            return (number,nome)

