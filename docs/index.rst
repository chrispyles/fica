.. fica documentation master file, created by
    sphinx-quickstart on Tue Mar 15 22:20:55 2022.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

``fica`` documentation
======================

.. toctree::
    :maxdepth: 3
    :hidden:

    api_reference

``fica`` is a Python library for managing and documenting the structure of user-specified
configurations. With it, you can create dictionaries of configurations that contain default values
and descriptions for easily configuring applications with user input and documenting available
configurations and their defaults.


Creating configurations
=======================

``fica``'s Python API provides to main classes for defining the structure of configurations:
:ref:`keys<keys>` and :ref:`configs<configs>`.


.. _keys:

Keys
----

Configurations in ``fica`` are represented as a list of keys which have a name and optionally a
default value, subkeys, and a description. These keys are represented by the :py:class:`fica.Key`
class, which accepts all of these as arguments.

The simplest kind of key, one with no default value or subkeys, is created by passing the name of
the key to the constructor:

.. code-block:: python

    fica.Key("foo")

To set a default, provide a value to the ``default`` argument:

.. code-block:: python

    fica.Key("foo", default=False)

If you don't provide a default value, ``fica`` sets it to the special value :py:obj:`fica.EMPTY`,
a singleton object that ``fica`` provides representing that a key should not be included in the
configurations dictionary unless a value is specified by the user.

To include a description in your :ref:`documentation<documenting>`, pass a string to the
``description`` argument:

.. code-block:: python

    fica.Key("foo", description="a value for foo")

For keys that map to a dictionary of more configurations, keys provide the ``subkeys`` argument.
This argument should receive a list of :py:class:`fica.Key` objects that represent the key's
subkeys.

.. code-block:: python

    fica.Key("foo", description="configurations for foo", subkeys=[
        fica.Key("bar", description="a value for bar"),
        fica.Key("baz", description="a value for baz"),
    ])

If you provide subkeys but do not specify a default value, ``fica`` automatically sets the default
to the special value :py:obj:`fica.SUBKEYS`, another singleton object provided by ``fica`` that
represents that a key's default value should be a dictionary mapping its subkeys to their default
values.

In order to facilitate easily loading configuration structures from external files, keys also
have a :py:meth:`from_dict<fica.Key.from_dict>` method that turns a Python dictionary into a
:py:class:`fica.Key` instance provided a dictionary mapping constructor argument names to their
values:

.. code-block:: python

    fica.Key.from_dict({
        "name": "foo",
        "default": False,
        "subkeys": [
            {
                "name": "bar",
                "default": False,
            },
        ],
    })


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

``fica`` checks the type of a value before calling any validators, so if you're using a validator in
conjunction with a validator, you can rely on the value passed to your validation function being of
the correct type.

A full list of available validators can be found in the :ref:`API reference<api_ref_validators>`.


.. _configs:

Configurations
--------------

Configurations are represented by the :py:class:`fica.Config` class, which can be instantiated by
passing a list of :py:class:`fica.Key` instances to its constructor, or from a list of dictionaries
via the :py:meth:`fica.Config.from_list` method.

.. code-block:: python

    fica.Config([
        fica.Key("foo"),
        fica.Key("bar"),
    ])

The :py:class:`fica.Config` class is how ``fica`` converts configurations provided by the user into
a dictionary containing all keys with their default values. To do this, use the
:py:meth:`fica.Config.to_dict` method, which takes as its only argument a dictionary containing the
values specified by the user.

.. code-block:: python

    config = fica.Config([...])
    config.to_dict(user_config)

The dictionary returned by :py:meth:`fica.Config.to_dict` contains every key-value pair in the
dictionary passed to it (unless a value for a key in the configuration is not of the correct type,
in which case a ``TypeError`` is raised). It also contains every other key in the configuration 
not contained in the provided dictionary mapped to its default value unless its default is
:py:obj:`fica.EMPTY`, in which case the key is *not* included in the returned dictionary.

You can force ``fica`` to include keys mapped to :py:obj:`fica.EMPTY` by setting ``include_empty``
to ``True``:

.. code-block:: python

    config.to_dict(user_config, include_empty=True)


.. _documenting:

Documenting configurations
==========================

``fica`` provides a Sphinx extension that can be used to create code blocks for documenting
configurations, their default values, and their descriptions. The main piece of this extension is
the ``fica`` directive, which uses Sphinx's code blocks to display the configurations. To use the
directive, pass the importable name of a :py:class:`fica.Config` object as the only argument to
the directive.

For example, say that we have the following in a file called ``fica_demo.py``:

.. literalinclude:: fica_demo.py
    :language: python

To document the object ``fica_demo.Config``, you would use the following in your RST file:

.. code-block:: rst

    .. fica:: fica_demo.Config

This would produce the following:

.. fica:: fica_demo.Config

Note that even though the default for ``quuz`` is :py:obj:`fica.EMPTY` (and would therefore not be
included in the dictionary returned by :py:meth:`fica.Config.to_dict` unless specified by the user),
the documentation produced by ``fica`` still includes it mapped to ``None``.

The default format for configurations is YAML, but you can also choose JSON by setting the
``format`` option to ``json``:

.. code-block:: rst

    .. fica:: fica_demo.Config
       :format: json

This produces:

.. fica:: fica_demo.Config
    :format: json


