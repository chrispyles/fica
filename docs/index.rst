``fica`` documentation
======================

.. toctree::
    :maxdepth: 3
    :hidden:

    api_reference

``fica`` is a Python library for managing and documenting the structure of user-specified
configurations. With it, you can create Python classes with easily-documentable fields that make it
easy to configure applications with user input and leverage the code analysis and completion tools
provided by your IDE to make development quicker and less error-prone.


Defining configurations
-----------------------

Configurations in ``fica`` are represented as subclasses of the :py:class:`fica.Config` class which
contain fields set to instances of the :py:class:`fica.Key` class which stores information about the
key (e.g. description, default value, subkeys).

Here's a simple configuration class:

.. code-block:: python

    class MyConfig(fica.Config):

        foo = fica.Key(description="a value for foo")

        bar = fica.Key(description="a value for bar", default=1)

As shown above, you can provide a description for the key using the ``description`` argument and
a default value using the ``default`` argument. If you don't provide a default value, ``fica`` will
default the value to ``None``.

For keys that have nested subconfigurations, you can define a nested :py:class:`fica.Config` class
and pass this to the ``subkey_container`` argument. ``fica`` will handle instantiating and
populating nested config ojects when you instatiate the root config object.

.. code-block:: python

    class MyConfig(fica.Config):

        foo = fica.Key(description="a value for foo")

        class BarValue:

            baz = fica.Key(description="a value for baz", default=True)

            quux = fica.Key(description="a value for quux", default=1)

        bar = fica.Key(description="a value for bar", subkey_container=BarValue)

If you provide a subkey container but do not specify a default value, ``fica`` automatically sets
the default to the special value :py:obj:`fica.SUBKEYS`, a singleton object provided by
``fica`` that represents that a key's default value should be an instance of its subkey container
class with its default values.


Factories
+++++++++

For cases in which a new instance of the default value must be generated each time the config is
created, you can pass a zero-argument factory function to the ``factory`` argument to generate the
value. This is very useful for creating keys for pass-by-reference types like lists and
dictionaries or other stateful values:

.. code-block:: python

    fica.Key("foo", factory=lambda: [])

    my_counter = 0
    def my_factory():
        global my_counter
        my_counter += 1
        return my_counter

    fica.Key("bar", factory=my_factory)

Note that the factory function is only called if the user does **not** specify a value for the key.


Validating values
+++++++++++++++++

Keys can also type-check the values users provide using the ``type_`` argument, which
accepts a single type or a tuple of types (like ``isinstance``).

.. code-block:: python

    fica.Key("foo", type_=(int, float))

If ``type_`` is provided and the user inputs a value that is not of the specified type(s), the key
will raise a ``TypeError``.

For simplicity, if a key is of a specific type or nullable, you can set ``allow_none`` to ``True``
instead of providing ``NoneType`` as one of the allowed types.

.. code-block:: python

    fica.Key("foo", type_=(int, float), allow_none=True)

For more complex validations, ``fica`` provides some validators that can be used to check values
specified by the user. These validators are in the :py:mod:`fica.validators` module, and instances
of these classes can be passed to the ``validator`` argument of the :py:class:`fica.Key`
constructor. When a user specifies a value that is invalid according to this validator, a
``ValueError`` is raised with a message for the user.

For example, to assert that a value is one of a specific set of possible values, you can use the
:py:class:`fica.validators.choice` validator. This validator takes as its only argument a list of
possible values:

.. code-block:: python

    fica.Key("foo", validator=fica.validators.choice([1, 2, 3]))

You can also specify a custom validation function that has been decorated with the
:py:class:`fica.validators.validator` decorator. Validator functions should accept a single argument
and return ``None`` if the value is valid and a string with an error message for the user if it is
invalid. If a validator function does not return a value of type ``str | None``, a ``TypeError`` is
raised.

.. code-block:: python

    @fica.validators.validator
    def is_even_validator(value):
        if value % 2 != 0:
            return f"{value} is not even"

    fica.Key("foo", validator=is_even_validator)

