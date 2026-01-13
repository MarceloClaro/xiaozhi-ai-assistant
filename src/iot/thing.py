import inspect
import json
from typing import Any, Callable, Dict, List


class ValueType:
    BOOLEAN = "boolean"
    NUMBER = "number"
    STRING = "string"
    FLOAT = "float"
    ARRAY = "array"  # 
    OBJECT = "object"  # 
    LIST = "array"  # LIST para ARRAY de


class Property:
    def __init__(self, name: str, description: str, getter: Callable):
        self.name = name
        self.description = description
        self.getter = getter

        if not inspect.iscoroutinefunction(getter):
            raise TypeError(f"Property getter for '{name}' must be an async function.")

        self.type = ValueType.STRING  # Tipo
        self._type_determined = False

    def _determine_type(self, value: Any):
        """
        ValorTipo.
        """
        if isinstance(value, bool):
            self.type = ValueType.BOOLEAN
        elif isinstance(value, int):
            self.type = ValueType.NUMBER
        elif isinstance(value, float):
            self.type = ValueType.FLOAT
        elif isinstance(value, str):
            self.type = ValueType.STRING
        elif isinstance(value, (list, tuple)):
            self.type = ValueType.ARRAY
        elif isinstance(value, dict):
            self.type = ValueType.OBJECT
        else:
            raise TypeError(f"NãoSuportadodeTipo: {type(value)}")

    def get_descriptor_json(self) -> Dict:
        return {"description": self.description, "type": self.type}

    async def get_state_value(self):
        """
        Valor.
        """
        value = await self.getter()
        # SeVezes getter，Tipo
        if not self._type_determined:
            self._determine_type(value)
            self._type_determined = True
        return value


class Parameter:
    def __init__(self, name: str, description: str, type_: str, required: bool = True):
        self.name = name
        self.description = description
        self.type = type_
        self.required = required
        self.value = None

    def get_descriptor_json(self) -> Dict:
        return {"description": self.description, "type": self.type}

    def set_value(self, value: Any):
        self.value = value

    def get_value(self) -> Any:
        return self.value


class Method:
    def __init__(
        self,
        name: str,
        description: str,
        parameters: List[Parameter],
        callback: Callable,
    ):
        self.name = name
        self.description = description
        self.parameters = {param.name: param for param in parameters}
        self.callback = callback

        # Forçar
        if not inspect.iscoroutinefunction(callback):
            raise TypeError(f"Method callback for '{name}' must be an async function.")

    def get_descriptor_json(self) -> Dict:
        return {
            "description": self.description,
            "parameters": {
                name: param.get_descriptor_json()
                for name, param in self.parameters.items()
            },
        }

    async def invoke(self, params: Dict[str, Any]) -> Any:
        """
        .
        """
        # ConfigurandoParâmetroValor，ProcessandoTipo
        for name, value in params.items():
            if name in self.parameters:
                param = self.parameters[name]
                # SeParâmetroTipo  STRING，Valor  dictoulist，paraJSONCaracteres（C++Versão）
                if param.type == ValueType.STRING and isinstance(value, (dict, list)):
                    param.set_value(json.dumps(value, ensure_ascii=False))
                else:
                    param.set_value(value)

        # PesquisarParâmetro
        for name, param in self.parameters.items():
            if param.required and param.get_value() is None:
                raise ValueError(f"Parâmetro: {name}")

        # 
        return await self.callback(self.parameters)


class Thing:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.properties = {}
        self.methods = {}

    def add_property(self, name: str, description: str, getter: Callable) -> None:
        self.properties[name] = Property(name, description, getter)

    def add_method(
        self,
        name: str,
        description: str,
        parameters: List[Parameter],
        callback: Callable,
    ) -> None:
        self.methods[name] = Method(name, description, parameters, callback)

    def get_descriptor_json(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "properties": {
                name: prop.get_descriptor_json()
                for name, prop in self.properties.items()
            },
            "methods": {
                name: method.get_descriptor_json()
                for name, method in self.methods.items()
            },
        }

    async def get_state_json(self) -> Dict:
        """
        dispositivoestado.
        """
        state = {}
        for name, prop in self.properties.items():
            state[name] = await prop.get_state_value()

        return {
            "name": self.name,
            "state": state,
        }

    async def invoke(self, command: Dict) -> Any:
        """
        .
        """
        method_name = command.get("method")
        if method_name not in self.methods:
            raise ValueError(f"NãoExiste: {method_name}")

        parameters = command.get("parameters", {})
        return await self.methods[method_name].invoke(parameters)
