import importlib

from docutils import nodes
from sphinx.locale import _
from sphinx.util.docutils import SphinxDirective

from ..exporter import create_exporter
from ..version import __version__


def import_and_get_config(object_path: str) -> str:
    """
    """
    mod, cls = object_path.rsplit(".", 1)
    module = importlib.import_module(mod)
    config_object = getattr(module, cls)
    return create_exporter("yaml").export(config_object)


class config(nodes.Structural, nodes.Element):
    pass


def visit_config_node(self, node):
    pass


def depart_config_node(self, node):
    pass


class FicaDirective(SphinxDirective):

    # this enables content in the directive
    has_content = True

    def run(self):
        section_id = 'fica-%d' % self.env.new_serialno('fica')
        section_node = nodes.section(ids=[section_id])
        section_node += nodes.title(_('Config'), _('Config'))

        content = import_and_get_config("\n".join(self.content))
        section_node += nodes.literal_block(_(content), _(content))

        config_node = config()
        config_node += section_node

        return [config_node]


def setup(app):
    app.add_node(config, html=(visit_config_node, depart_config_node))
    app.add_directive('fica', FicaDirective)
    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
