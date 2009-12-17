"""
This module contains paste templates for setting up an instance to run
"""
from paste.script.templates import Template, var
from paste.util.template import paste_script_template_renderer
from paste.deploy.converters import asint
DEFAULT_PORT = 8088


class InstanceTemplate(Template):
    """
    template creates an instance of spazzer that can be run.
    """
    #remove hardcoded spazzer
    _template_dir = 'templates/default_instance'
    summary = "Spazzer app instance template"
    template_renderer = staticmethod(paste_script_template_renderer)
    egg_plugins = ["PasteScript"]
    vars = [var("server_port",
                "The port this instance will run on default=8088",
                default = DEFAULT_PORT)]

    def pre(self, command, output_dir, vars):
        vars["server_port"] = asint(vars.get("server_port", DEFAULT_PORT))
