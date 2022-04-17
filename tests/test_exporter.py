"""Tests for ``fica.exporter``"""

import pytest

from textwrap import dedent

from fica.exporter import create_exporter, JsonExporter, YamlExporter


class TestJsonExporter:
    """
    Tests for ``fica.exporter.JsonExporter``.
    """

    def test_export(self, sample_config):
        """
        Test for the ``export`` method.
        """
        exported_config = JsonExporter().export(sample_config)
        assert exported_config == dedent("""\
            {
              "foo": null,
              "bar": {
                "baz": 1
              },
              "quuz": 1,
              "grault": 2,
              "garply": 3
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
        exported_config = YamlExporter().export(sample_config)
        assert exported_config == dedent("""\
            foo: null
            bar:
              baz: 1
            quuz: 1
            grault: 2
            garply: 3
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
