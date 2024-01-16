from pydantic import BaseModel


class NewFolderSchema(BaseModel):
    folder_name: str


class UpdateFolderNameSchema(BaseModel):
    folder_name: str
    folder_id: str
