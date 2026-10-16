# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


from importlib import import_module
from knack.help_files import helps
from knack.deprecation import Deprecated

import sys
import os

try:
    from ruamel.yaml import YAML

    yaml = YAML()
    yaml.width = 1000  # prevents wrapping
    yaml.allow_duplicate_keys = True
except ImportError as e:
    msg = "{}\npip install ruamel.Yaml to use this script.".format(e)
    exit(msg)

loaded_helps = {}

FRONT_MATTER_PARTIAL = ""
HEADER_PARTIAL = ""
FOOTER_PARTIAL = ""
# landing page
LANDING = [
    "# Arc Data",
    "Commands for using Azure Arc-enabled data services." "## arcdata",
    "|     |     |",
    "| --- | --- |",
    "[az arcdata dc](reference-az-arcdata-dc.md) | Create, delete, and manage data controllers.",
    "[az arcdata resource-kind](reference-az-arcdata-resource-kind.md) | Resource-kind commands to define and template custom resources on your cluster.",
    "[az arcdata ad-connector](reference-az-arcdata-ad-connector.md) | Manage Active Directory authentication for Azure Arc data services.",
    "## sql mi-arc",
    "|     |     |",
    "| --- | --- |",
    "[az sql mi-arc](reference-az-sql-mi-arc.md) | Manage Azure Arc-enabled SQL managed instances.",
    "## sql midb-arc",
    "|     |     |",
    "| --- | --- |",
    "[az sql midb-arc](reference-az-sql-midb-arc.md) | Manage databases for Azure Arc-enabled SQL managed instances.",
    "## sql instance-failover-group-arc",
    "|     |     |",
    "| --- | --- |",
    "[az sql instance-failover-group-arc](reference-az-sql-instance-failover-group-arc.md) | Create or Delete a Failover Group.",
    "## postgres server-arc",
    "|     |     |",
    "| --- | --- |",
    "[az postgres server-arc](reference-postgres-arc-server.md) | Manage Azure Arc enabled PostgreSQL servers.",
]


