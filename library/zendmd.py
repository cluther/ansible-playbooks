#!/usr/bin/env python
import os


class ZenDMD(object):
    platform = None
    distribution = None

    def __init__(self, module):
        self.module = module
        self.args = self.module.params

        self.creates = self.args["creates"]
        self.code = self.args["code"].strip()
        self.state = self.args["state"].strip()

        self.serviced_cmd = self.module.get_bin_path("serviced", required=True)

        if self.creates and os.path.isfile(self.creates):
            self.changed = False
        else:
            self.changed = True
            if self.state == "run":
                self.run()

            with open(self.creates, "a"):
                os.utime(self.creates, None)

    def run(self):
        tmpfile = "/z/ansible.zendmd"

        try:
            with open(tmpfile, "w") as f:
                f.write(self.code)

            self.module.run_command([
                self.serviced_cmd,
                "service", "shell", "--mount=/z,/z", "zope",
                "su", "-l", "zenoss", "-c",
                "zendmd --script %s" % tmpfile])
        finally:
            os.remove(tmpfile)


def main():
    module = AnsibleModule(
        argument_spec={
            "creates": {"default": None},
            "code": {"required": True},
            "state": {"default": "present", "choices": ["run"]},
        })

    result = ZenDMD(module)

    module.exit_json(
        creates=result.creates,
        code=result.code,
        state=result.state,
        changed=result.changed,
        )


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
