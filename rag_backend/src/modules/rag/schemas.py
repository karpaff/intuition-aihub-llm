from pydantic import BaseModel
from typing import List


class SourceItem(BaseModel):
    chapter_n: int
    text_chunk: str

class RagAnswer(BaseModel):
    answer: str
    sources: List[SourceItem]