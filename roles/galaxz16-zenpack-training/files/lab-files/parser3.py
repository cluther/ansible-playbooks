import re
from Products.ZenRRD.CommandParser import CommandParser


class iptables(CommandParser):

    def processResults(self, cmd, result):
        """Process command (cmd) data and add to results."""
        values = {}

        # Command output is in cmd.result.output
        for line in cmd.result.output.splitlines():
            match = re.match(
                r'^Chain (?P<chain>\S+) \(policy \S+ '
                r'(?P<packets>\d+) packets, '
                r'(?P<bytes>\d+) bytes\)$',
                line)

            if match:
                for measure in ("packets", "bytes"):
                    values_key = "{}{}".format(match.group("chain"), measure)
                    values[values_key] = int(match.group(measure))

        # Add values to result only for all matching datapoints.
        for point in cmd.points:
            if point.id in values:
                result.values.append((point, values[point.id]))
