from typing import TypeVar
from db.models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
