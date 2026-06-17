from dataclasses import dataclass


@dataclass
class Subject:
    id: str
    name: str
    color: str

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "color": self.color}

    @classmethod
    def from_dict(cls, data: dict) -> "Subject":
        return cls(id=data["id"], name=data["name"], color=data["color"])
