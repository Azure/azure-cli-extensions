import json
import pprint
import uuid
import yaml
from json import scanner
from json.decoder import py_scanstring

from functools import wraps
import pydash as _

try:
    from _json import scanstring as c_scanstring
except ImportError:
    c_scanstring = None


def get_full_type_name(obj):
    if not isinstance(obj, type):
        obj = type(obj)

    return obj.__module__ + "." + obj.__name__


def set_object_ref(obj):
    if hasattr(obj, "__ref__"):
        return obj.__ref__

    obj.__ref__ = _.head(str(uuid.uuid1()).split("-"))
    return obj.__ref__


def resolve_type_by_full_name(typeName):
    try:
        typeArr = typeName.split(".")
        moduleName = ".".join(typeArr[:-1])
        className = typeArr[-1]
        exec("from {0} import {1}".format(moduleName, className))
        return eval(className)
    except Exception as ex:
        raise Exception(
            "Unable to load class {0} check the class name and try again. Error: {1}".format(
                typeName, str(ex)
            )
        )


def get_decorator(obj, key, decorator, default):
    attr = getattr(type(obj), key, None)
    getf = getattr(attr, "fget", None)
    wr = getattr(getf, "__wrapped__", None)
    return getattr(wr, decorator, default)


def clear_changes_tracking(obj):
    """
    invokes the _clear_change_tracking method of the object if it exists.
    """
    _.get(obj, "_clear_change_tracking", _.noop)()


class ExtendedJsonEncoder(json.JSONEncoder):
    """JSONEncoder with additional capabilities to allow for encoding of Typed, and Untyped POPO objects using the jsonProperty attribute"""

    def __init__(
        self,
        includeTags=[],
        excludeTags=[],
        excludeUntagged=False,
        changesOnly=False,
        *args,
        **kwargs,
    ):
        """Initializer with additional parameters for managing serialized content

        Keyword Arguments:
            includeTags {list} -- List of str containing tag names for properties that should be included when serializing (default: {[]})
            excludeTags {list} -- List of str containing tag names for properties that should be excluded when serializing.  Ignored if includeTags is provided (default: {[]})
            excludeUntagged {bool} -- Flag to indicate whether properties that do not have tags should be included in the serialized output (default: {False})
        """
        super().__init__(*args, **kwargs)
        self._serializedInstances = (
            []
        )  # ensure instances are only serialized once to prevent circular serialization
        self._includeTags = includeTags
        self._excludeTags = excludeTags
        self._excludeUntagged = excludeUntagged
        self._changesOnly = changesOnly

    def default(self, obj):
        """Overrides the json.dumps default serializer"""
        if obj is None:
            return None

        # using __ref__ as a mechanism to prevent circular references in serialization
        if obj in self._serializedInstances and hasattr(obj, "__ref__"):
            return "__ref__:{0}".format(obj.__ref__)

        self._serializedInstances.append(obj)

        try:
            return json.JSONEncoder.default(self, obj)
        except:
            if hasattr(obj, "__dict__"):
                try:

                    def matchTag(key, tags, excludeUntagged):
                        """Matches the tags decorated on the property against the given list of tags and returns true or false if any matches are present

                        Arguments:
                            key {str} -- property name to check for tags
                            tags {str} -- list of tags to check against
                            excludeUntagged {bool} -- flag to indicate whether to exclude the property if no tags are present. It the property is untagged, and this value is set to True, then the results will be True

                        Returns:
                            [bool] -- [True or false indicating whether the key has a matching tag.]
                        """

                        # Since properties with tags are only available as class properties (not instance properties) we resolve the key properties to assess the tag existance, rather than the instance values
                        prop_tags = get_decorator(obj, key, "tags", [])

                        if len(prop_tags) == 0 and excludeUntagged is False:
                            return True

                        return _.some(prop_tags, lambda t: t in tags)

                    def filterKeysByTags(keys):
                        if len(self._includeTags) > 0:
                            keys = _.filter_(
                                keys,
                                lambda k: matchTag(
                                    k, self._includeTags, self._excludeUntagged
                                ),
                            )
                        if len(self._excludeTags) > 0:
                            keys = _.filter_(
                                keys,
                                lambda k: matchTag(
                                    k,
                                    self._excludeTags,
                                    not self._excludeUntagged,
                                )
                                is False,
                            )

                        return filterKeysByChanged(keys)

                    def filterKeysByChanged(keys):
                        if self._changesOnly is False:
                            return keys

                        changed_keys = _.result(
                            obj, "_changed_keys", _.identity([])
                        )

                        return _.filter_(
                            keys, lambda k: _.index_of(changed_keys, k) > -1
                        )

                    # this is a complex type that may or may not declare all attributes, so we will return a dictionary
                    def mapVal(destination, key):
                        if key.startswith("_"):
                            return destination
                        destination[key] = _.get(obj, key)
                        return destination

                    # this is to support the use of the @jsonProperty attribute for getters and setter functions.
                    def mapClassProp(destination, key):
                        if key.startswith("_"):
                            return destination

                        if issubclass(
                            type(_.get(type(obj), key, None)), jsonProperty
                        ):
                            destination[key] = _.get(obj, key)

                        return destination

                    ref = set_object_ref(obj)

                    result = {}

                    # if the class is using the @jsonSerializable decorator, then it may have _exclude_type_info = True
                    # if this is the case, the extended serializer will not attempt to use the __type__ and __ref__ properties to deserialize back to the original types
                    # if True, it will deserialize to a dictionary rather than the original type.
                    if not _.get(obj, "_exclude_type_info", False):
                        result = {
                            "__type__": get_full_type_name(obj),
                            "__ref__": ref,
                        }

                    result.update(
                        _.reduce_(
                            filterKeysByTags(obj.__dict__.keys()), mapVal, {}
                        )
                    )  # Apply instance properties
                    result.update(
                        _.reduce_(
                            filterKeysByTags(dir(type(obj))), mapClassProp, {}
                        )
                    )  # Apply class properties

                    return result
                except:
                    return None
            return str(obj)


