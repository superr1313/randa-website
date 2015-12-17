# encoding: utf-8

update_config = {
    'template_path': 'src/main/web/app',
    'compiled_path': None,
    'force_compiled': False,
    'environment_args': {
        'autoescape': False,
        'extensions': [
            'jinja2.ext.autoescape',
            'jinja2.ext.with_',
        ],
        'block_start_string': '{%',
        'block_end_string': '%}',
        'variable_start_string': '{!',
        'variable_end_string': '!}',
        'comment_start_string': '<!--',
        'comment_end_string': '-->'
    },
    'globals': None,
    'filters': None,
}
