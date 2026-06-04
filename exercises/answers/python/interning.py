class StringInterner:
    def __init__(self):
        self._str_to_id: dict[str, int] = {}
        self._id_to_str: list[str] = []

    def intern(self, s: str) -> int:
        if s in self._str_to_id:
            return self._str_to_id[s]
        sym_id = len(self._id_to_str)
        self._str_to_id[s] = sym_id
        self._id_to_str.append(s)
        return sym_id

    def resolve(self, sym_id: int) -> str | None:
        if 0 <= sym_id < len(self._id_to_str):
            return self._id_to_str[sym_id]
        return None