class ExtendedJsonDecoder(json.JSONDecoder):
    """JSONDecoder capable of deserializing json strings that are encoded with type and reference information via the EntityAwareJsonEncoder"""

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
        self.parse_string = self._parse_string
        self.scanstr = (
            c_scanstring or py_scanstring
        )  # Hack: since the default json decoder does not allow us to override the scanstr directly, we need to duplicate this here so we can resolve references
        self.scan_once = scanner.py_make_scanner(self)
        self._ref_instances = {}

    def _parse_string(self, s, *args, **kwargs):
        """parses a given string using scanstr

        Arguments:
            s {[str]} -- string to parse

        Returns:
            [type] -- returns a tuple of the object, and the string representation
        """
        results = self.scanstr(s, *args, **kwargs)
        if results[0].startswith("__ref__"):
            refKey = results[0].split(":")[1]
            refObj = _.get(self._ref_instances, refKey)
            if refObj is not None:
                results = (refObj, results[1])
        return results

    def object_hook(self, obj):
        """object_hook implementation with type and ref support."""
        if isinstance(obj, dict):
            if "__type__" in obj:
                # import the type
                typeName = _.get(obj, "__type__")
                ref = _.get(obj, "__ref__")
                resolvedType = resolve_type_by_full_name(typeName)
                try:
                    instance = hydrate_from_dictionary(resolvedType(), obj)
                    self._ref_instances[ref] = instance
                    return instance
                except:
                    pass
        clear_changes_tracking(obj)
        return obj


def clone_to(obj, newType: type, **kwargs):
    """Performs a deep clone on the object using jsonProperties and converts it to the type specified in newType

    Keyword Arguments:
        obj {Any} -- the object to clone, (default: {None})
        includeTags {List[str]} -- List of property tags that should be included in the output.  Tags are defined using the @tags() decorator when declaring a property using the jsonProperty decorator
        excludeTags {List[str]} -- List of property tags that should be excluded in the output.  Tags are defined using the @tags() decorator when declaring a property using the jsonProperty decorator
        excludeUntagged {{bool}} -- true or falss indicating whether untagged properties should be excluded.  Defaults to False
    Returns:
        [str] -- [json formatted string]
    """

    t = from_json(to_json(obj), newType)
    return t


