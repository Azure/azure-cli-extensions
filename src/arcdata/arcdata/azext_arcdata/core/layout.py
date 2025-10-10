# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from six import add_metaclass
from abc import ABCMeta, abstractmethod
from tabulate import tabulate
from collections import OrderedDict
import string
import os

__all__ = ["BoxLayout"]


@add_metaclass(ABCMeta)
class BaseLayout(object):
    def __init__(self):
        pass

    @abstractmethod
    def render(self):
        pass


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class BoxLayout(BaseLayout):
    def __init__(self, data, config=None, bdc_config=False):
        """
        BoxLayout stacks its components on top of each other. You might think of
        it as a version of FlowLayout in ascii format.

        :param data: Hierarchical `dict` of structured well defined data.
        :param config: (optional) configuration `dict` used to provide simple
                       header layout customization and the ability to highlight
                       specific string tokens in the outout. This can takes the
                       following format:
                       ```
                       {
                          'headers': {
                             'left': {'label': '', 'id': 'state'},
                             'right': {
                                'label': 'Health Status: ',
                                'id': 'healthStatus'
                             }
                          },
                         'identifiers': [
                            {
                               'id': 'healthStatus',
                               'name': 'healthy',
                               'style': 'green'
                            },
                            {
                               'id': 'healthStatus',
                               'name': 'unhealthy',
                               'style': 'red',
                               'undesirable': True
                            }
                         ]
                       }
                       ```
        :param bdc_config: Bool, indicating a specialized box layout for the
        BDC config instead of status.
        """
        super(BoxLayout, self).__init__()
        self._bdc_config = bdc_config
        self._data = data
        self._rendered_data = OrderedDict()
        self._config = (
            config
            if config
            else {"headers": {"right": {}, "left": {}}, "identifiers": []}
        )

    @property
    def rendered_data(self):
        """
        Gets the hierarchical data representation used to render the layout as
        an `OrderedDict`. If `render` has not been invoked, an empty `dict` is
        returned.
        """
        return self._rendered_data

    def has_children(self):
        for key, value in self._data.items():
            if isinstance(value, list) and len(value) > 0:
                return True
        return False

    def render(self):
        if not self.has_children():
            import json

            return "{}\n".format(json.dumps(self._data, indent=4))

        headers = self._config["headers"]
        identifiers = self._config["identifiers"]

        for key, value in self._stack_boxes().items():
            depth = value["depth"]
            if not value["parent"]:
                br()
                left = value["name"].capitalize()
                if "state" in value["identifiers"]:
                    left = left + ":" + value["identifiers"]["state"]
                right = headers["right"]["label"] + value["identifiers"].get(
                    headers["right"].get("id"), ""
                )
                header(
                    title={"left": left, "right": right},
                    identifiers=identifiers,
                )
            else:
                left = value["name"].capitalize()
                right = ""
                if "identifiers" in value:
                    if left != value["parent"].capitalize():
                        left = left + " " + value["parent"].capitalize()
                    if "state" in value["identifiers"]:
                        left = left + ":" + value["identifiers"]["state"]
                    right = headers["right"]["label"] + value[
                        "identifiers"
                    ].get(headers["right"].get("id"), "")

                if not self._bdc_config or (
                    ("serviceName" not in value["columns"])
                    and ("resourceName" not in value["columns"])
                    and ("instanceName" not in value["columns"])
                ):
                    Box(
                        {
                            "depth": depth,
                            "header": {"left": left, "right": right},
                            "content": {
                                "subject": value["columns"],
                                "body": value["rows"],
                            },
                            "identifiers": identifiers,
                        }
                    ).render()
                    br()
                # Special case for listing the service header when it has no settings
                # TODO: revisit logic here and remove special case
                elif len(left.split()) > 1 and "settings" not in left.lower():
                    Box(
                        {
                            "depth": depth,
                            "header": {"left": left, "right": right},
                            "content": {"subject": [], "body": []},
                            "identifiers": identifiers,
                        }
                    ).render()
                    br()
        return ""

    def _stack_boxes(self):
        def stack(data, boxes, parent="", name="", trail="", identifiers=None):
            empty_slot = "-"
            for key, value in data.items():
                # assume name is first XYXName
                if isinstance(key, str) and "Name" in key:
                    name = value

                if not parent and not trail:
                    trail = name
                    boxes[trail] = OrderedDict(
                        [
                            ("name", name),
                            ("parent", parent),
                            ("identifiers", OrderedDict()),
                            ("depth", len(trail.split(".")) - 1),
                            ("columns", list(data.keys())[:-1]),
                            ("rows", [[]]),
                        ]
                    )
                if isinstance(value, dict):
                    # lookahead for list if no list, stop
                    contains_list = False
                    rows = []
                    for d_k, d_v in value.items():
                        rows.append([d_k, d_v if d_v else empty_slot])
                        if isinstance(d_v, list):
                            contains_list = True
                    if contains_list:
                        stack(value, boxes, parent, name, trail, identifiers)
                    else:
                        # -- generic box structure --
                        t = trail + "." + key
                        boxes[t] = OrderedDict(
                            [
                                ("name", key),
                                ("parent", parent),
                                ("depth", len(t.split(".")) - 1),
                                ("columns", ["name", "url"]),
                                ("rows", rows),
                            ]
                        )

                elif isinstance(value, list):
                    new_empty_box = False
                    for box_item in value:
                        if not new_empty_box:
                            new_empty_box = True

                            trail = (
                                name + ":" + trail + "." + key
                                if parent
                                else name + ":" + key
                            )

                            # -- generic box structure --
                            boxes[trail] = OrderedDict(
                                [
                                    ("name", name if parent else key),
                                    ("parent", parent if parent else key),
                                    ("identifiers", OrderedDict()),
                                    ("depth", len(trail.split(".")) - 1),
                                    ("columns", list(box_item.keys())[:-1]),
                                    ("rows", []),
                                ]
                            )
                            parent = key

                        # -- seed new empty row slot to row context of box --
                        box = boxes[trail]
                        rows = box["rows"]
                        rows.append([])
                        box["rows"] = rows
                        boxes[trail] = box
                        stack(box_item, boxes, parent, name, trail, identifiers)
                else:
                    # -- add column value to current row context of box --
                    if trail in boxes:
                        box = boxes[trail]

                        # To remain generic use use identifier keys to stash any
                        # context values by the identifying key(s)
                        if identifiers:
                            for identify in identifiers:
                                if identify["id"] == key:
                                    content = box["identifiers"]

                                    # if `undesirable` is set then the entire
                                    # list is tainted and parent identifiers
                                    # should be notified in order to style
                                    # correctly. For example, assume a calling
                                    # client had a config with the following:
                                    #
                                    # ```
                                    # 'identifiers': [
                                    #    {  'id': 'healthStatus',
                                    #       'name': 'healthy',
                                    #       'style': 'green'
                                    #    },
                                    #    {  'id': 'healthStatus',
                                    #       'name': 'unhealthy',
                                    #       'style': 'red',
                                    #       'undesirable': True
                                    #    }
                                    # }
                                    # ```
                                    # Since the identifier name `unhealthy` was
                                    # configured with `undesirable=True` and the
                                    # value 'unhealthy' was found then the
                                    # entire set is taineted and should be
                                    # styled with the color `red`.
                                    #
                                    # @NOTE: This should be simplified
                                    previous = content.get(key, "")
                                    keep_previous = False
                                    for i in identifiers:
                                        if " " + i[
                                            "name"
                                        ] + " " == previous and i.get(
                                            "undesirable"
                                        ):
                                            keep_previous = True
                                    if not keep_previous:
                                        content[key] = " " + value + " "
                                        box["identifiers"] = content
                                    break

                        if key in box["columns"]:
                            rows = box["rows"]
                            # current row context is the last row
                            last_row = rows[-1]

                            # add column value to current row context
                            last_row.append(
                                value if value is not None else empty_slot
                            )
                            # persist row changes back to the current context
                            rows[-1] = last_row
                            box["rows"] = rows
                            boxes[trail] = box

        stacked_boxes = OrderedDict()
        stack(
            self._data, stacked_boxes, identifiers=self._config["identifiers"]
        )

        self._rendered_data = stacked_boxes

        return self._rendered_data

    def __repr__(self):
        return self.render()


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class Box(object):
    def __init__(self, data):
        self._data = data
        self._identifiers = (
            data.get("identifiers", []) if "identifiers" in data else []
        )

    def render(self):
        data = self._data
        identifiers = self._identifiers

        # -- Render header --
        header(
            title=data["header"],
            char="-",
            depth=data["depth"],
            identifiers=identifiers,
        )

        # -- Render table content --
        content = data["content"]
        columns = [string.capwords(s) + "\n" for s in content["subject"]]

        rows = content["body"]
        for row in tabulate(rows, columns, "plain").split("\n"):
            badge(row, depth=data["depth"], end="\n", identifiers=identifiers)


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


