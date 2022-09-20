import json
import Config
from multiprocessing import Process
from random import seed
from random import randint
import time

class Hidrante:
    
    def __init__(self,consumo,vazao,vazamento,fechado):
        self.mes = 9
        self.ano = 2022
        self.historico = {}
        self.consumo = consumo
        self.vazao = vazao
        self.vazamento = vazamento
        self.fechado = fechado
        seed(time.time())
        self.id = randint(0,100000)

    def ContabilizarConsumo(self,TempoPassado):
            self.consumo += self.vazao*TempoPassado

    def GerarBoleto(self):
        valor = self.consumo * 10.69
        valor_consumo = (valor,self.consumo)
        self.historico[self.mes,self.ano] = valor_consumo
        if(self.mes == 12):
            self.mes = 0
            self.ano = self.ano + 1
        self.mes = self.mes + 1
        return valor_consumo
           
    def getDadoJSON(self):
        x = {
            "ID": self.id,
            "consumo": self.consumo,
            "vazao": self.vazao,
            "vazamento": self.vazamento,
            "fechado": self.fechado,
            "mes": self.mes,
            "ano": self.ano,
            "historico": self.historico
        }
        x = json.dumps(x)
        return x

    def setDadoJson(self,Json):
        self.consumo = Json["consumo"]
        self.vazao = Json["vazao"]
        self.vazamento = Json["vazamento"]
        self.fechado = Json["fechado"]

if __name__ == '__main__':
    hidro = Hidrante(0,25,False,False)
    hidro.run(Config.CONSUMO_DELAY)