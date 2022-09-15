import json
import Config

class Hidrante:
    id = 1000

    def __init__(self,consumo,vazao,vazamento,fechado):
        self.consumo = consumo
        self.vazao = vazao
        self.vazamento = vazamento
        self.fechado = fechado
        self.id = Hidrante.id
        Hidrante.id = Hidrante.id + 1

    def AlterarConsumo(self,consumo):
        self.consumo = consumo

    def AlterarVazao(self,vazao):
        self.vazao = vazao

    def AlterarVazamento(self,vazamento):
        self.vazamento = vazamento

    def AlterarFechado(self,fechado):
        self.fechado = fechado
        
    def getConsumo(self):
        return self.consumo

    def getVazao(self):
        return self.vazao

    def getVazamento(self):
        return self.vazamento

    def getFechado(self):
        return self.fechado

    def getID(self):
        return self.id
        
    def getDadoJSON(self):
        x = {
            "ID": self.id,
            "consumo": self.consumo,
            "vazao": self.vazao,
            "vazamento": self.vazamento,
            "fechado": self.fechado
        }
        x = json.dumps(x)
        #print(x)
        return x

    def setDadoJson(self,Json):
        self.consumo = Json["consumo"]
        self.vazao = Json["vazao"]
        self.vazamento = Json["vazamento"]
        self.fechado = Json["fechado"]