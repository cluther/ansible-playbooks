#!/usr/bin/env python
import json
import time


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

        self.host_id = None
        self.changed = False

        if self.state == "present":
            while not self.present():
                time.sleep(1)

    def present(self):
        host = self.find_host()
        if host:
            return True

        # Add host.
        _, out, _ = self.module.run_command(
            "%s host add %s:%s %s" % (
                self.serviced_cmd,
                self.ip,
                self.port,
                self.pool))

        host = self.find_host()
        if host:
            self.changed = True
            return True
        else:
            return False

    def find_host(self):
        _, out, _ = self.module.run_command(
            "%s host list -v" % self.serviced_cmd)

        try:
            hosts = json.loads(out)
        except Exception:
            return
        else:
            for host in hosts:
                criteria = (
                    host.get("IPAddr") == self.ip,
                    host.get("RPCPort") == self.port,
                    host.get("PoolID") == self.pool,
                    )

                if all(criteria):
                    self.host_id = host.get("ID")
                    return host


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
        host_id=result.host_id,
        changed=result.changed,
        )


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
