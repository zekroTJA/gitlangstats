from typing import List


class LanguageModel:
    name: str
    size: int


class RepoModel:
    name: str
    languages: List[LanguageModel]
