from src.iot.thing import Thing


class Lamp(Thing):
    def __init__(self):
        super().__init__("Lamp", "de")
        self.power = False

        #  - Usando getter
        self.add_property("power", "Abrindo", self.get_power)

        #  - UsandoProcessandoDispositivo
        self.add_method("TurnOn", "Abrindo", [], self._turn_on)

        self.add_method("TurnOff", "Fechando", [], self._turn_off)

    async def get_power(self):
        return self.power

    async def _turn_on(self, params):
        self.power = True
        return {"status": "success", "message": "JáAbrindo"}

    async def _turn_off(self, params):
        self.power = False
        return {"status": "success", "message": "JáFechando"}
