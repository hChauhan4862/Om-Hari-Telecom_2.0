from src.models._base import *

class TeacherAdd(BaseModel):
    name: str = Field(..., title="The name of the Teacher", max_length=50, regex="^[a-zA-Z ]+$")
    email: str = Field(..., title="The email of the Teacher", max_length=50, regex="^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    phone: str = Field(..., title="The phone of the Teacher", max_length=10, regex="^[6-9][0-9]{9}$")
    address: Union[str, None] = Field(default="", title="The address of the Teacher", max_length=100, regex="^[a-zA-Z0-9 ]*$")
    username: str = Field(..., title="The username of the Teacher", max_length=30, regex="^T_[a-zA-Z0-9_]+$")
    password: str = Field(..., title="The password of the Teacher", max_length=50, regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*(_|[^\w])).+$")