def print_formatted_text(text, end="\n"):
    from prompt_toolkit import print_formatted_text as pft

    try:
        pft(text, end=end)
    except Exception:
        print(text, end=end)


def br():
    print("\n")


def indention(depth):
    margin = 3
    offset = margin * depth
    return 1 if offset <= margin else offset


def badge(text, depth=0, end="", identifiers=None):
    def background(label, color):
        from prompt_toolkit import print_formatted_text as pft, ANSI

        try:
            style = {"green": 102, "red": 101}[color]
            pft(
                ANSI(
                    "\x1b[97;{style}m{label}".format(style=style, label=label)
                ),
                end="",
            )
        except Exception:
            # shim fall back for cygwin/git-bash/ect...
            from colorama import init, Back

            init(strip=False)
            style = {"green": Back.GREEN, "red": Back.RED}[color]
            print("{}{}".format(style, label) + Back.RESET, end="")

    margin_left = "".ljust(indention(depth))

    if identifiers:
        for identifier in identifiers:
            tokens = text.split(" " + identifier["name"] + " ")
            if len(tokens) == 2:
                print_formatted_text(margin_left + tokens[0] + " ", end="")
                background(identifier["name"], identifier["style"])
                print_formatted_text(" " + tokens[1], end=end)
                return

    print_formatted_text(margin_left + text, end=end)


def div(char="-", depth=0):
    margin_left = indention(depth)
    margin_right = 1
    width = terminal_width() - margin_right

    length = width - margin_left
    divider = ["".ljust(margin_left), (char * length)[:length]]
    print_formatted_text("")  # newline
    print_formatted_text("".join(divider))


def header(title, char="=", depth=0, identifiers=None):
    title_left = title.get("left", "")
    title_right = title.get("right", "")

    # Render Title Left
    margin_left = indention(depth)
    left = "".join(["".ljust(margin_left), title_left])
    print_formatted_text(left, end="")

    # Render Title Right
    if title_right:
        margin_right = 1
        length = terminal_width() - margin_right - len(left) - len(title_right)
        right = ["".ljust(length - (0 if margin_left <= 1 else 5)), title_right]
        badge("".join(right), depth=depth, end="", identifiers=identifiers)

    div(char=char, depth=depth)


def terminal_width():
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 79  # can not calculate terminal width, default to 80 chars

    return width