class ReferenceDict(object):
    def __init__(self, target_mod):
        self._target_mod = target_mod

    def build(self):
        def merge_arguments(mod_name, content):
            for item in content:
                if "command" in item:
                    command = item["command"]
                    arg = self._build_argument(mod_name, command["name"])
                    if arg:
                        item["command"]["arguments"] = arg
                else:
                    group = item["group"]
                    if "content" in group:
                        merge_arguments(mod_name, group["content"])

        result = self._build_help()
        merge_arguments(self._target_mod.split(".")[-1], result["content"])

        return result

    def _build_help(self):
        try:
            help_mod = import_module("{}.help".format(self._target_mod))
        except ModuleNotFoundError as e:
            return None

        # the modules keys are keys added to helps object from fresh import....
        help_dict = help_mod.helps
        result = ReferenceDict._get_new_yaml_dict(help_dict)

        # clear modules help from knack.helps, store help.py info
        for key, value in help_dict.items():
            loaded_helps[key] = value
        helps.clear()

        return result

    def _build_argument(self, group, command):
        try:
            arg_mod = import_module(self._target_mod)
            cli_mod = import_module("azdata.cli.core")
        except ModuleNotFoundError as e:
            return None

        # -- arguments --
        cli = cli_mod.cli()
        cli.invocation = cli.invocation_cls(
            cli_ctx=cli,
            parser_cls=cli.parser_cls,
            commands_loader_cls=cli.commands_loader_cls,
            help_cls=cli.help_cls,
            initial_data=None,
        )
        cli.invocation.data = {"command_string": command}

        args = ()
        loader = arg_mod.COMMAND_LOADER_CLS(*args, **{"cli_ctx": cli})
        group = loader.load_command_table([group])

        if command not in group:
            return None

        command_type = group[command]

        # -- arguments --
        command_table = loader.command_table
        loader.command_name = command
        command_table[command].load_arguments()
        loader.load_arguments(command)

        # -- For every argument include argument help text --
        args = []
        for arg in command_type.arguments:
            reg = loader.argument_registry
            a = reg.arguments[command][arg].settings
            value = command_type.arguments[arg]

            value.type.settings["options_list"] = a["options_list"]
            value.type.settings["help"] = a["help"]
            a = value.type.settings
            args.append(a)

        return args

    @staticmethod
    def _get_new_yaml_dict(help_dict):
        def _convert_summaries(old_dict, new_dict):
            if "short-summary" in old_dict:
                new_dict["summary"] = old_dict["short-summary"]
            if "long-summary" in old_dict:
                new_dict["description"] = old_dict["long-summary"]

        result = dict(version=1, content=[])
        content = result["content"]

        for command_or_group, yaml_text in help_dict.items():
            help_dict = yaml.load(yaml_text)

            type = help_dict["type"]

            elem = {type: dict(name=command_or_group)}
            elem_content = elem[type]

            _convert_summaries(old_dict=help_dict, new_dict=elem_content)

            if "parameters" in help_dict:
                parameters = []
                for param in help_dict["parameters"]:
                    new_param = dict()
                    if "name" in param:
                        options = param["name"].split()
                        new_param["name"] = max(options, key=lambda x: len(x))
                    _convert_summaries(old_dict=param, new_dict=new_param)

                    if "populator-commands" in param:
                        new_param["value-sources"] = []
                        for item in param["populator-commands"]:
                            new_param["value-sources"].append(
                                {"link": {"command": item}}
                            )
                    parameters.append(new_param)
                elem_content["arguments"] = parameters

            if "examples" in help_dict:
                elem_examples = []
                for ex in help_dict["examples"]:
                    new_ex = dict()
                    if "name" in ex:
                        new_ex["summary"] = ex["name"]
                    if "text" in ex:
                        new_ex["command"] = ex["text"]
                    if "min_profile" in ex:
                        new_ex["min_profile"] = ex["min_profile"]
                    if "max_profile" in ex:
                        new_ex["max_profile"] = ex["max_profile"]
                    elem_examples.append(new_ex)
                elem_content["examples"] = elem_examples

            content.append(elem)

        return result


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class RecursionDocument(object):
    def __init__(self, references, group):
        self._references = references
        self._group = group

    def to_markdown(self, dest):
        """

        :param dest: The file output destination location.
        """

        def sanitize_options_list(arg):
            sanitized = []
            deprecated = ""
            for a in list(arg["options_list"]):
                # -- Add more skip filtering here --
                if not isinstance(a, Deprecated):
                    sanitized.append(a)
            return "{}{}".format(" ".join(list(sanitized)), deprecated)

        group = self._group
        group_title = ("{} {}".format(BRAND, group if group else "")).rstrip()
        print(group_title)
        index = len(group.split(" ")) if group else 0
        header = [
            FRONT_MATTER_PARTIAL.format(group=group_title),
            "# {title}".format(title=group_title),
            "Reference",
            # HEADER_PARTIAL.format(brand=BRAND),
            "## Commands",
        ]
        line = []
        toc = ["|     |     |", "| --- | --- |"]
        group_summary = None
        for items in self._references:
            for item in items:
                if "group" in item:
                    command = item["group"]
                    if index != 0 and not command["name"].startswith(group):
                        continue

                    if len(group.split(" ")) == 2 and group_summary is None:
                        group_summary = item["group"]["summary"]

                    header[3] = item["group"]["summary"]

                    # -- command table --
                    r = 1 if index == 0 else index + 1
                    value = command["name"].split(" ")[0:r]
                    if index == 0:
                        if len(command["name"].split(" ")[:-1]) == index:
                            if value and value[0]:
                                row = "|[{} {}](reference-{}-{}.md) | {} |".format(
                                    BRAND,
                                    " ".join(value),
                                    BRAND,
                                    "-".join(value),
                                    command["summary"],
                                )
                                toc.append(row)
                    else:
                        sub_group = index + 1 == len(command["name"].split(" "))
                        if " ".join(value) != group and sub_group:
                            row = "[{} {}](reference-{}-{}.md) | {}".format(
                                BRAND,
                                " ".join(value),
                                BRAND,
                                "-".join(value),
                                command["summary"],
                            )
                            toc.append(row)

                else:  # command details
                    command = item["command"]
                    if index != 0 and not command["name"].startswith(group):
                        continue

                    if len(command["name"].split(" ")) == index + 1:
                        r = 1 if index == 0 else index + 1
                        value = command["name"].split(" ")[0:r]
                        command_section = "{} {}".format(BRAND, " ".join(value))

                        row = "[{command}](#{link}) | {summary}".format(
                            command=command_section,
                            link=BRAND + "-" + "-".join(value),
                            summary=command["summary"],
                        )

                        toc.append(row)

                        # ------------------------------------------------------

                        command_h2 = "## {}".format(command_section)
                        line.append(command_h2)

                        # ------------------------------------------------------

                        if "description" in command:
                            desc = command["description"]
                        else:
                            desc = command["summary"]

                        line.append(desc)

                        # ------------------------------------------------------

                        def to_markdown_args(args):
                            out = []
                            args = args if args else []
                            for arg in args:
                                opts = sanitize_options_list(arg)
                                if not arg.get("required"):
                                    opts = "[{}]".format(opts)
                                out.append(opts)

                            if not out:
                                return ""

                            first = out[0]
                            out = out[1:]
                            space = ""
                            padding = (
                                "".join(
                                    [
                                        space + " "
                                        for i in range(len(command_section))
                                    ]
                                )
                                + " "
                            )
                            return (
                                first
                                + " \n"
                                + padding
                                + "  \n{}\n".format(padding).join(out)
                            )

                        if "arguments" not in command:
                            command["arguments"] = []

                        usage = "```bash\n{} {}".format(
                            command_section,
                            to_markdown_args(command["arguments"]),
                        )

                        line.append(usage)
                        line.append("```")

                        # ------------------------------------------------------

                        if "examples" in command:
                            example_h3 = "### Examples"
                            line.append(example_h3)

                            for ex in command["examples"]:
                                line.append(ex["summary"])
                                line.append(
                                    "```bash\n{}```".format(
                                        ex["command"].replace("'", '"')
                                    )
                                )

                        has_required = False

                        for arg in command["arguments"]:
                            if arg.get("required"):
                                has_required = True
                                break

                        if has_required:
                            required_parameters_h3 = "### Required Parameters"
                            line.append(required_parameters_h3)

                            for arg in command["arguments"]:
                                opts = sanitize_options_list(arg)
                                if arg.get("required"):
                                    line.append("#### `{}`".format(opts))
                                    line.append(arg.get("help", ""))
                                    if arg.get("default"):
                                        line.append(
                                            "`{}`".format(arg["default"])
                                        )

                        has_optional = False
                        for arg in command["arguments"]:
                            if not arg.get("required"):
                                has_optional = True
                                break

                        if has_optional:
                            optional_parameters_h3 = "### Optional Parameters"
                            line.append(optional_parameters_h3)

                            for arg in command["arguments"]:
                                opts = sanitize_options_list(arg)
                                if not arg.get("required"):
                                    line.append("#### `{}`".format(opts))
                                    line.append(arg.get("help", ""))
                                    if arg.get("default"):
                                        line.append(
                                            "`{}`".format(arg["default"])
                                        )

                        global_arguments_h3 = "### Global Arguments"
                        line.append(global_arguments_h3)
                        line.append("#### `--debug`")
                        line.append(
                            "Increase logging verbosity to show all "
                            "debug logs."
                        )
                        line.append("#### `--help -h`")
                        line.append("Show this help message and exit.")
                        line.append("#### `--output -o`")
                        line.append(
                            "Output format.  Allowed values: json, "
                            "jsonc, table, tsv.  Default: json."
                        )
                        line.append("#### `--query -q`")
                        line.append(
                            "JMESPath query string. See "
                            "[http://jmespath.org/](http://jmespath."
                            "org/]) for more information and examples."
                        )
                        line.append("#### `--verbose`")
                        line.append(
                            "Increase logging verbosity. Use --debug "
                            "for full debug logs."
                        )

        depth = len(group.split(" "))
        if depth == 2 and group_summary:
            header[3] = group_summary

        content = toc + line
        content = header + content
        filename = BRAND + "-" + "-".join(group.split(" ")) if group else BRAND

        file_path = os.path.join(dest, "reference-{}.md".format(filename))

        if depth == 1:
            content = LANDING
            file_path = os.path.join(dest, "arcdata-landing.md")

        with open(file_path, "w") as f:
            content_clean = []
            for c in content:
                if c is not None:
                    content_clean.append(c)
                else:
                    pass

            f.write("\n".join(content_clean))
            f.write("\n")
            # f.write(FOOTER_PARTIAL.format(brand=BRAND))

        print("---------------------------------------------------------------")


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This script requires Python 3")

    BRAND = "az"
    mods = [
        "azext_arcdata.ad_connector",
        "azext_arcdata.dc",
        "azext_arcdata.sqlmi",
        "azext_arcdata.postgres",
        "azext_arcdata.sqlmidb",
    ]
    dest = "output"
    reference_dicts = []

    # -- build reference mapping for each command module --
    for mod in mods:
        result = ReferenceDict(mod).build()
        reference_dicts.append(result["content"])

    # -- generate the markdown document for each reference mapping --
    for items in reference_dicts:
        for item in items:
            if "group" in item:
                group = item["group"]["name"]
                RecursionDocument(reference_dicts, group).to_markdown(dest)