``fica`` checks the type of a value before calling any validators, so if you're using ``type_`` in
conjunction with a validator, you can rely on the value passed to your validation function being of
the correct type.

A full list of available validators can be found in the :ref:`API reference<api_ref_validators>`.


Using configurations
--------------------

The :py:class:`fica.Config` class provides a simple constructor that accepts as its only argument
a ``dict`` mapping strings corresponding to field names to the values specified by the user. Any
fields that don't have an entry in the dictionary are mapped to their default values in the
resulting instance.

Because the subkey containers are themselves subclasses of :py:class:`fica.Config`, users need only
specify the keys in a nested structure that they wish to edit. In the example above, passing
``{"bar": {"baz": False}}`` to the ``MyConfig`` constructor would produce a ``BarValue`` instance
with ``baz`` set to ``False`` and ``quux`` set to ``1`` (its default).

.. code-block:: python

    # this class is the same as above, but reproduced here for convenience
    class MyConfig(fica.Config):

        foo = fica.Key(description="a value for foo")

        class BarValue:

            baz = fica.Key(description="a value for baz", default=True)

            quux = fica.Key(description="a value for quux", default=1)

        bar = fica.Key(description="a value for bar", subkey_container=BarValue)


    MyConfig({"foo": False})          # results in foo=False, bar={baz=True, quux=1}
    MyConfig({"bar": {"baz": False}}) # results in foo=None, bar={baz=False, quux=1}
    MyConfig("foo": False, "bar": 3}) # results in foo=False, bar=3

By default, ``fica`` assumes that the name of a key in the user-specified configuration is the same
as the name of the attribute in the :py:class:`fica.Config` subclass (e.g., in the example above,
a user-specified value with key ``foo`` maps to the ``foo`` attribute of ``MyConfig``). To specify
a different name from the attribute name, add the ``name`` argument to the :py:class:`fica.Key`
constructor; when this value is provided, ``fica`` ignores the name of the attribute in the config
class and instead looks for a key with the specified name in the user config. This behavior can be
useful for allowing key names that collide with the names of methods offered by the
:py:class:`fica.Config` class.

.. code-block:: python

    class MyConfig(fica.Config):

        foo = fica.Key(name="bar")

    MyConfig({"bar": 2}) # results in foo=2

Note that the default constructor for :py:class:`fica.Config` has a ``documentation_mode`` argument
that defaults to ``False``. When ``fica`` creates an instance of this config class to document its
configurations, it will set this argument to ``True``; this can be useful for cases in which you
override the default constructor to perform validations or set other values before initializing the
config. The example below demonstrates the use of this argument.

.. code-block:: python

    class MyConfig(fica.Config):

        foo = fica.Key(description="an even number", type_=int)

        def __init__(self, user_config, documentation_mode=False):
            if not documentation_mode:
                if foo % 2 != 0:
                    raise ValueError("foo is odd!")

            super().__init__(user_config, documentation_mode=documentation_mode)

(Note that it is possible to achieve the same effect as in this example with validators, which is
the preferred method for doing so, but we did it this way here to illustrate the use of the
``documentation_mode`` argument.)

Once you have instantiated the config class, accessing the values of each field is the same as any
attribute access in Python. Fields that have subkey containers (and aren't defaulted/overridden to a
value other than an instance of a config class) are mapped to instances of their subkey container
class.

.. code-block:: python

    >>> my_config = MyConfig()
    >>> my_config.foo
    >>> my_config.bar.baz
    ... True
    >>> my_config = MyConfig({"bar": 1})
    >>> my_config.bar
    ... 1

By default, a user can override the default value of a key with subkeys to be some other value that
will prevent the nested configurations from being accessible via the :py:class:`fica.Config`
instance. For example, consider the following case:

.. code-block:: python
    
    class MyConfig(fica.Config):

        class BarValue:

            baz = fica.Key(description="a value for baz", default=True)

        bar = fica.Key(description="a value for bar", subkey_container=BarValue)
    
    my_config = MyConfig({"bar": 1})

