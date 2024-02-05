from pydantic import BaseModel


class DatabaseErrorResponseSchema(BaseModel):

    detail: str
