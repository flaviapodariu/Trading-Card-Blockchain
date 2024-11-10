from enum import Enum
from types import SimpleNamespace
from card_props import CardProperties

# Enum for EsdtTokenType
class EsdtTokenType(Enum):
    Fungible = 0
    NonFungible = 1
    SemiFungible = 2
    Meta = 3
    Invalid = 4

    @classmethod
    def from_int(cls, value: int):
        try:
            return cls(value)
        except ValueError:
            raise ValueError("Invalid integer for token_type")

    def __str__(self):
        return self.name


# Class for EsdtTokenData
class EsdtTokenData:
    def __init__(self, token_type: EsdtTokenType, amount: int, frozen: bool,
                 hash: bytes, name: bytes, attributes: CardProperties, creator: bytes,
                 royalties: int, uris: list[bytes]):
        self.token_type = token_type
        self.amount = amount
        self.frozen = frozen
        self.hash = hash
        self.name = name
        self.attributes = attributes
        self.creator = creator
        self.royalties = royalties
        self.uris = uris

    # Class method to initialize a new EsdtTokenData object
    @classmethod
    def new_esdt_token_data(cls, properties: SimpleNamespace):
        try:
            token_type = EsdtTokenType.from_int(properties.__dict__['token_type'].__discriminant__)
            amount = properties.__dict__['amount']
            frozen = properties.__dict__['frozen']
            # hash = properties.__dict__['hash']
            name = properties.__dict__['name'].decode("utf-8")
            attributes = CardProperties.new_card_properties(list(properties.__dict__['attributes']))
            # creator = properties.__dict__['creator']
            royalties = properties.__dict__['royalties']
            uris = properties.__dict__['uris']
            return cls(token_type, amount, frozen, b'hash', name, attributes, b'creator', royalties, uris)
        except ValueError as e:
            raise ValueError(f"Error creating CardProperties: {e}")


    def to_dict(self):
        return {
            "token_type": self.token_type.name,
            "amount": self.amount,
            "frozen": self.frozen,
            "hash": self.hash.decode("utf-8"),
            "name": self.name,
            "attributes": self.attributes.to_dict(),
            "creator": self.creator.decode("utf-8"),
            "royalties": self.royalties,
            "uris": list("")
        }
