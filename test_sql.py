from sqlmodel import SQLModel, Field
class Test(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
print('SQLModel ok')