#!/usr/bin/env python
import json


class ServicedTemplate(object):
    platform = None
    distribution = None

    def __init__(self, module):
        self.module = module
        self.args = self.module.params

        self.name = self.args["name"].strip()
        self.pool = self.args["pool"].strip()
        self.deployment = self.args["deployment"].strip()
        self.state = self.args["state"].strip()

        self.serviced_cmd = self.module.get_bin_path("serviced", required=True)

        self.changed = False

        if self.state == "deployed":
            self.deployed()

    def deployed(self):
        # Check if template has already been deployed.
        _, out, _ = self.module.run_command(
            "%s service list -v" % self.serviced_cmd)

        try:
            services = json.loads(out)
        except Exception:
            # No services are deployed.
            pass
        else:
            for service in services:
                criteria = (
                    service.get("Name") == self.name,
                    service.get("PoolID") == self.pool,
                    service.get("DeploymentID") == self.deployment,
                    )

                if all(criteria):
                    # Template is already deployed.
                    return

        # Find ID of template.
        _, out, _ = self.module.run_command(
            "%s template list -v" % self.serviced_cmd)

        for template in json.loads(out):
            if template.get("Name") == self.name:
                template_id = template.get("ID")
                break
        else:
            self.module.fail_json(msg="no template named %s" % self.name)

        # Deploy template.
        _, out, _ = self.module.run_command(
            "%s template deploy %s %s %s" % (
                self.serviced_cmd, template_id, self.pool, self.deployment))


def main():
    module = AnsibleModule(
        argument_spec={
            "name": {"required": True},
            "pool": {"default": "default"},
            "deployment": {"default": "default"},
            "state": {"default": "deployed", "choices": ["deployed"]},
        })

    result = ServicedTemplate(module)

    module.exit_json(
        name=result.name,
        pool=result.pool,
        deployment=result.deployment,
        state=result.state,
        changed=result.changed,
        )


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
