import os

import logging

global log
log = logging.getLogger(__name__)


def checktool(tool, required_version):
    # Get the tool path to check for the existence of the tool.
    tool_path = os.popen(f"which {tool}").read().replace('\n', '')
    tool_status = 0
    if os.path.exists(tool_path):
        # Obtain the current tool version.
        try:
            version_string = os.popen(f"{tool} -v").read().split()
        except ValueError:
            version_string = os.popen(f"{tool} -v").read().split()
        try:
            current_version = version_string[version_string.index("Version") + 1]
        except ValueError:
            current_version = version_string[version_string.index("version") + 1]

        # Check the required versions and the current version
        from distutils.version import LooseVersion, StrictVersion
        if LooseVersion(current_version) >= LooseVersion(required_version):
            tool_status = 1
        else:
            tool_status = 0
    else:
        tool_status = 0

    return tool_status, current_version

    log.info(" Using %s hspice version for the library characterization" % h_version)


def toolenv():
    """
    Checks the environment of the required tools for running the sims.
    """

    import sys
    import platform
    if not sys.version_info > (3, 0):
        print(f"Error: Found {platform.python_version()}, Python 3.0 or greater is required for MemGen")
        sys.exit(1)

    globals_dir = os.path.abspath(__file__)
    verified_tools_file = os.path.join(globals_dir, "configs", "verified_tools.yaml")

    from globals import global_utils
    config_dic = global_utils.yaml_config_parser(verified_tools_file)

    tool_status_list = []
    for tool in config_dic.keys():
        tool_status, current_version = checktool(tool, config_dic[tool])
        log.info(f"{tool}: Required Version {config_dic[tool]} \t Current Version {current_version} \t ")


if __name__ == '__main__':
    toolenv()
