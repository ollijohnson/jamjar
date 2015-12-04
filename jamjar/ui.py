#------------------------------------------------------------------------------
# ui.py - CLI commands module
#
# November 2015, Zoe Kelly
#------------------------------------------------------------------------------

import cmd, sys, io, pydoc

from . import database, query


class _BaseCmd(cmd.Cmd):
    """Base class for command submodes."""
    def __init__(self, paging_on):
        super().__init__()
        self.paging_on = paging_on
        self.out = None
        if paging_on == True:
            self.turn_paging_on()
        else:
            self.turn_paging_off()

    def turn_paging_on(self):
        self.paging_on = True

    def turn_paging_off(self):
        self.paging_on = False
        sys.stdout = sys.__stdout__

    def precmd(self, line):
        self.start_pager()
        return (line)

    def start_pager(self):
        if self.paging_on:
            self.out = io.StringIO()
            sys.stdout = self.out


    def postcmd(self, stop, line):
        self.flush_pager()
        return (stop)

    def flush_pager(self):
       # Reset
        sys.stdout = sys.__stdout__

        if self.paging_on:
            # Page output of this command
            if self.out is not None:
                pydoc.pager(self.out.getvalue())
        self.out = None

    def do_paging_off(self, arg):
        """"Turn paging off"""
        self.turn_paging_off()

    def do_paging_on(self, arg):
        """Turn paging on"""
        self.turn_paging_on()

    def do_EOF(self, arg):
        """Handle EOF (AKA ctrl-d)."""
        print("")
        return self.do_exit(None)

    def do_exit(self, arg):
        """Exit this submode."""
        return True


class UI(_BaseCmd):
    def __init__(self, db, *, paging_on=False):
        super().__init__(paging_on)
        self.file = None
        self.intro = "Welcome to JamJar.  Type help or ? to list commands.\n"
        self.prompt = "(jamjar) "
        self.database = db

    def do_targets(self, target_string):
        """Get information about targets matching a regex."""
        target_list = list(self.database.find_targets(target_string))
        if len(target_list) == 0:
            print("No targets found")
        elif len(target_list) == 1:
            TargetSubmode(target=target_list[0], paging_on=self.paging_on).cmdloop()
        else:
            target = self._target_selection(target_list)
            if target is not None:
                TargetSubmode(target=target,
                              paging_on=self.paging_on).cmdloop()

    def do_rebuilt_targets(self, target_string):
        """Get information about targets that were rebuilt matching a regex."""
        target_list = list(self.database.find_rebuilt_targets(target_string))
        if len(target_list) == 0:
            print("No targets found")
        elif len(target_list) == 1:
            TargetSubmode(target=target_list[0], paging_on=self.paging_on).cmdloop()
        else:
            target = self._target_selection(target_list)
            if target is not None:
                TargetSubmode(target=target,
                              paging_on=self.paging_on).cmdloop()

    def _target_selection(self, targets):
        for idx, target in enumerate(targets):
            print("({}) {}".format(idx , target))
        self.flush_pager()

        target = None
        while True:
            try:
                choice = input("Choose target (range 0:{}): ".format(
                    len(targets) - 1))
            except EOFError:
                print("")
                break
            # Exit target selection on empty input.
            if not choice:
                break
            try:
                target_index = int(choice)
                target = targets[target_index]
            except (ValueError, IndexError):
                pass
            else:
                break
        return target


class TargetSubmode(_BaseCmd):
    def __init__(self, target, *, paging_on):
        super().__init__(paging_on)
        self.target = target
        self.prompt = "({}) ".format(self.target.brief_name())
        file = None

    def do_deps(self, arg):
        """
        Show all direct dependencies, including those arising from includes.
        """
        self._print_targets(query.deps(self.target))

    def do_deps_rebuilt(self, arg):
        """Show direct dependencies that have been rebuilt."""
        self._print_targets(query.deps_rebuilt(self.target))

    def do_dep_chains(self, arg):
        """Show all chains of dependencies below this target."""
        # Yuck.
        kwargs = self._arg_to_kwargs(arg)
        if "max_depth" in kwargs:
            kwargs["max_depth"] = int(kwargs["max_depth"])
        for chain in query.dep_chains(self.target, **kwargs):
            self._print_chain(chain)

    def do_dep_chains_rebuilt(self, arg):
        """Show all chains of dependencies below this target."""
        for chain in query.dep_chains_rebuilt(self.target):
            self._print_chain(chain)

    def do_rebuild_chains(self, arg):
        """Show Jam's view on why this target was rebuilt."""
        for chain in query.rebuild_chains(self.target):
            self._print_chain(chain)

    def do_show(self, arg):
        """Dump all available meta-data for this target."""
        print("name:", self.target.name)
        print("depends on:")
        self._print_targets(self.target.deps)
        print("depended on by:")
        self._print_targets(self.target.deps_rev)
        print("includes:")
        self._print_targets(self.target.incs)
        print("included by:")
        self._print_targets(self.target.incs_rev)
        if self.target.timestamp_chain is not None:
            print("timestamp:", self.target.timestamp_chain[-1].timestamp)
            print("timestamp inherited from:")
            self._print_targets(self.target.timestamp_chain)
        else:
            print("timestamp:", self.target.timestamp)
        print("binding:", self.target.binding)
        print("rebuilt:", self.target.rebuilt)
        if self.target.rebuilt:
            print("    rebuilt reason:", self.target.rebuild_info.reason)
            if self.target.rebuild_info.dep is not None:
                print("    dependency:", self.target.rebuild_info.dep.name)

    def _arg_to_kwargs(self, arg):
        """Parse an input argument consisting of param=value pairs."""
        kwargs = {}
        args = arg.split()
        for arg in args:
            key, value = arg.split("=")
            kwargs[key] = value
        return kwargs

    def _print_chain(self, chain):
        """Print a sequence of targets forming a dependency chain."""
        print(" -> ".join(target.name for target in chain))

    def _print_targets(self, targets):
        """Print a sequence of targets."""
        for target in targets:
            print("    {}".format(target.name))

