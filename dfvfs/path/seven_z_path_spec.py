# -*- coding: utf-8 -*-
"""The zip path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import location_path_spec


class SevenZPathSpec(location_path_spec.LocationPathSpec):
  """Class that implements the 7z file path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_7Z

  def __init__(self, location=None, parent=None, **kwargs):
    """Initializes the path specification object.

       Note that the 7z file path specification must have a parent.

    Args:
      location: optional 7z file internal location string prefixed with a path
                separator character. The default is None.
      parent: optional parent path specification (instance of PathSpec).
              The default None.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification

    Raises:
      ValueError: when parent is not set.
    """
    if not parent:
      raise ValueError(u'Missing parent value.')

    super(SevenZPathSpec, self).__init__(
        location=location, parent=parent, **kwargs)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(SevenZPathSpec)
