import json
import Config

class Hidrante:
    id = "0000"
    consumo = 0.0
    vazao = 0.0
    vazamento = False

    def __init__(self,consumo,vazao,vazamento):
        self.consumo = consumo
        self.vazao = vazao
        self.vazamento = vazamento

    def AlterarConsumo(self,consumo):
        self.consumo = consumo

    def AlterarVazao(self,vazao):
        self.vazao = vazao

    def AlterarVazamento(self,vazamento):
        self.vazamento = vazamento

    def getDadoJSON(self):
        x = {
            "ID": self.id,
            "consumo": self.consumo,
            "vazao": self.vazao,
            "vazamento": self.vazamento
        }
        x = json.dumps(x)
        return x