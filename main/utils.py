from typing import Any, Type



def snap(val: float, mult: float) -> float:
    return mult * round(val / mult)


def coalesce(value: Any, structure: Type) -> Type:
    if isinstance(value, structure):
        return value
    
    if structure == list:
        return [value]
    
    if structure == set:
        return {value,}
    
    if structure == tuple:
        return (value,)
    
    return value
