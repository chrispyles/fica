"""Tests for ``fica.exporter``"""

import pytest

from textwrap import dedent

from fica import Config, Key
from fica.exporter import create_exporter, JsonExporter, YamlExporter


def test_that_sample_config_raise_if_not_in_doc_mode_works(sample_config):
    """
    Tests that the class returned by the ``sample_config`` fixture raises an error when it is not
    instantiated in documentation mode if indicated.
    """
    sample_config.raise_if_not_in_doc_mode = True
    with pytest.raises(RuntimeError):
        sample_config()


class TestJsonExporter:
    """
    Tests for ``fica.exporter.JsonExporter``.
    """

    def test_export(self, sample_config):
        """
        Test for the ``export`` method.
        """
        sample_config.raise_if_not_in_doc_mode = True
        sample_config.foo.required = True
        exported_config = JsonExporter().export(sample_config)
        assert exported_config == dedent("""\
            {
              "foo": null,     // foo
              "bar": {         // bar
                "baz": 1,      // baz
                "quux": null
              },
              "quuz": {
                // Default value: 1
                "corge": true
              },
              "grault": 2,
              "garplish": 3
            }
        """).strip()


class TestYamlExporter:
    """
    Tests for ``fica.exporter.YamlExporter``.
    """

    def test_export(self, sample_config):
        """
        Test for the ``export`` method.
        """
        sample_config.raise_if_not_in_doc_mode = True
        sample_config.foo.required = True
        exported_config = YamlExporter().export(sample_config)
        assert exported_config == dedent("""\
            foo: null      # foo
            bar:           # bar
              baz: 1       # baz
              quux: null
            quuz:
              # Default value: 1
              corge: true
            grault: 2
            garplish: 3
        """).strip()


def test_create_exporter():
    """
    Test for ``fica.exporter.create_exporter``.
    """
    exporter = create_exporter("json")
    assert isinstance(exporter, JsonExporter)

    exporter = create_exporter("yaml")
    assert isinstance(exporter, YamlExporter)

    # test errors
    with pytest.raises(ValueError):
        create_exporter("foo")
