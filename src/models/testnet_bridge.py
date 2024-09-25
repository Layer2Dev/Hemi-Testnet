import random

from pydantic import BaseModel, validator, root_validator, Field


class TestnetBridgeConfig(BaseModel):
    from_chain: str
    amount: float | list[float]

    calculated_amount: float = Field(init=False)

    @validator('from_chain', pre=True)
    def validate_from_chain(cls, from_chain):
        if from_chain not in ['ERC20', 'OP', 'ARB', 'SEPOLIA']:
            raise ValueError(f'from_chain must be ERC20/OP/ARB. Got {from_chain}')
        return from_chain

    @validator('amount', pre=True)
    def validate_amount(cls, amount):
        if isinstance(amount, list):
            if len(amount) != 2 or not all(isinstance(i, (int, float)) for i in amount):
                raise ValueError('amount list must contain exactly two numeric values')
            return round(random.uniform(amount[0], amount[1]), 7)
        elif isinstance(amount, (int, float)):
            return amount
        raise ValueError('amount must be a numeric value or a list of two numeric values')

    @root_validator(pre=True)
    def set_calculated_fields(cls, values):
        amount = values.get('amount')

        if isinstance(amount, list):
            values['calculated_amount'] = round(random.uniform(amount[0], amount[1]), 7)
        else:
            values['calculated_amount'] = amount

        return values
