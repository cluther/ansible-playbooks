#!/usr/bin/env python
import json
import time


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

        self.service_id = None
        self.changed = False

        if self.state == "deployed":
            while not self.deployed():
                time.sleep(1)

    def deployed(self):
        service = self.find_service()
        if service:
            return True

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

        service = self.find_service()
        if service:
            self.changed = True
            return True
        else:
            return False

    def find_service(self):
        _, out, _ = self.module.run_command(
            "%s service list -v" % self.serviced_cmd)

        try:
            services = json.loads(out)
        except Exception:
            return
        else:
            for service in services:
                criteria = (
                    service.get("Name") == self.name,
                    service.get("PoolID") == self.pool,
                    service.get("DeploymentID") == self.deployment,
                    )

                if all(criteria):
                    self.service_id = service.get("ID")
                    return service


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
        service_id=result.service_id,
        changed=result.changed,
        )


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
