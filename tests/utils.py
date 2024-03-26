class JavaHelper:
    @staticmethod
    def convert(v: list[int]) -> bytes:
        return b"".join(
            map(
                lambda x: x.to_bytes(1, "little", signed=True),
                v,
            )
        )

    @staticmethod
    def rconvert(v: bytes) -> list[int]:
        return list(
            map(
                lambda x: int.from_bytes(
                    x.to_bytes(1, "little"), "little", signed=True
                ),
                v,
            )
        )
