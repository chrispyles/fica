import fica

CONFIG = fica.Config([
    fica.Key(
        name="foo",
        description="a value for foo",
        default=False,
    ),
    fica.Key(
        name="bar",
        description="a value for bar",
        subkeys=[
            fica.Key(
                name="baz",
                default=1,
            ),
            fica.Key(
                name="qux",
                default="qux",
                description="a value for qux"
            )
        ]
    ),
    fica.Key(
        name="quuz",
        description="a value for quuz",
    ),
])