This results in ``my_config.bar`` being set to ``1``, meaning that attempts to access fields in the
``BarValue`` config (i.e. ``my_config.bar.baz``) will error. To prevent users from being able to
override the subkey container with their own value, set ``enforce_subkeys`` to ``True`` in the
:py:class:`fica.Key` constructor. This will require that the user-specified value for that key be
a dictionary that contains values for the fields of the subkey container.

.. code-block:: python

    class MyConfig(fica.Config):

        class BarValue:

            baz = fica.Key(description="a value for baz", default=True)

        bar = fica.Key(
            description="a value for bar", subkey_container=BarValue, enforce_subkeys=True)
    
    my_config = MyConfig({"bar": 1})              # throws an error

    my_config = MyConfig({"bar": {"baz": False}})
    my_config.bar.baz                             # returns False

To update the values in a :py:class:`fica.Config` object after it has been instantiated, use the
:py:meth:`update<fica.Config.update>` method:

.. code-block:: python

    class MyConfig(fica.Config):

        foo = fica.Key(description="a value for foo")

        class BarValue:

            baz = fica.Key(description="a value for baz", default=True)

            quux = fica.Key(description="a value for quux", default=1)

        bar = fica.Key(description="a value for bar", subkey_container=BarValue)

    my_config = MyConfig()
    my_config.update({"bar": {"quux": 2}})
    my_config.bar.baz                       # returns True
    my_config.bar.quux                      # returns 2

By default, the provided user config dictionary can contain keys that are not present in the config
class, and they are ignored. To validate that a user has not provided unexpected configs (e.g. to
alert the user to typos), set ``require_valid_keys=True`` in the constructor. This setting is also
applied to calls to ``update``.

.. code-block:: python

    # continuing with MyConfig from above
    my_config = MyConfig({"baz": 1}, require_valid_keys=True)     # throws an error

    my_config = MyConfig({"foo": 1}, require_valid_keys=True)     # no error
    my_config.update({"baz": 1})                                  # throws an error

:py:class:`fica.Config` also provides a method :py:meth:`fica.Config.get_user_config` for generating
a dictionary that could be passed to the config class constructor to re-create the config. The
returned dictionary contains all keys that are mapped to values other than their defaults, recursing
into keys with subkeys. This can be useful for serializing configuration objects to be reloaded
later.

.. code-block:: python

    # continuing with MyConfig from the last example
    >>> my_config = MyConfig({"foo": 1, "bar": {"quux": 2}})
    >>> my_config.get_user_config()
    ... {"foo": 1, "bar": {"quux": 2}}
    >>> my_config = MyConfig({"foo": 1, "bar": False})
    >>> my_config.get_user_config()
    ... {"foo": 1, "bar": False}


.. _documenting:

Documenting configurations
--------------------------

``fica`` provides a Sphinx extension that can be used to create code blocks for documenting
configurations, their default values, and their descriptions. The main piece of this extension is
the ``fica`` directive, which uses Sphinx's code blocks to display the configurations. To use the
directive, pass the importable name of a :py:class:`fica.Config` subclass as the only argument to
the directive.

To use the ``fica`` Sphinx extension, add ``fica.sphinx`` to the ``extensions`` list in your Sphinx
``conf.py`` file:

.. code-block:: python

    extensions = [
        ...,
        "fica.sphinx",
    ]

For example, say that we have the following in a file called ``fica_demo.py``:

.. literalinclude:: fica_demo.py
    :language: python

To document the class ``fica_demo.Config``, you would use the following in your RST file:

.. code-block:: rst

    .. fica:: fica_demo.Config

This would produce the following:

.. fica:: fica_demo.Config

The default format for configurations is YAML, but you can also choose JSON by setting the
``format`` option to ``json``:

.. code-block:: rst

    .. fica:: fica_demo.Config
       :format: json

This produces:

.. fica:: fica_demo.Config
    :format: json
