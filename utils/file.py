from pathlib import Path

from django.template import Engine, Context


def gen_file_from_template(template_path, file_path, **context):
    template = Engine().from_string(Path(template_path).read_text())
    context = Context(context, autoescape=False)
    content = template.render(context)
    Path(file_path).write_text(content)
