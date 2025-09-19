import uuid
from datetime import datetime


__all__ = [
    "gen",
    "gen_completions_id",
]


def gen() -> str:
    return str(uuid.uuid4())

def gen_completions_id(uid: str = None) -> str:
    return f"comp-{gen() if uid is None else uid}"
