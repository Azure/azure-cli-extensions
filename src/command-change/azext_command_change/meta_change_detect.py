# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_command_change.util import get_command_tree, ChangeType, extract_cmd_name, extract_subgroup_name, \
    extract_cmd_property
from azext_command_change.meta_change import (CmdAdd, CmdRemove, CmdPropAdd, CmdPropRemove, CmdPropUpdate,
                                               ParaAdd, ParaRemove, ParaPropAdd, ParaPropRemove, ParaPropUpdate,
                                               SubgroupAdd, SubgroupRemove)
from azext_command_change._const import (CMD_PROPERTY_ADD_BREAK_LIST, CMD_PROPERTY_REMOVE_BREAK_LIST,
                                         CMD_PROPERTY_UPDATE_BREAK_LIST, PARA_PROPERTY_REMOVE_BREAK_LIST,
                                         PARA_PROPERTY_ADD_BREAK_LIST, PARA_PROPERTY_UPDATE_BREAK_LIST)
from knack.log import get_logger
logger = get_logger(__name__)


class MetaChangeDetect:

    EXPORTED_META_PROPERTY = ["rule_id", "is_break", "rule_message", "suggest_message", "cmd_name", "subgroup_name"]
    CHECKED_PARA_PROPERTY = ["name", "options", "required", "choices", "id_part", "nargs", "default", "desc",
                             "aaz_type", "type", "aaz_default", "aaz_choices"]

    def __init__(self, deep_diff=None, base_meta=None, diff_meta=None):
        self.deep_diff = {}
        if deep_diff:
            self.deep_diff = deep_diff
        else:
            logger.info("None diffs from cmd meta json")
        assert base_meta["module_name"] == diff_meta["module_name"]
        self.module_name = base_meta["module_name"]
        self.base_meta = base_meta
        self.diff_meta = diff_meta
        self.diff_objs = []
        self.cmd_set_with_parameter_change = set()

    @staticmethod
    def __search_cmd_obj(cmd_name, search_meta):
        command_tree = get_command_tree(cmd_name)
        meta_search = search_meta
        while True:
            if "is_group" not in command_tree:
                break
            if command_tree["is_group"]:
                group_name = command_tree["group_name"]
                meta_search = meta_search["sub_groups"][group_name]
                command_tree = command_tree["sub_info"]
            else:
                cmd_name = command_tree["cmd_name"]
                meta_search = meta_search["commands"][cmd_name]
                break
        return meta_search

    def __log_cmd_with_parameter_change(self, cmd_name):
        self.cmd_set_with_parameter_change.add(cmd_name)

    def __iter_dict_items(self, dict_items, diff_type):
        if diff_type not in [ChangeType.REMOVE, ChangeType.ADD]:
            raise Exception("Unsupported dict item type")

        for dict_key in dict_items:
            has_cmd, cmd_name = extract_cmd_name(dict_key)
            if not has_cmd or not cmd_name:
                has_subgroup, subgroup_name = extract_subgroup_name(dict_key)
                if not has_subgroup or not subgroup_name:
                    continue
                if diff_type == ChangeType.REMOVE:
                    diff_obj = SubgroupRemove(subgroup_name)
                else:
                    diff_obj = SubgroupAdd(subgroup_name)
                self.diff_objs.append(diff_obj)
                continue

            has_cmd_key, cmd_property = extract_cmd_property(dict_key, cmd_name)
            if has_cmd_key:
                if cmd_property == "parameters":
                    self.__log_cmd_with_parameter_change(cmd_name)
                elif diff_type == ChangeType.ADD:
                    if cmd_property in CMD_PROPERTY_ADD_BREAK_LIST:
                        diff_obj = CmdPropAdd(cmd_name, cmd_property, True)
                    else:
                        diff_obj = CmdPropAdd(cmd_name, cmd_property, True)
                    self.diff_objs.append(diff_obj)
                else:
                    if cmd_property in CMD_PROPERTY_REMOVE_BREAK_LIST:
                        diff_obj = CmdPropRemove(cmd_name, cmd_property, True)
                    else:
                        diff_obj = CmdPropRemove(cmd_name, cmd_property, False)
                    self.diff_objs.append(diff_obj)
            else:
                if diff_type == ChangeType.REMOVE:
                    diff_obj = CmdRemove(cmd_name)
                else:
                    diff_obj = CmdAdd(cmd_name)

                self.diff_objs.append(diff_obj)

    def __iter_list_items(self, list_items, diff_type):
        """
        ['parameters'][0]['options'][1]
        ['parameters'][0]['choices'][0]
        ['parameters'][3]
        """
        if diff_type not in [ChangeType.REMOVE, ChangeType.ADD]:
            raise Exception("Unsupported dict item type")

        for key, _ in list_items.items():
            has_cmd, cmd_name = extract_cmd_name(key)
            if not has_cmd or not cmd_name:
                print("extract cmd failed for " + key)
                continue
            has_cmd_key, cmd_property = extract_cmd_property(key, cmd_name)
            if not has_cmd_key:
                continue
            if cmd_property == "parameters":
                self.__log_cmd_with_parameter_change(cmd_name)

    def check_dict_item_remove(self):
        if not self.deep_diff.get("dictionary_item_removed", None):
            return
        dict_item_removed = self.deep_diff["dictionary_item_removed"]
        self.__iter_dict_items(dict_item_removed, ChangeType.REMOVE)

    def check_dict_item_add(self):
        if not self.deep_diff.get("dictionary_item_added", None):
            return
        dict_item_added = self.deep_diff["dictionary_item_added"]
        self.__iter_dict_items(dict_item_added, ChangeType.ADD)

    def check_list_item_remove(self):
        if not self.deep_diff.get("iterable_item_removed", None):
            return

        list_item_remove = self.deep_diff["iterable_item_removed"]
        self.__iter_list_items(list_item_remove, ChangeType.REMOVE)

    def check_list_item_add(self):
        if not self.deep_diff.get("iterable_item_added", None):
            return
        list_item_add = self.deep_diff["iterable_item_added"]
        self.__iter_list_items(list_item_add, ChangeType.ADD)

    def check_value_change(self):
        if not self.deep_diff.get("values_changed", None):
            return
        value_changes = self.deep_diff["values_changed"]
        for key, value_obj in value_changes.items():
            old_value = value_obj["old_value"]
            new_value = value_obj["new_value"]
            has_cmd, cmd_name = extract_cmd_name(key)
            if not has_cmd or not cmd_name:
                print("extract cmd failed for " + key)
                continue

            has_cmd_prop, cmd_property = extract_cmd_property(key, cmd_name)
            if not has_cmd_prop:
                return
            if cmd_property == "parameters":
                self.__log_cmd_with_parameter_change(cmd_name)
            else:
                if cmd_property in CMD_PROPERTY_UPDATE_BREAK_LIST:
                    diff_obj = CmdPropUpdate(cmd_name, cmd_property, True, old_value, new_value)
                else:
                    diff_obj = CmdPropUpdate(cmd_name, cmd_property, False, old_value, new_value)
                self.diff_objs.append(diff_obj)

    @staticmethod
    def __search_para_with_name_and_options(base_para_obj, search_parameters):
        para_name = base_para_obj["name"]
        para_option_set = set(base_para_obj["options"])
        for para_obj in search_parameters:
            name = para_obj["name"]
            option_set = set(para_obj.get("options", []))
            if para_name == name or para_option_set.issubset(option_set):
                # parameter obj which has the same name or new option list contains old option list,
                # is same parameter obj
                # if name is changed and new option list lost element in old option list, then is different
                return para_obj
        return None

    def check_cmd_parameter_diff(self, cmd_name, base_parameters, cmp_parameters):
        """check cmd parameter diff"""
        for base_para_obj in base_parameters:
            base_para_obj["checked"] = True
            cmp_para_obj = self.__search_para_with_name_and_options(base_para_obj, cmp_parameters)
            if cmp_para_obj is None:
                # cmd lost parameter obj, is break
                diff_obj = ParaRemove(cmd_name, base_para_obj["name"], True)
                # add flag to avoid duplicate compare
                self.diff_objs.append(diff_obj)
                continue
            cmp_para_obj["checked"] = True
            for prop in self.CHECKED_PARA_PROPERTY:
                if prop not in base_para_obj and prop not in cmp_para_obj:
                    continue
                if prop in base_para_obj and prop not in cmp_para_obj:
                    # prop dropped in new para obj
                    if prop in PARA_PROPERTY_REMOVE_BREAK_LIST:
                        diff_obj = ParaPropRemove(cmd_name, base_para_obj["name"], prop, True)
                    else:
                        diff_obj = ParaPropRemove(cmd_name, base_para_obj["name"], prop, False)
                    self.diff_objs.append(diff_obj)
                    continue
                if prop not in base_para_obj and prop in cmp_para_obj:
                    # prop added in new para obj
                    if prop in PARA_PROPERTY_ADD_BREAK_LIST:
                        diff_obj = ParaPropAdd(cmd_name, base_para_obj["name"], prop, True)
                    else:
                        diff_obj = ParaPropAdd(cmd_name, base_para_obj["name"], prop, False)
                    self.diff_objs.append(diff_obj)
                    continue
                # prop exists in both new and old para obj, value needs to be checked
                base_val = base_para_obj[prop]
                cmp_val = cmp_para_obj[prop]

                if base_val != cmp_val:
                    if isinstance(base_val, list) and isinstance(cmp_val, list):
                        if set(base_val).issubset(set(cmp_val)):
                            diff_obj = ParaPropUpdate(cmd_name, base_para_obj["name"], prop, False, base_val, cmp_val)
                        else:
                            diff_obj = ParaPropUpdate(cmd_name, base_para_obj["name"], prop, True, base_val, cmp_val)
                    elif prop in PARA_PROPERTY_UPDATE_BREAK_LIST:
                        diff_obj = ParaPropUpdate(cmd_name, base_para_obj["name"], prop, True, base_val, cmp_val)
                    else:
                        diff_obj = ParaPropUpdate(cmd_name, base_para_obj["name"], prop, False, base_val, cmp_val)
                    self.diff_objs.append(diff_obj)

        # check added parameter obj, if obj is required, then is break
        for cmp_para_obj in cmp_parameters:
            if "checked" in cmp_para_obj and cmp_para_obj["checked"]:
                continue
            para_name = cmp_para_obj["name"]
            required = cmp_para_obj.get("required", None)
            if required:
                diff_obj = ParaAdd(cmd_name, para_name, True)
            else:
                diff_obj = ParaAdd(cmd_name, para_name, False)
            self.diff_objs.append(diff_obj)

    def check_cmds_parameter_diff(self):
        """
        deal with command parameter diffs
        """
        for cmd_name in self.cmd_set_with_parameter_change:
            cmd_base = self.__search_cmd_obj(cmd_name, self.base_meta)
            cmd_cmp = self.__search_cmd_obj(cmd_name, self.diff_meta)
            base_parameters = cmd_base.get("parameters", [])
            cmp_parameters = cmd_cmp.get("parameters", [])
            self.check_cmd_parameter_diff(cmd_name, base_parameters, cmp_parameters)

    def check_deep_diffs(self):
        self.check_dict_item_remove()
        self.check_dict_item_add()
        self.check_list_item_remove()
        self.check_list_item_add()
        self.check_value_change()
        self.check_cmds_parameter_diff()

    @staticmethod
    def fill_subgroup_rules(obj, ret_mod, rule):
        command_group_info = ret_mod
        group_name_arr = obj.subgroup_name.split(" ")
        start_level = 1
        while start_level < len(group_name_arr):
            group_name = " ".join(group_name_arr[:start_level])
            if group_name not in command_group_info["sub_groups"]:
                command_group_info["sub_groups"][group_name] = {
                    "name": group_name,
                    "commands": {},
                    "sub_groups": {}
                }
            start_level += 1
            command_group_info = command_group_info["sub_groups"][group_name]
        group_name = obj.subgroup_name
        group_rules = []
        if group_name not in command_group_info["sub_groups"]:
            command_group_info["sub_groups"] = {group_name: group_rules}
        group_rules = command_group_info["sub_groups"][group_name]
        group_rules.append(rule)
        command_group_info["sub_groups"][group_name] = group_rules

    @staticmethod
    def fill_cmd_rules(obj, ret_mod, rule):
        command_tree = get_command_tree(obj.cmd_name)
        command_group_info = ret_mod
        while True:
            if "is_group" not in command_tree:
                break
            if command_tree["is_group"]:
                group_name = command_tree["group_name"]
                if group_name not in command_group_info["sub_groups"]:
                    command_group_info["sub_groups"][group_name] = {
                        "name": group_name,
                        "commands": {},
                        "sub_groups": {}
                    }
                command_tree = command_tree["sub_info"]
                command_group_info = command_group_info["sub_groups"][group_name]
            else:
                cmd_name = command_tree["cmd_name"]
                command_rules = []
                if cmd_name in command_group_info["commands"]:
                    command_rules = command_group_info["commands"][cmd_name]
                command_rules.append(rule)
                command_group_info["commands"][cmd_name] = command_rules
                break

    def export_meta_changes(self, only_break, output_type="text"):
        ret_objs = []
        ret_mod = {
            "module_name": self.module_name,
            "name": "az",
            "commands": {},
            "sub_groups": {}
        }
        for obj in self.diff_objs:
            if only_break and not obj.is_break:
                continue
            ret = {}
            for prop in self.EXPORTED_META_PROPERTY:
                if hasattr(obj, prop):
                    ret[prop] = getattr(obj, prop)
            ret["rule_name"] = obj.__class__.__name__
            if output_type == "dict":
                ret_objs.append(ret)
            elif output_type == "text":
                ret_objs.append(str(obj))
            if output_type != "tree":
                continue
            if not hasattr(obj, "cmd_name") and not hasattr(obj, "subgroup_name"):
                logger.info("unsupported rule ignored")
            elif not hasattr(obj, "cmd_name") and hasattr(obj, "subgroup_name"):
                self.fill_subgroup_rules(obj, ret_mod, ret)
            elif not hasattr(obj, "subgroup_name") and hasattr(obj, "cmd_name"):
                self.fill_cmd_rules(obj, ret_mod, ret)
            else:
                logger.info("unsupported rule ignored")

        return ret_objs if output_type in ["text", "dict"] else ret_mod
