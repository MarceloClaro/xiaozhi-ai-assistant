import asyncio
import json
from typing import Any, Dict, Optional, Tuple

from src.iot.thing import Thing
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ThingManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ThingManager()
        return cls._instance

    def __init__(self):
        self.things = []
        self.last_states = {}  # Estado，VezesdeEstado

    async def initialize_iot_devices(self, config):
        """Inicializandodispositivo.

        ：DispositivoJáparaMCPEm，deAIeestado。
        """
        from src.iot.things.lamp import Lamp

        # Dispositivo
        self.add_thing(Lamp())

    def add_thing(self, thing: Thing) -> None:
        self.things.append(thing)

    async def get_descriptors_json(self) -> str:
        """
        dispositivodeJSON.
        """
        # get_descriptor_json()（RetornoDados），
        # de
        descriptors = [thing.get_descriptor_json() for thing in self.things]
        return json.dumps(descriptors)

    async def get_states_json(self, delta=False) -> Tuple[bool, str]:
        """dispositivodeestadoJSON.

        Args:
            delta: RetornoConversãode，TrueRetornoConversãode

        Returns:
            Tuple[bool, str]: RetornoestadoConversãodeValoreJSONCaracteres
        """
        if not delta:
            self.last_states.clear()

        changed = False

        tasks = [thing.get_state_json() for thing in self.things]
        states_results = await asyncio.gather(*tasks)

        states = []
        for i, thing in enumerate(self.things):
            state_json = states_results[i]

            if delta:
                # PesquisarEstadoConversão
                is_same = (
                    thing.name in self.last_states
                    and self.last_states[thing.name] == state_json
                )
                if is_same:
                    continue
                changed = True
                self.last_states[thing.name] = state_json

            # Pesquisarstate_jsonJá
            if isinstance(state_json, dict):
                states.append(state_json)
            else:
                states.append(json.loads(state_json))  # JSONCaracteres  para

        return changed, json.dumps(states)

    async def get_states_json_str(self) -> str:
        """
        para，deeRetornoValorTipo.
        """
        _, json_str = await self.get_states_json(delta=False)
        return json_str

    async def invoke(self, command: Dict) -> Optional[Any]:
        """dispositivo.

        Args:
            command: nameemethodAguardarInformaçãodeComando

        Returns:
            Optional[Any]: SeEncontradodispositivosucesso，Retorno；entãoexceção
        """
        thing_name = command.get("name")
        for thing in self.things:
            if thing.name == thing_name:
                return await thing.invoke(command)

        # ErroLog
        logger.error(f"DispositivoNãoExiste: {thing_name}")
        raise ValueError(f"DispositivoNãoExiste: {thing_name}")
