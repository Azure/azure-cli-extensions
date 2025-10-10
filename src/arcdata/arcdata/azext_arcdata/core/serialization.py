# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import pydash as _
import re
from typing import List

__all__ = ["Sanitizer"]


class SanitizerRule:
    def __init__(
        self, property_path_pattern="", filter=lambda property_path, value: None
    ):
        self._property_path_pattern = property_path_pattern
        self._filter = filter
        self._regex = re.compile(self._property_path_pattern)

    def is_property_match(self, property_path):
        return self._regex.search(property_path)

    def sanitize_value(self, property_path, value):
        if self.is_property_match(property_path):
            return self._filter(property_path, value)
        else:
            return value


class Sanitizer(object):
    """
    Object sanitizer allowing for properties to be excluded based on
    configurable filters
    """

    def __init__(self, filters: List[SanitizerRule] = [], *args, **kwargs):
        """
        Initializer with additional parameters for managing serialized content

        Keyword Arguments:
            filters list(SanitizerRule) -- array of funcs that are called with
             the property path/value must return true to include in the
             sanitized output, or false to remove.
        """
        super().__init__(*args, **kwargs)
        self._serializedInstances = []
        self._filters = filters

    def sanitize_value(self, property_path, property_value):
        for f in self._filters:
            try:
                return f.sanitize_value(property_path, property_value)
            except Exception:
                raise ValueError(
                    "Unable to sanitize property {0} failed to "
                    "call filter.".format(property_path)
                )

        return property_value

    def _array_sanitizer_aggregator(self, path, value, aggregator):
        aggregator.append(self.sanitize(value, path))
        return aggregator

    def sanitize(self, obj, path=""):
        """
        Sanitizes the given object and returns a new dict with properties that
        are allowed to be serialized.
        """
        if obj is None:
            return None

        if isinstance(obj, list):
            result = _.reduce_(
                obj,
                lambda agg, value: self._array_sanitizer_aggregator(
                    path, value, agg
                ),
                [],
            )
            return result

        obj = _.get(obj, "__dict__", obj)

        if isinstance(obj, dict):
            # if the object is a dict, we need to pass each property to each
            # filter to determine if it should be serialized or not. And return
            # the resulting dictionary
            result = {}
            for key in _.keys(obj):
                result[key] = self.sanitize(obj[key], ".".join([path, key]))

            return result
        else:
            # if the object is not a dict by this point, it is going to be a
            # simple type, so we can just return it.
            return self.sanitize_value(path, obj)

    @staticmethod
    def sanitize_object(obj, filters: List[SanitizerRule] = []):
        """
        Convenience method allowing for an object and filters to be passed in.
        The results will be the sanitized object
        """
        sanitizer = Sanitizer(filters)
        return sanitizer.sanitize(obj)

    @staticmethod
    def replace_if_string(
        text,
        pattern,
        repl,
        ignore_case=False,
        count=0,
        escape=True,
        from_start=False,
        from_end=False,
    ):

        """
        Convenience method Replace occurrences of `pattern` with `repl` in `
        text` without the need to check for str type. Optionally, ignore case
        when replacing. Optionally, set `count` to limit number of replacements.

        Args:
            text (str): String to replace.
            pattern (str): String pattern to find and replace.  (this can be a
            regex pattern)
            repl (str): String to substitute `pattern` with.
            ignore_clase (bool, optional): Whether to ignore case when
            replacing. Defaults to ``False``.
            count (int, optional): Maximum number of occurrences to replace.
                Defaults to ``0`` which replaces all.
            escape (bool, optional): Whether to escape `pattern` when searching.
                This is needed if a literal replacement is desired when pattern
                may contain special regular expression characters. Defaults to
                ``True``.
            from_start (bool, optional): Whether to limit replacement to start
            of string.
            from_end (bool, optional): Whether to limit replacement to end of
                string.

        Returns:
            str: Replaced string.

        Remarks:
            If the value of text is not a string value, the value will be
            returned unmodified.

        Example:

            >>> replace('aabbcc', 'b', 'X')
            'aaXXcc'
            >>> replace('aabbcc', 'B', 'X', ignore_case=True)
            'aaXXcc'
            >>> replace('aabbcc', 'b', 'X', count=1)
            'aaXbcc'
            >>> replace('aabbcc', '[ab]', 'X')
            'aabbcc'
            >>> replace('aabbcc', '[ab]', 'X', escape=False)
            'XXXXcc'
        """
        if isinstance(text, str):
            return _.replace(
                text,
                pattern,
                repl,
                ignore_case,
                count,
                escape,
                from_start,
                from_end,
            )

        return text
