import fica

conf = fica.Config([
    fica.Key(
        name="foo",
        description="Value of foo",
        default=False,
    ),
    fica.Key(
        name="bar",
        description="Value of bar",
        subkeys=[
            fica.Key(
                name="baz",
                default=1,
            ),
            fica.Key(
                name="quux",
                default="quux",
                description="a config for quux"
            )
        ]
    )
])
