import re

# Extend CommandPlugin to model via SSH.
from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin


# Class name must match filename. (i.e. iptables.py contains iptables class)
class iptables(CommandPlugin):

    # Relationship name to model. See zenpack.yaml class_relationships.
    relname = "iptablesChains"

    # Type of objects to create. See zenpack.yaml classes.
    modname = "ZenPacks.training.IPTables4.Chain"

    # Command to run on monitored device.
    command = "/sbin/iptables -nvxL"

    def process(self, device, results, log):
        log.info(
            "Modeler %s processing data for device %s",
            self.name(), device.id)

        # Create empty RelationshipMap for iptablesChains relationship.
        rm = self.relMap()

        # Parse results. Append ObjectMap to rm for each chain.
        for line in results.splitlines():
            match = re.match(
                r'^Chain (?P<chain>\S+) \(policy (?P<policy>\S+) .*',
                line)

            if match:
                chain = match.group("chain")
                rm.append(self.objectMap({
                    "id": self.prepId(chain),
                    "title": chain,
                    "policy": match.group("policy"),
                    }))

        # Return filled RelationshipMap.
        return rm
