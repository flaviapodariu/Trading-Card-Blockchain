from enum import Enum

class Rarity(Enum):
    Common = 0
    Rare = 1
    Epic = 2
    Legendary = 3

    @classmethod
    def from_int(cls, value: int):
        try:
            return cls(value)
        except ValueError:
            raise ValueError("Invalid integer for Rarity")
        
    @classmethod
    def from_string(cls, str_rarity: str):
        try:
           return cls[str_rarity].value
        except KeyError:
            raise ValueError(f"Invalid string for {cls.__name__}: {str_rarity}")    

    def __str__(self):
        return self.name


# Define Class as an Enum
class Class(Enum):
    Warrior = 0
    Mage    = 1
    Rogue   = 2
    Priest  = 3
    Hunter  = 4
    Warlock = 5
    Shaman  = 6
    Druid   = 7
    Paladin = 8


    @classmethod
    def from_int(cls, value: int):
        try:
            return cls(value)
        except ValueError:
            raise ValueError("invalid integer for Class")
        
    @classmethod
    def from_string(cls, str_class: str):
        try:
           return cls[str_class].value
        except KeyError:
            raise ValueError(f"Invalid string for {cls.__name__}: {str_class}")
        
    def __str__(self):
        return self.name


# Define Power as an Enum
class Power(Enum):
    Low = 0
    Medium = 1
    High = 2

    @classmethod
    def from_int(cls, value: int):
        try:
            return cls(value)
        except ValueError:
            raise ValueError("invalid integer for Power")
    
    @classmethod
    def from_string(cls, str_power: str):
        try:
           return cls[str_power].value
        except KeyError:
            raise ValueError(f"Invalid string for {cls.__name__}: {str_power}")
        
    def __str__(self):
        return self.name


# Define CardProperties class
class CardProperties:

    def __init__(self, class_type: Class, rarity: Rarity, power: Power):
        self.class_type = class_type
        self.rarity = rarity
        self.power = power

    @classmethod
    def new_card_properties(cls, bytes: list[int]):
        try:
            class_type = Class.from_int(bytes[0])
            rarity = Rarity.from_int(bytes[1])
            power = Power.from_int(bytes[2])
            return cls(class_type, rarity, power)
        except ValueError as e:
            raise ValueError(f"Error creating CardProperties: {e}")

    def __str__(self):
        return f"Class: {self.class_type}, Rarity: {self.rarity}, Power: {self.power}"
    
    def to_dict(self):
        return {
            "class": self.class_type.name,
            "rarity": self.rarity.name,
            "power": self.power.name
        }