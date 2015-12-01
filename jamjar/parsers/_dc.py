#------------------------------------------------------------------------------
# _dc.py
#
# Parser for the jam 'c' debug flag output - which contains the names of files
# that cause rebuilds - ie new sources, missing targets
#
# November 2015, Zoe Kelly
#------------------------------------------------------------------------------

"""jam -dc output parser"""

__all__ = (
    "DCParser",
)


from ._base import BaseParser


class DCParser(BaseParser):
    def parse_logfile(self, filename):
        """
        Function which will read log files with '-dc' debug output.

        Currently can read:
        Rebuilding x: dependency y was updated
        Rebuilding x: it doesn't exist
        """

        debug_flag=False

        with open(filename) as f:
            for line in f:
                words = line.split()

                if len(words) >= 6 and words[0] == "Rebuilding" and words[2] == "dependency":
                    x = words[1].split('\"')[1]
                    y = words[3].split('\"')[1]
                    if debug_flag == True:
                        print("rebuilt {} dependency {} updated".format(x, y))

                    # Add to database
                    x_target = self.db.get_target(x)
                    y_target = self.db.get_target(y)

                    # Check that y is in list of dependencies of x, update if not
                    x_target.add_dependency(y_target)

                    # Set rebuilt flag and reason
                    if (words[4] + words[5]) == "wasupdated":
                        x_target.set_rebuilt_dep(y_target)

                    if debug_flag == True:
                        print(x_target.rebuild_info)

                elif (len(words) >=5 and words[0] == "Rebuilding" and
                      (words[2] + words[3] + words[4]) == "itdoesn'texist"):
                    x = words[1].split('\"')[1]

                    # Add to database
                    x_target = self.db.get_target(x)

                    # Set rebuilt flag and reason
                    x_target.set_rebuilt_exist()

                    if debug_flag == True:
                        print(x_target.rebuild_info)

                elif (len(words) >=5 and words[0] == "Rebuilding" and
                          (words[2] + words[3] + words[4]) == "isolderthan"):
                    x = words[1].split('\"')[1]
                    y = words[5].split('\"')[1]
                    if debug_flag == True:
                        print("rebuilt {} is older than dependency {}".format(x, y))

                    # Add to database
                    x_target = self.db.get_target(x)
                    y_target = self.db.get_target(y)

                    # Set rebuilt flag and reason
                    x_target.set_rebuilt_dep(y_target)

                    if debug_flag == True:
                        print(x_target.rebuild_info)

