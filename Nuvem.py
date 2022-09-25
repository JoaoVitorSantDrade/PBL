from shutil import ExecError
import Hidrante
import Socket
import Config
from multiprocessing import Process, Manager
import time
import os
import json

class Nuvem:
    
    def __init__(self):
        self.Server = None


    def HidrometroInterface(self,num_hidrometros):
        print("Bem vindo ao painel de controles dos hidrometros!")
        while True:
            escolha = input("<1> - Ver lista de Hidrometros\n<2> - Alterar vazão de hidrometro\n<3> - Abrir hidrometro\n<4> - Fechar hidrometro\n<5> - Alterar intervalo de envio de dados\n<6> - Vazamento de hidrometro\n<7> - Historico de hidrometro\n<8> - Boleto de hidrometro\n")
            if not escolha.isnumeric():
                escolha = -1
            else:
                escolha = int(escolha)

            if escolha == 1: #Funcionando ok
                os.system('cls' if os.name == 'nt' else 'clear')
                contador = 1
                for key, value in num_hidrometros._getvalue().items(): #Itera sobre os elementos do dicionario e os adiciona no json
                    doc = json.loads(value) # Carrega o json de uma string
                    print("<%s> - ID %s - Consumo (%.2fm³) | Vazão (%.2fm³/s) - Fechado: %s | Vazamento: %s" % (str(contador),doc["ID"],float(doc["consumo"]),float(doc["vazao"]),str(doc["fechado"]),str(doc["vazamento"])))
                    contador = contador + 1
                input("\nPressione qualquer tecla para retornar\n")
                os.system('cls' if os.name == 'nt' else 'clear')

            elif escolha == 2:
                os.system('cls' if os.name == 'nt' else 'clear')
                resp = 0
                selector = input("Digite o ID do hidrometro que deseja alterar vazão: ")
                if not selector.isnumeric():
                    selector = -1
                else:
                    selector = int(selector)

                for key, value in num_hidrometros._getvalue().items(): #Itera sobre os elementos do dicionario e os adiciona no json
                    doc = json.loads(value) # Carrega o json de uma string
                    if(doc["ID"] == selector):
                        doc["vazao"] = float(input("Vazão anterior: %sm³/s\nDigite a nova vazão: " % doc["vazao"]))
                        num_hidrometros[doc["ID"]] = json.dumps(doc)
                        resp = 1
                if resp == 0:
                    input("Hidrometro inexistente.\nPressione qualquer tecla para retornar...\n")
                else:
                    input("Hidrometro %s teve sua vazão alterada com sucesso\nPressione qualquer tecla para retornar...\n" % str(selector))
                os.system('cls' if os.name == 'nt' else 'clear')

            elif escolha == 3:
                os.system('cls' if os.name == 'nt' else 'clear')
                resp = 0
                selector = input("Digite o ID do hidrometro que deseja abrir: ")
                if not selector.isnumeric():
                    selector = -1
                else:
                    selector = int(selector)

                for key, value in num_hidrometros._getvalue().items(): #Itera sobre os elementos do dicionario e os adiciona no json
                    doc = json.loads(value) # Carrega o json de uma string
                    if(doc["ID"] == selector):
                        if(doc["fechado"] == True):
                            doc["fechado"] = False
                            num_hidrometros[doc["ID"]] = json.dumps(doc)
                            resp = 1
                        else:
                            resp = 2
                        #enviar info p/ hidrometro
                if resp == 0:
                    input("Hidrometro inexistente.\nPressione qualquer tecla para retornar...\n")
                elif resp == 1:
                    input("Hidrometro %s foi aberto com sucesso\nPressione qualquer tecla para retornar...\n" % str(selector))
                else:
                    input("Hidrometro %s já se encontra aberto\nPressione qualquer tecla para retornar...\n" % str(selector))
                os.system('cls' if os.name == 'nt' else 'clear')


            elif escolha == 4:
                os.system('cls' if os.name == 'nt' else 'clear')
                resp = 0
                selector = input("Digite o ID do hidrometro que deseja fechar: ")
                if not selector.isnumeric():
                    selector = -1
                else:
                    selector = int(selector)

                for key, value in num_hidrometros._getvalue().items(): #Itera sobre os elementos do dicionario e os adiciona no json
                    doc = json.loads(value) # Carrega o json de uma string
                    if(doc["ID"] == selector):
                        if(doc["fechado"] == False):
                            doc["fechado"] = True
                            num_hidrometros[doc["ID"]] = json.dumps(doc)
                            resp = 1
                        else:
                            resp = 2
                        #enviar info p/ hidrometro
                if resp == 0:
                    input("Hidrometro inexistente.\nPressione qualquer tecla para retornar...\n")
                elif resp == 1:
                    input("Hidrometro %s foi fechado com sucesso\nPressione qualquer tecla para retornar...\n" % str(selector))
                else:
                    input("Hidrometro %s já se encontra fechado\nPressione qualquer tecla para retornar...\n" % str(selector))
                os.system('cls' if os.name == 'nt' else 'clear')


            elif escolha == 5:
                os.system('cls' if os.name == 'nt' else 'clear')
                resp = 0
                selector = input("Digite o ID do hidrometro que deseja alterar o intervalo de envio de dados: ")
                if not selector.isnumeric():
                    selector = -1
                else:
                    selector = int(selector)

                for key, value in num_hidrometros._getvalue().items(): #Itera sobre os elementos do dicionario e os adiciona no json
                    doc = json.loads(value) # Carrega o json de uma string
                    if(doc["ID"] == selector):
                        doc["delay"] = float(input("intervalo anterior: %ss\nDigite o novo intervalo: " % doc["delay"]))
                        num_hidrometros[doc["ID"]] = json.dumps(doc)
                        resp = 1
                if resp == 0:
                    input("Hidrometro inexistente.\nPressione qualquer tecla para retornar...\n")
                else:
                    input("Hidrometro %s teve seu intervalo alterado com sucesso\nPressione qualquer tecla para retornar...\n" % str(selector))
                os.system('cls' if os.name == 'nt' else 'clear')
                
            elif escolha == 6:
                os.system('cls' if os.name == 'nt' else 'clear')
                resp = 0
                selector = input("Digite o ID do hidrometro que deseja alterar o vazamento: ")
                if not selector.isnumeric():
                    selector = -1
                else:
                    selector = int(selector)

                for key, value in num_hidrometros._getvalue().items(): #Itera sobre os elementos do dicionario e os adiciona no json
                    doc = json.loads(value) # Carrega o json de uma string
                    if(doc["ID"] == selector):
                        valor = float(input("Vazamento anterior: %sm³/s\nDigite o novo vazamento: " % doc["vazamento_valor"]))
                        doc["vazamento_valor"] = valor
                        if valor > 0:
                            doc["vazamento"] = True
                        else:
                            doc["vazamento"] = False
                            
                        num_hidrometros[doc["ID"]] = json.dumps(doc)
                        resp = 1
                if resp == 0:
                    input("Hidrometro inexistente.\nPressione qualquer tecla para retornar...\n")
                else:
                    input("Hidrometro %s teve seu vazamento alterado com sucesso\nPressione qualquer tecla para retornar...\n" % str(selector))
                os.system('cls' if os.name == 'nt' else 'clear')

            elif escolha == 7:
                os.system('cls' if os.name == 'nt' else 'clear')
                resp = 0
                selector = input("Digite o ID do hidrometro que deseja ver o historico: ")
                if not selector.isnumeric():
                    selector = -1
                else:
                    try:
                        f = open("historico/hidrometro-"+selector+".txt","rb")
                        contador = 1
                        while True:
                            Json = f.readline()
                            if not Json:
                                input("Todo o historico para o hidrometro requisitado foi mostrado\nPressione qualquer tecla para retornar...")
                                break
                            else:
                                Json = json.loads(Json)
                                variables = (contador,str(Json["date"]),str(Json["consumo"]),str(Json["vazao"]),str(Json["vazamento"]),str(Json["vazamento_vazao"]),str(Json["fechado"]),str(Json["delay"]))
                                print("<%i> - %s | consumo: %sm³ - vazão: %sm³/s | vazamento: %s - vazão do vazamento: %sm³/s | fechado: %s | intervalo: %s" % variables)
                                contador = contador + 1
                        f.close()
                    except FileNotFoundError as fnfe:
                        input("Não foi encontrado um historico para o hidrometro requisitado\nPressione qualquer tecla para retornar...")
                os.system('cls' if os.name == 'nt' else 'clear')


            elif escolha == 8:
                os.system('cls' if os.name == 'nt' else 'clear')
                resp = 0
                valor_a_pagar = 0
                selector = input("Digite o ID do hidrometro que deseja receber o boleto: ")
                if not selector.isnumeric():
                    selector = -1
                else:
                    selector = int(selector)

                for key, value in num_hidrometros._getvalue().items(): #Itera sobre os elementos do dicionario e os adiciona no json
                    doc = json.loads(value) # Carrega o json de uma string
                    if(doc["ID"] == selector):
                        valor_a_pagar = float(doc["consumo"]) * float(input("Digite o valor por m³ de água consumido: "))
                        resp = 1
                if resp == 0:
                    input("Hidrometro inexistente.\nPressione qualquer tecla para retornar...\n")
                elif valor_a_pagar == 0:
                    input("Você não consumiu nada este mês\nPressione qualquer tecla para retornar")
                else:
                    input("Hidrometro %s teve seu boleto gerado com sucesso\nValor a pagar: %.2f\nPressione qualquer tecla para retornar...\n" % (str(selector),valor_a_pagar))
                os.system('cls' if os.name == 'nt' else 'clear')

            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Escolha uma opção válida!\n")

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

            server_http_process.start()
            server_process.start()
            time.sleep(1)
            servidor_nuvem.HidrometroInterface(lista_hidrometros_conectados)
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