def clone(obj, **kwargs):
    """Performs a deep clone on the object using jsonProperties, properties may be excluded by tags

    Keyword Arguments:
        obj {Any} -- the object to clone, (default: {None})
        includeTags {List[str]} -- List of property tags that should be included in the output.  Tags are defined using the @tags() decorator when declaring a property using the jsonProperty decorator
        excludeTags {List[str]} -- List of property tags that should be excluded in the output.  Tags are defined using the @tags() decorator when declaring a property using the jsonProperty decorator
        excludeUntagged {{bool}} -- true or false indicating whether untagged properties should be excluded.  Defaults to False
    Returns:
        [str] -- [json formatted string]
    """

    t = from_json(to_json(obj, **kwargs))
    return t


def hydrate_from_dictionary(instance, obj):
    """hydrates the property values of instance from the values in obj

    Arguments:
        instance {object} -- Instance which will be populated with values
        obj {dict} -- Dictionary of provided values

    Returns:
        [type] -- [description]
    """

    def mapVal(destination, key):
        try:
            if key.startswith("_"):
                return destination

            # if the destination property was attributed with @jsonType, it will have a jsonType function on the wrapped function
            # we will use this declared type to hydrate the property rather than leaving it as a dict
            jsonType = get_decorator(destination, key, "_jsonType", None)
            isList = get_decorator(destination, key, "_isList", False)

            if jsonType:
                if isList:
                    typedArray = _.map_(
                        _.get(obj, key),
                        lambda v: hydrate_from_dictionary(jsonType(), v),
                    )
                    setattr(destination, key, typedArray)
                else:
                    typedValue = jsonType()
                    hydrate_from_dictionary(typedValue, _.get(obj, key))
                    setattr(destination, key, typedValue)
            else:
                setattr(destination, key, _.get(obj, key))
        except:
            # if a key does not exist on the destination object, just ignore it.
            pass
        return destination

    return _.reduce_(list(obj.keys()), mapVal, instance)


def hydrate_from_query_dictionary(instance, obj):
    """Hydrates values from a query dictionary as provided in an http request

    Arguments:
        instance {object} -- Instance which will be populated with values
        obj {dict} -- Http Query Dictionary of provided values

    Returns:
        [type] -- [description]
    """

    def mapVal(destination, key):
        try:
            destPropValue = _.get(obj, key, [""])
            destination[key] = (
                destPropValue if len(destPropValue) > 1 else destPropValue[0]
            )
        except:
            # if a key does not exist on the destination object, just ignore it.
            pass
        return destination

    result = _.reduce_(list(obj.keys()), mapVal, instance)
    return result


def to_json(self, obj=None, **kwargs) -> str:
    """Serializes the given object to a json formatted string

    Keyword Arguments:
        obj {Any} -- the object to serialize, (default: {None})
        includeTags {List[str]} -- List of property tags that should be included in the output.  Tags are defined using the @tags() decorator when declaring a property using the jsonProperty decorator
        excludeTags {List[str]} -- List of property tags that should be excluded in the output.  Tags are defined using the @tags() decorator when declaring a property using the jsonProperty decorator
        excludeUntagged {{bool}} -- true or falss indicating whether untagged properties should be excluded.  Defaults to False
        changesOnly {{bool}}  -- serializes only properties that have changed since the object was created. Change tracking requires classes to be decorated with @jsonSerializable, and properties to be decorated with jsonProperty decorator
    Returns:
        [str] -- [json formatted string]
    """
    # if is None, then we are trying to serialize self.
    if obj is None:
        obj = self

    return json.dumps(
        obj,
        check_circular=False,
        cls=ExtendedJsonEncoder,
        indent=4,
        sort_keys=True,
        **kwargs,
    )


