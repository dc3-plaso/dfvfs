# -*- coding: utf-8 -*-
"""The 7z file entry implementation."""

from dfvfs.lib import date_time
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import seven_z_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class SevenZDirectory(file_entry.Directory):
  """Class that implements a directory object using py7zlib."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of path.SevenZPathSpec).
    """
    location = getattr(self.path_spec, u'location', None)

    if (location is None or
        not location.startswith(self._file_system.PATH_SEPARATOR)):
      return

    seven_z_file = self._file_system.GetSevenZFile()
    for seven_z_info in seven_z_file.getmembers():
      path = seven_z_info.filename

      if not path or not path.startswith(location[1:]):
        continue

      _, suffix = self._file_system.GetPathSegmentAndSuffix(location[1:], path)

      # Ignore anything that is part of a sub directory or the directory itself.
      if suffix or path == location[1:]:
        continue

      path_spec_location = self._file_system.JoinPath([path])
      yield seven_z_path_spec.SevenZPathSpec(
          location=path_spec_location, parent=self.path_spec.parent)


class SevenZFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using py7zlib."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_7Z

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, seven_z_info=None):
    """Initializes the file entry object.
    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification (instance of path.PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
               The default is False.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system. The default is False.
      seven_z_info: optional 7z info object (instance of py7zlib.ArchiveFile).
                The default is None.
    """
    super(SevenZFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._seven_z_info = seven_z_info

  def _GetDirectory(self):
    """Retrieves the directory object (instance of ZipDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return SevenZDirectory(self._file_system, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the zip info is missing in a non-virtual file entry.
    """
    seven_z_info = self.GetSevenZInfo()
    if not self._is_virtual and seven_z_info is None:
      raise errors.BackEndError(u'Missing 7z info in non-virtual file entry.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = getattr(seven_z_info, u'size', None)

    # Date and time stat information.
    atime = getattr(seven_z_info, u'lastaccesstime', None)
    if atime is not None:
      date_time_values = date_time.Filetime(atime)
      stat_time, stat_time_nano = date_time_values.CopyToStatObject()
      stat_object.atime = stat_time
      stat_object.atime_nano = stat_time_nano
    ctime = getattr(seven_z_info, u'creationtime', None)
    if ctime is not None:
      date_time_values = date_time.Filetime(ctime)
      stat_time, stat_time_nano = date_time_values.CopyToStatObject()
      stat_object.ctime = stat_time
      stat_object.ctime_nano = stat_time_nano
    mtime = getattr(seven_z_info, u'lastwritetime', None)
    if mtime is not None:
      date_time_values = date_time.Filetime(mtime)
      stat_time, stat_time_nano = date_time_values.CopyToStatObject()
      stat_object.mtime = stat_time
      stat_object.mtime_nano = stat_time_nano

    # File entry type stat information.
    if self._is_virtual:
      stat_object.type = stat_object.TYPE_DIRECTORY
    else:
      stat_object.type = stat_object.TYPE_FILE

    return stat_object

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    seven_z_info = self.GetSevenZInfo()

    # Note that the root file entry is virtual and has no 7z_info.
    if seven_z_info is None:
      return u''

    path = getattr(seven_z_info, u'filename', None)
    return self._file_system.BasenamePath(path)

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield SevenZFileEntry(
            self._resolver_context, self._file_system, path_spec)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""
    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return

    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return
    if parent_location == u'':
      parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, u'parent', None)
    path_spec = seven_z_path_spec.SevenZPathSpec(
        location=parent_location, parent=parent_path_spec)
    return SevenZFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetSevenZInfo(self):
    """Retrieves the 7z info file object.

    Returns:
      The 7z info object (instance of py7zlib.ArchiveFile).

    Raises:
      ValueError: if the path specification is incorrect.
    """
    if not self._seven_z_info:
      location = getattr(self.path_spec, u'location', None)
      if location is None:
        raise ValueError(u'Path specification missing location.')

      if not location.startswith(self._file_system.LOCATION_ROOT):
        raise ValueError(u'Invalid location in path specification.')

      if len(location) == 1:
        return

      seven_z_file = self._file_system.GetSevenZFile()
      self._seven_z_info =  seven_z_file.getmember(location[1:])
    return self._seven_z_info
