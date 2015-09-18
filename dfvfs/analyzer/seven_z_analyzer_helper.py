# -*- coding: utf-8 -*-
"""The 7z format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class SevenZAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the 7z analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_ARCHIVE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_7Z

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.FormatSpecification(
        self.type_indicator)

    format_specification.AddNewSignature(b'7z\xbc\xaf\x27\x1c', offset=0)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(SevenZAnalyzerHelper())
