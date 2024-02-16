"""Tests for ``fica.sphinx``"""

from unittest import mock

from fica import Config, __version__
from fica.exporter import create_exporter
from fica.sphinx import FicaDirective, import_and_get_config, setup as setup_sphinx


def generate_export(config: Config, fmt: str) -> str:
    """
    Generate a configuration export in the specified format.

    Args:
        config (``fica.config.Config``): the config object to export
        fmt (``str``): the format to export it to

    Returns:
        ``str``: the exported config object
    """
    return create_exporter(fmt).export(config)


@mock.patch("fica.sphinx.create_exporter")
@mock.patch("fica.sphinx.import_module")
def test_import_and_get_config(mocked_import_module, mocked_create_exporter, sample_config):
    """
    Test for ``fica.sphinx.import_and_get_config``.
    """
    mocked_import_module.return_value.MyObject = sample_config
    import_and_get_config("mypackage.subpackage.MyObject", "yaml")
    mocked_import_module.assert_called_with("mypackage.subpackage")
    mocked_create_exporter.assert_called_with("yaml")
    mocked_create_exporter.return_value.export.assert_called_with(sample_config)


class TestFicaDirective:
    """
    Tests for ``fica.sphinx.FicaDirective``.
    """

    @mock.patch("fica.sphinx.CodeBlock.__init__")
    @mock.patch("fica.sphinx.CodeBlock.run")
    @mock.patch("fica.sphinx.import_and_get_config")
    def test_default_format(self, mocked_get_config, mocked_run, mocked_init, sample_config):
        """
        Test the default format (YAML) of the directive.
        """
        mocked_init.return_value = None
        mocked_get_config.return_value = generate_export(sample_config, "yaml")
        directive = FicaDirective()
        directive.arguments = ["mypackage.MyConfig"]
        directive.options = {}
        directive.run()
        assert directive.content == mocked_get_config.return_value.split("\n")
        assert directive.arguments[0] == "yaml"
        mocked_run.assert_called()

    @mock.patch("fica.sphinx.CodeBlock.__init__")
    @mock.patch("fica.sphinx.CodeBlock.run")
    @mock.patch("fica.sphinx.import_and_get_config")
    def test_yaml_format(self, mocked_get_config, mocked_run, mocked_init, sample_config):
        """
        Test the explicitly-set YAML format of the directive.
        """
        mocked_init.return_value = None
        mocked_get_config.return_value = generate_export(sample_config, "yaml")
        directive = FicaDirective()
        directive.arguments = ["mypackage.MyConfig"]
        directive.options = {"format": "yaml"}
        directive.run()
        assert directive.content == mocked_get_config.return_value.split("\n")
        assert directive.arguments[0] == "yaml"
        mocked_run.assert_called()

    @mock.patch("fica.sphinx.CodeBlock.__init__")
    @mock.patch("fica.sphinx.CodeBlock.run")
    @mock.patch("fica.sphinx.import_and_get_config")
    def test_json_format(self, mocked_get_config, mocked_run, mocked_init, sample_config):
        """
        Test the JSON format of the directive.
        """
        mocked_init.return_value = None
        mocked_get_config.return_value = generate_export(sample_config, "json")
        directive = FicaDirective()
        directive.arguments = ["mypackage.MyConfig"]
        directive.options = {"format": "json"}
        directive.run()
        assert directive.content == mocked_get_config.return_value.split("\n")
        assert directive.arguments[0] == "javascript"
        mocked_run.assert_called()


def test_setup():
    """
    Test for ``fica.sphinx.setup``.
    """
    app = mock.Mock()
    ret = setup_sphinx(app)
    app.add_directive.assert_called_with("fica", FicaDirective)
    assert ret == {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