def from_json(jsonValue: str, resultType=None):
    """Deserializes an object from the given jsonValue.  Resolving where possible types as specified in the json

    Arguments:
        jsonValue {str} -- json formatted string

    Keyword Arguments:
        resultType {[type]} -- Type override indicater for jsonvalues not encoded with type information. Or in the case where a type conversion is desired (default: {None})

    Returns:
        object -- deserialized object
    """

    result = json.loads(jsonValue, cls=ExtendedJsonDecoder)
    if resultType is not None and not isinstance(result, resultType):
        result = hydrate_from_dictionary(
            resultType(), _.get(result, "__dict__", result)
        )

    clear_changes_tracking(result)
    return result


def to_yaml(self, obj=None, **kwargs) -> str:
    """Serializes the object to YAML"""
    if obj is None:
        obj = self
    jsn = to_json(obj, **kwargs)
    dct = json.loads(jsn)
    results = yaml.dump(dct)
    return results


def from_yaml(yamlValue, resultType=None):
    obj = yaml.safe_load(yamlValue)
    jsn = json.dumps(obj)
    results = from_json(jsn, resultType)
    return results


def set_on_change_intercept(target, *args, **kwargs):
    def set_intercept_decorator(func, *args, **kwargs):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return set_intercept_decorator


class jsonProperty(property):
    """decorator to indicate that a property should be serialized when using to_json"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __set__(self, obj, value):
        super().__set__(obj, value)
        changed_properties = _.get(obj, "_changed_properties")
        if changed_properties is not None:
            changed_properties.add(self.fset.__name__)


def jsonSerializable(cls):
    """
    Decorator to mark a class as json serializable, and allows for property change tracking
    """

    def _to_json(self, *args, **kwargs):
        return to_json(self, *args, **kwargs)

    def _to_yaml(self, *args, **kwargs):
        return to_yaml(self, *args, **kwargs)

    def _to_dict(self) -> dict:
        return json.loads(self._to_json())

    def _hydrate(self, dictionary: dict):
        hydrate_from_dictionary(self, dictionary)

    def _on_prop_change(self, property: str):
        self._changed_properties.add(property)

    def _clear_change_tracking(self):
        self._changed_properties.clear()

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, type(self)):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    def _changed_keys(self):
        """Returns a list of property keys that have been changed, or if the property is an object, and that object has changes of its children have changes, that key will appear as changed"""
        direct_changed_keys = list(self._changed_properties)
        unchanged_keys = _.filter_(
            _.keys(type(self)),
            lambda k: _.index_of(direct_changed_keys, k) == -1,
        )

        indirect_changed_keys = _.filter_(
            unchanged_keys,
            lambda k: _has_key_changed(self, k),
        )

        return _.union(direct_changed_keys, indirect_changed_keys)

    def _has_key_changed(self, key: str):
        if not key:
            return False

        attr = getattr(self, key, None)
        try:
            changes = attr._changed_keys()
            change_count = len(changes)
            return change_count > 0
        except:
            pass

        return False

    def init_wrapper(func):
        @wraps(func)
        def init_decorator(*args, **kwargs):
            obj = args[0]
            obj._changed_properties = set()
            func(*args, **kwargs)
            obj._clear_change_tracking()

        return init_decorator

    cls._exclude_type_info = True
    cls._to_json = _to_json
    cls.to_json = _to_json
    cls._to_dict = _to_dict
    cls.to_dict = _to_dict
    cls._hydrate = _hydrate
    cls.to_str = to_str
    cls.__repr__ = __repr__
    cls.__eq__ = __eq__
    cls.__ne__ = __ne__
    cls._on_prop_change = _on_prop_change
    cls._clear_change_tracking = _clear_change_tracking
    cls._to_yaml = _to_yaml
    cls._to_yaml = _to_yaml
    cls._changed_keys = _changed_keys
    cls.__init__ = init_wrapper(cls.__init__)
    return cls


def jsonType(typeDef, isList=False):
    """decorator to be used with the jsonProperty decorator to indicate the expected type when deserializing"""

    def jsonTypeDecorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        func._jsonType = typeDef
        func._isList = isList
        return wrapper

    return jsonTypeDecorator


def tags(*args):
    """decorator to allow you to add tags to a property that can be used when serializing to include or exclude properties."""

    def tagsDecorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        func.tags = list(args)

        return wrapper

    return tagsDecorator
