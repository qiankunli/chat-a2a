import uuid6


def uuid7_str() -> str:
    return str(uuid6.uuid7())


def uuid7_hex() -> str:
    """uuid6 id顺序与创建时间一致，许多逻辑依赖该特性"""
    return uuid6.uuid7().hex
