#!/usr/bin/env python
import json


class ServicedHost(object):
    platform = None
    distribution = None

    def __init__(self, module):
        self.module = module
        self.args = self.module.params

        self.ip = self.args["ip"].strip()
        self.port = self.args["port"]
        self.pool = self.args["pool"].strip()
        self.state = self.args["state"].strip()

        self.serviced_cmd = self.module.get_bin_path("serviced", required=True)

        self.changed = False

        if self.state == "present":
            self.present()

    def present(self):
        # Check if host is already present.
        _, out, _ = self.module.run_command(
            "%s host list -v" % self.serviced_cmd)

        try:
            hosts = json.loads(out)
        except Exception:
            # No hosts.
            pass
        else:
            for host in hosts:
                criteria = (
                    host.get("IPAddr") == self.ip,
                    host.get("RPCPort") == self.port,
                    host.get("PoolID") == self.pool,
                    )

                if all(criteria):
                    # Host is already added.
                    return

        # Add host.
        _, out, _ = self.module.run_command(
            "%s host add %s:%s %s" % (
                self.serviced_cmd,
                self.ip,
                self.port,
                self.pool))

        self.changed = True


def main():
    module = AnsibleModule(
        argument_spec={
            "ip": {"required": True},
            "port": {"default": 4979},
            "pool": {"default": "default"},
            "state": {"default": "present", "choices": ["present"]},
        })

    result = ServicedHost(module)

    module.exit_json(
        ip=result.ip,
        port=result.port,
        pool=result.pool,
        state=result.state,
        changed=result.changed,
        )


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
