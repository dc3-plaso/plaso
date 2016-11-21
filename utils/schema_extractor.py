# -*- coding: utf-8 -*-
"""A helper script used to get and format the database schema for sqlite
plugins. The resulting schema will be placed into your clipboard which can then
be pasted directly into your plugin.

Requires jinja2 and pyperclip python modules.
"""

import argparse
import os
import jinja2
import pyperclip
import sqlite3

from plaso.parsers import sqlite


def _existing_path(path):
  """Validates an existing file path."""
  if not os.path.exists(path):
    raise argparse.ArgumentTypeError(
        u'Could not find path: {0:s}'.format(path))
  return path


if __name__ == u'__main__':

  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument(
      u'database_path', type=_existing_path,
      help=u'The path to the database file to extract schema from.')

  options = arg_parser.parse_args()

  # Get database schema.
  database = sqlite.SQLiteDatabase('bogus')
  with open(options.database_path, u'rb') as file_object:
    database.Open(file_object)
    schema = database.schema

  schema = {
      table: query.replace(u'\n', u'\\n').replace(u'\'', u'\\\'')
      for table, query in schema.items()}
  env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
  template = env.from_string('''
  {% for table, query in schema|dictsort %}
    {% if loop.first %}
      {u'{{ table }}':
    {% else %}
      u'{{ table }}':
    {% endif %}
          u'{{ query|wordwrap(65, wrapstring=" '\n          u'") }}'
            {%- if not loop.last -%}
              ,
            {% else -%}
              }
            {%- endif %}
  {%- endfor %}''')
  schema = template.render(schema=schema)

  pyperclip.copy(schema)


