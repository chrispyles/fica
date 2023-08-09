import fica

from typing import Any, Optional


class Config(fica.Config):

    foo: bool = fica.Key(
        description="a value for foo",
        default=False,
    )

    class BarValue(fica.Config):

        baz: int = fica.Key(default=1)

        qux: str = fica.Key(
            default="qux",
            description="a value for qux",
        )

    bar: BarValue = fica.Key(
        description="a value for bar",
        subkey_container=BarValue,
    )

    quuz: Optional[Any] = fica.Key(description="a value for quuz")

    class CorgeValue(fica.Config):

        grault = fica.Key(description="a value for grault")

    corge: CorgeValue = fica.Key(
        description="a value for corge",
        default=False,
        subkey_container=CorgeValue,
    )
