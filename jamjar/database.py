#------------------------------------------------------------------------------
# database.py - Database module
#
# November 2015, Phil Connell
#------------------------------------------------------------------------------

"""Target database."""

__all__ = (
    "Database",
    "Target",
)


import collections
import re


class Database:
    """Database of jam targets."""

    # Mapping from target names to targets.
    _targets = None

    def __init__(self):
        self._targets = collections.OrderedDict()

    def __repr__(self):
        return "{}({} targets)".format(type(self).__name__, len(self._targets))

    def get_target(self, name):
        """Get a target with a given name, creating it if necessary."""
        try:
            target = self._targets[name]
        except KeyError:
            target = Target(name)
            self._targets[name] = target
        return target

    def find_targets(self, name_regex):
        """Iterator that yields all targets whose name matches a regex."""
        for name, target in self._targets.items():
            if re.search(name_regex, name):
                yield target

    def find_rebuilt_targets(self, name_regex):
        """Iterator that yields all targets whose name matches a regex and
           have their rebuilt flag set to True."""
        for target in self.find_targets(name_regex):
            if target.rebuilt:
                yield target


class Target:
    """
    Representation of a jam target.

    .. attribute:: name

        Name of the target (including any grist).

    .. attribute:: deps

        Sequence of targets that this target depends on, in the order that the
        dependencies are reported by Jam.

    .. attributes:: deps_rev

        Set of targets that depend on this target.

    .. attribute:: incs

        Sequence of targets that this target includes (in the Jam sense!) in
        the order that the inclusions are reported by Jam.

    .. attribute:: incs_rev

        Set of targets that include this target.

    .. attribute:: timestamp_chain

        Sequence of targets that this target inherits its timestamp from.

    """

    def __init__(self, name):
        self.name = name
        self.deps = []
        self.deps_rev = set()
        self.incs = []
        self.incs_rev = set()
        self.timestamp = None
        self.binding = None
        self.rebuilt = False
        self.rebuild_info = RebuildInfo()
        self.timestamp_chain = None

    def __repr__(self):
        return "{}({})".format(type(self).__name__, self.name)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        else:
            return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def add_dependency(self, other):
        """Record the target 'other' as depended on by this target."""
        # Dependencies may be parsed more than once, but only one copy allowed
        if self not in other.deps_rev:
            self.deps.append(other)
            other.deps_rev.add(self)

    def add_inclusion(self, other):
        """Record the target 'other' as included by this target."""
        # Inclusions may be parsed more than once, but only one copy allowed
        if self not in other.incs_rev:
            self.incs.append(other)
            other.incs_rev.add(self)

    def brief_name(self):
        """Return a summarised version of this target's name."""
        # For now, just strip out most of the grist.
        grist, filename = self._grist_and_filename()
        if "!" in grist:
            brief_grist = "{}!{}!...>".format(
                            *grist.split("!", maxsplit=2)[:2])
        else:
            brief_grist = grist
        return brief_grist + filename

    def filename(self):
        """Return the file name for this target (i.e. strip off gristing)."""
        return self._grist_and_filename()[1]

    def grist(self):
        """Return this target's grist."""
        return self._grist_and_filename()[0]

    def _grist_and_filename(self):
        """Split this target's name into a grist and filename."""
        if self.name.startswith("<"):
            grist, filename = self.name.split(">", maxsplit=1)
            return grist + ">", filename
        else:
            return "", self.name

    def set_timestamp(self, timestamp):
        """Set the updated timestamp on this target."""
        self.timestamp = timestamp

    def set_binding(self, binding):
        """Set the file binding for this target"""
        self.binding = binding

    def set_rebuilt(self):
        """Mark this target as having been rebuilt"""
        self.rebuilt = True

    def set_rebuilt_reason(self, reason):
        """Set the rebuild reason of this target"""
        self.rebuild_info.reason = reason

    def set_rebuilt_dep(self, dep):
        """ Mark this target as having been rebuilt due to dependency
            being updated """
        self.rebuilt = True
        self.rebuild_info.reason = "Dependency updated"
        self.rebuild_info.dep = dep


class RebuildInfo:
    """
    Class containing information related to rebuilds
    """
    def __init__(self):
        self.reason = None
        self.dep = None

    def __repr__(self):
        return "{}(reason={}, dep={})".format(
            type(self).__name__, self.reason, self.dep)

