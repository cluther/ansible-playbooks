#!/usr/bin/env python
import json
import re


class ServicedService(object):
    platform = None
    distribution = None

    def __init__(self, module):
        self.module = module
        self.args = self.module.params

        self.name = self.args["name"].strip()
        self.state = self.args["state"].strip()
        self.launch = self.args["launch"]
        self.auto_launch = self.args["auto_launch"]

        self.serviced_cmd = self.module.get_bin_path("serviced", required=True)

        self.changed = False

        self.common()
        if self.state == "started":
            self.started()
        elif self.state == "stopped":
            self.stopped()

    def common(self):
        _, out, _ = self.module.run_command(
            "%s service list %s -v" % (self.serviced_cmd, self.name))

        try:
            self.service = json.loads(out)
        except Exception:
            self.module.fail_json(msg="no %s service found" % self.name)

        self.set_launch()

    def set_launch(self):
        if self.service.get("Launch") != self.launch:
            self.changed = True

            self.service["Launch"] = self.launch

            fd, path = tempfile.mkstemp()
            try:
                with os.fdopen(fd, 'w') as f:
                    json.dump(self.service, f)

                x, y, z = self.module.run_command(
                    "%s service edit %s" % (
                        self.serviced_cmd,
                        self.name),
                    data=json.dumps(self.service),
                    use_unsafe_shell=True)
            finally:
                os.remove(path)

    def started(self):
        if self.get_status() != "Running":
            self.changed = True

            self.module.run_command(
                "%s service start %s%s" % (
                    self.serviced_cmd,
                    self.name,
                    " --auto-launch" if self.auto_launch else ""))

    def stopped(self):
        if self.get_status() != "Stopped":
            self.changed = True

            self.module.run_command(
                "%s service stop %s" % (
                    self.serviced_cmd,
                    self.name))

    def get_status(self):
        _, out, _ = self.module.run_command(
            "%s service status %s" % (self.serviced_cmd, self.name))

        return re.split(r'[\s\t]+', out.splitlines()[-1].strip())[2]


def main():
    module = AnsibleModule(
        argument_spec={
            "name": {"required": True},
            "state": {"default": "started", "choices": ["started", "stopped"]},
            "launch": {"default": "auto", "choices": ["auto", "manual"]},
            "auto_launch": {"default": True, "choices": [True, False], "type": "bool"},
        })

    result = ServicedService(module)

    module.exit_json(
        name=result.name,
        state=result.state,
        launch=result.launch,
        auto_launch=result.auto_launch,
        changed=result.changed,
        )


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
