from abc import ABC, abstractmethod


class Tool(ABC):
    name: str
    description: str
    parameters: dict  # JSON Schema object

    @abstractmethod
    async def execute(self, args: dict) -> str: ...

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
