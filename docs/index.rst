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
have a :py:meth:`fica.Key.from_dict` method that turns a Python dictionary into a
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


.. _configs:

Configurations
--------------

Configurations are represented by the :py:class:`fica.Config` class.


.. _documenting:

Documenting configurations
==========================

``fica`` also provides a Sphinx extension that can be used to create code blocks for documenting
configurations, their default values, and their descriptions.


.. fica:: fica_demo.CONFIG

.. fica:: fica_demo.CONFIG
    :format: json

.. code-block:: rst

    .. fica:: fica_demo.CONFIG
