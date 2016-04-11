# -*- coding: utf-8 -*-
"""Error related attribute container object definitions."""

from plaso.containers import interface


class ExtractionError(interface.AttributeContainer):
  """Class to represent an extraction error attribute container.

  Attributes:
    name: a string containing the parser or parser plugin name.
    description: a string containing the description of the error.
    path_spec: optional path specification of the file entry (instance of
               dfvfs.PathSpec) or None.
  """

  def __init__(
      self, name, description, path_spec=None, level=None, filename=None,
      line_number=None):
    """Initializes a parse error.

    Args:
      name: a string containing the parser or parser plugin name.
      description: a string containing the description of the error.
      path_spec: optional path specification of the file entry (instance of
                 dfvfs.PathSpec).
      level: the logging level for the error.
      filename: the filename of the python file that called teh error.
      line_number: the line number that called this error.
    """
    super(ExtractionError, self).__init__()
    self.description = description
    self.name = name
    self.path_spec = path_spec
    self.level = level
    self.filename = filename
    self.line_number = line_number
