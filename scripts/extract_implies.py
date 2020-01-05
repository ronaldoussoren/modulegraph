#!/usr/bin/env python3
"""
This script looks for ImportModules calls in C extensions
of the stdlib.

The current version has harcoded the location of the source
tries on Ronald's machine, a future version will be able
to rebuild the modulegraph source file that contains
this information.
"""

import os
import pprint
import re

import_re = re.compile(r'PyImport_ImportModule\w+\("(\w+)"\);')


def extract_implies(root):
    modules_dir = os.path.join(root, "Modules")
    for fn in os.listdir(modules_dir):
        if not fn.endswith(".c"):
            continue

        module_name = fn[:-2]
        if module_name.endswith("module"):
            module_name = module_name[:-6]

        with open(os.path.join(modules_dir, fn)) as fp:
            data = fp.read()

        imports = sorted(set(import_re.findall(data)))
        if imports:
            yield module_name, imports


def main():
    for version in ("2.6", "2.7", "3.1"):
        print("====", version)
        pprint.pprint(
            list(
                extract_implies(
                    "/Users/ronald/Projects/python/release%s-maint"
                    % (version.replace(".", ""))
                )
            )
        )


if __name__ == "__main__":
    main()
