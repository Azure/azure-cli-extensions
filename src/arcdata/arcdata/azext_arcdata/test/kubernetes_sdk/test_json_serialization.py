from datetime import datetime
import json
from azext_arcdata.core.json_serialization import (
    jsonSerializable,
    jsonType,
    to_json,
    from_json,
    jsonProperty,
    tags,
    to_yaml,
    from_yaml,
)
import pydash as _
import unittest


class Test_Serialization(unittest.TestCase):
    # ensures that the message monitor, when started will capture all messages sent to the service broker
    def test_serializeAnonObject(self):
        testObj = {"message": "test obj"}

        result = to_json(testObj)
        self.assertTrue(result.find("test obj"))

    def test_deserializeAnonObject(self):
        testJson = '{"message":"test obj"}'
        result = from_json(testJson)
        self.assertTrue(result["message"] == "test obj")

    def test_serialize_class(self):
        t = SerializeClass()
        result = to_json(t)
        print(result)
        dresult = from_json(result)
        self.assertIsInstance(dresult, SerializeClass)
        self.assertEqual("Prop1", t.prop1)

    def test_serialize_class_yaml(self):
        t = SerializeClass()
        result = to_yaml(t)
        print(result)
        dresult = from_yaml(result)
        self.assertIsInstance(dresult, SerializeClass)
        self.assertEqual("Prop1", t.prop1)

    def test_serialize_complex_classes(self):
        c = ComplexSerializeClass()
        result = to_json(c)
        print(result)
        dresult = from_json(result)
        self.assertIsInstance(dresult, ComplexSerializeClass)
        self.assertIsInstance(dresult.child, SerializeClass)

    def test_serialize_complex_classes_yaml(self):
        c = ComplexSerializeClass()
        result = to_yaml(c)
        print(result)
        dresult = from_yaml(result)
        self.assertIsInstance(dresult, ComplexSerializeClass)
        self.assertIsInstance(dresult.child, SerializeClass)

    def test_serialize_getters_setters(self):
        testClass = GetterSetter()
        testClass.prop1 = "TestValue"
        json = to_json(testClass)
        result = from_json(json)
        self.assertEqual(result.prop1, testClass.prop1)

    def test_serialize_getters_setters_yaml(self):
        testClass = GetterSetter()
        testClass.prop1 = "TestValue"
        json = to_json(testClass)
        result = from_json(json)
        self.assertEqual(result.prop1, testClass.prop1)

    def test_serialize_inherited_getters_setters(self):
        testClass = GetterSetterSubClass()
        testClass.prop1 = "TestValue"
        json = to_json(testClass)
        result = from_json(json)
        self.assertEqual(result.prop1, testClass.prop1)

    def test_serialize_inherited_getters_setters_yaml(self):
        testClass = GetterSetterSubClass()
        testClass.prop1 = "TestValue"
        yml = to_yaml(testClass)
        result = from_yaml(yml)
        self.assertEqual(result.prop1, testClass.prop1)

    def test_deserialize_references(self):
        # ensure that serializations that contain circular references, or multiple references to the same instance will deserialize to the same instance structure.
        test1 = GetterSetter()
        test1.prop1 = "test"
        testArr = [test1, test1, test1, test1]
        testJson = to_json(testArr)
        deserializedArr = from_json(testJson)
        deserialized1 = deserializedArr[0]
        for item in deserializedArr:
            self.assertEqual(deserialized1, item)
        self.assertEqual(4, len(deserializedArr))

    def test_deserialize_references_yaml(self):
        # ensure that serializations that contain circular references, or multiple references to the same instance will deserialize to the same instance structure.
        test1 = GetterSetter()
        test1.prop1 = "test"
        testArr = [test1, test1, test1, test1]
        testJson = to_yaml(testArr)
        deserializedArr = from_yaml(testJson)
        deserialized1 = deserializedArr[0]
        for item in deserializedArr:
            self.assertEqual(deserialized1, item)
        self.assertEqual(4, len(deserializedArr))

    def test_serialize_references(self):
        test1 = GetterSetter()
        test1.prop1 = "test"
        testHash = str(hash(test1))
        test1.__ref__ = testHash
        testArr = [test1, test1, test1, test1]
        testJson = to_json(testArr)

        self.assertEqual(4, testJson.count(testHash))

    def test_serialize_references_yaml(self):
        test1 = GetterSetter()
        test1.prop1 = "test"
        testHash = str(hash(test1))
        test1.__ref__ = testHash
        testArr = [test1, test1, test1, test1]
        testYaml = to_yaml(testArr)

        self.assertEqual(4, testYaml.count(testHash))

    def test_deserialize_subclass_with_parentclass_hint(self):
        sub = GetterSetterSubClass()
        subJson = to_json(sub)
        subDeserialized = from_json(subJson, GetterSetter)
        self.assertTrue(isinstance(subDeserialized, GetterSetterSubClass))

    def test_deserialize_subclass_with_parentclass_hint_yaml(self):
        sub = GetterSetterSubClass()
        subJson = to_yaml(sub)
        subDeserialized = from_yaml(subJson, GetterSetter)
        self.assertTrue(isinstance(subDeserialized, GetterSetterSubClass))

    def test_serialize_only_include_tags(self):
        tc = TaggedClass()
        tc.taggedStr = "test"
        tc.taggedInt = 1
        tc.unTaggedStr = "Untagged"
        tc.unTaggedInt = 1

        json = to_json(tc, includeTags=["test1", "test2"], excludeUntagged=True)
        dtc = from_json(json)
        self.assertEqual(dtc.taggedStr, tc.taggedStr)
        self.assertEqual(dtc.taggedInt, tc.taggedInt)
        self.assertNotEqual(dtc.unTaggedStr, tc.unTaggedStr)
        self.assertNotEqual(dtc.unTaggedInt, tc.unTaggedInt)

    def test_serialize_only_include_tags_2(self):
        tc = TaggedClass()
        tc.taggedStr = "test"
        tc.taggedInt = 1
        tc.unTaggedStr = "Untagged"
        tc.unTaggedInt = 1

        json = to_json(tc, includeTags=["test1"], excludeUntagged=True)
        dtc = from_json(json)
        self.assertEqual(dtc.taggedStr, tc.taggedStr)
        self.assertNotEqual(dtc.taggedInt, tc.taggedInt)
        self.assertNotEqual(dtc.unTaggedStr, tc.unTaggedStr)
        self.assertNotEqual(dtc.unTaggedInt, tc.unTaggedInt)

    def test_serialize_ignore_exclude_tags(self):
        tc = TaggedClass()
        tc.taggedStr = "test"
        tc.taggedInt = 1
        tc.unTaggedStr = "Untagged"
        tc.unTaggedInt = 1

        json = to_json(tc, excludeTags=["test1"], excludeUntagged=True)
        dtc = from_json(json)
        self.assertNotEqual(dtc.taggedStr, tc.taggedStr)
        self.assertEqual(dtc.taggedInt, tc.taggedInt)
        self.assertNotEqual(dtc.unTaggedInt, tc.unTaggedInt)
        self.assertNotEqual(dtc.unTaggedStr, tc.unTaggedStr)

    def test_serialize_ignore_exclude_tags_2(self):
        tc = TaggedClass()
        tc.taggedStr = "test"
        tc.taggedInt = 1
        tc.unTaggedStr = "Untagged"
        tc.unTaggedInt = 1

        json = to_json(tc, excludeTags=["test1"])
        dtc = from_json(json)
        self.assertNotEqual(dtc.taggedStr, tc.taggedStr)
        self.assertEqual(dtc.taggedInt, tc.taggedInt)
        self.assertEqual(dtc.unTaggedStr, tc.unTaggedStr)
        self.assertEqual(dtc.unTaggedInt, tc.unTaggedInt)

    def test_decorated_serializable_class(self):
        dsc = DecoratedSerializableClass()
        serialized = dsc._to_dict()
        assert serialized["prop1"] == "Prop1"
        assert serialized["prop2"] == "Prop2"
        serialized["prop1"] = "TestProp1"
        serialized["prop2"] = "TestProp2"
        dsc._hydrate(serialized)
        assert dsc.prop1 == "TestProp1"
        assert dsc.prop2 == "TestProp2"

    def test_decorated_complex_serializable_class(self):
        dsc = ComplexDecoratedSerializeClass()
        serialized = dsc._to_dict()
        assert serialized["child"]["prop1"] == "ChildProp1"
        assert serialized["child"]["prop2"] == "ChildProp2"
        assert serialized["prop1"] == "Prop1"
        serialized["child"]["prop1"] = "TestChildProp1"
        serialized["child"]["prop2"] = "TestChildProp2"
        serialized["prop1"] = "TestProp1"
        dsc._hydrate(serialized)
        assert dsc.child.prop1 == "TestChildProp1"
        assert dsc.child.prop2 == "TestChildProp2"
        assert dsc.prop1 == "TestProp1"

    def test_decorated_array_serializable_class(self):
        dsc = ComplexDecoratedArraySerializeClass()
        serialized = dsc._to_dict()
        assert serialized["children"][0]["prop1"] == "Child1Prop1"
        assert serialized["children"][0]["prop2"] == "Child1Prop2"
        assert serialized["children"][1]["prop1"] == "Child2Prop1"
        assert serialized["children"][1]["prop2"] == "Child2Prop2"
        assert serialized["prop1"] == "Prop1"
        serialized["children"][0]["prop1"] = "TestChild1Prop1"
        serialized["children"][0]["prop2"] = "TestChild1Prop2"
        serialized["children"][1]["prop1"] = "TestChild2Prop1"
        serialized["children"][1]["prop2"] = "TestChild2Prop2"
        serialized["prop1"] = "TestProp1"
        dsc._hydrate(serialized)
        assert dsc.children[0].prop1 == "TestChild1Prop1"
        assert dsc.children[0].prop2 == "TestChild1Prop2"
        assert dsc.children[1].prop1 == "TestChild2Prop1"
        assert dsc.children[1].prop2 == "TestChild2Prop2"
        assert dsc.prop1 == "TestProp1"

    def test_change_tracking_no_changes_on_init(self):
        dsc = DecoratedSerializableClass()
        assert len(dsc._changed_properties) == 0
        dsc.prop1 = "test"
        assert len(dsc._changed_properties) == 1

    def test_deep_change_tracking(self):
        cdsc = ComplexDecoratedSerializeClass2()
        cdsc.complexChild.child.prop1 = "childPropChanges"
        cdsc.complexChild.name = "child1"
        cdsc.complexChild2.prop1 = "testChange"
        cdsc.complexChild2.name = "child2"
        cdsc._changed_keys()
        json_str = to_json(cdsc, changesOnly=True)

        deserialized = json.loads(json_str)

        assert (
            _.get(deserialized, "complexChild.child.prop1")
            == "childPropChanges"
        )
        assert _.get(deserialized, "complexChild.child.name") is None
        assert _.get(deserialized, "complexChild.prop1") is None
        assert (
            _.get(deserialized, "complexChild.name") is None
        )  # this property is not marked as a jsonProperty, and should not be tracked in the change tracking.
        assert _.get(deserialized, "complexChild2.prop1") == "testChange"
        assert (
            _.get(deserialized, "complexChild.name") is None
        )  # this property is not marked as a jsonProperty, and should not be tracked in the change tracking.


@jsonSerializable
class DecoratedSerializableClass:
    def __init__(self):
        self.prop1 = "Prop1"
        self.prop2 = "Prop2"

    _prop1 = None

    @jsonProperty
    def prop1(self):
        return self._prop1

    @prop1.setter
    def prop1(self, value):
        self._prop1 = value


@jsonSerializable
class ComplexDecoratedSerializeClass:
    def __init__(self):
        self.child = DecoratedSerializableClass()
        self.child.prop1 = "ChildProp1"
        self.child.prop2 = "ChildProp2"
        self.prop1 = "Prop1"

    @jsonProperty
    @jsonType(DecoratedSerializableClass)
    def child(self):
        return self._child

    @child.setter
    def child(self, value):
        self._child = value

    @jsonProperty
    def prop1(self):
        return self._prop1

    @prop1.setter
    def prop1(self, value):
        self._prop1 = value


@jsonSerializable
class ComplexDecoratedSerializeClass2:
    def __init__(self):
        self.complexChild = ComplexDecoratedSerializeClass()
        self.complexChild2 = ComplexDecoratedSerializeClass()

    @jsonProperty
    def complexChild(self):
        return self._complexChild

    @complexChild.setter
    def complexChild(self, value):
        self._complexChild = value

    @jsonProperty
    def complexChild2(self):
        return self._complexChild2

    @complexChild2.setter
    def complexChild2(self, value):
        self._complexChild2 = value


@jsonSerializable
class ComplexDecoratedArraySerializeClass:
    def __init__(self):
        self.prop1 = "Prop1"

        self.children = list()
        child = DecoratedSerializableClass()
        child.prop1 = "Child1Prop1"
        child.prop2 = "Child1Prop2"
        self.children.append(child)

        child = DecoratedSerializableClass()
        child.prop1 = "Child2Prop1"
        child.prop2 = "Child2Prop2"
        self.children.append(child)

    @jsonProperty
    @jsonType(DecoratedSerializableClass, True)
    def children(self):
        return self._child

    @children.setter
    def children(self, value):
        self._child = value


class SerializeClass:
    def __init__(self):
        self.prop1 = "Prop1"
        self.date2 = datetime.now()
        self.prop3 = "Prop2"


class ComplexSerializeClass:
    def __init__(self):
        self.child = SerializeClass()
        self.child.prop1 = "ChildProp1"
        self.child.prop3 = "ChildProp3"
        self.prop1 = "Prop1"


class TaggedClass:
    def __init__(self):
        self._taggedStr = ""
        self._taggedInt = 0
        self._unTaggedStr = ""
        self._unTaggedInt = 0

    @jsonProperty
    @tags("test1")
    def taggedStr(self):
        return self._taggedStr

    @taggedStr.setter
    def taggedStr(self, value):
        self._taggedStr = value

    @jsonProperty
    @tags("test2")
    def taggedInt(self):
        return self._taggedInt

    @taggedInt.setter
    def taggedInt(self, value):
        self._taggedInt = value

    @jsonProperty
    def unTaggedStr(self):
        return self._unTaggedStr

    @unTaggedStr.setter
    def unTaggedStr(self, value):
        self._unTaggedStr = value

    @jsonProperty
    def unTaggedInt(self):
        return self._unTaggedInt

    @unTaggedInt.setter
    def unTaggedInt(self, value):
        self._unTaggedInt = value


class GetterSetter:
    def __init__(self):
        self.prop1 = ""

    @jsonProperty
    @tags("test")
    def prop1(self):
        return self._prop1

    @prop1.setter
    def prop1(self, value):
        self._prop1 = value


class GetterSetterSubClass(GetterSetter):
    def __init__(self):
        super().__init__()

    @jsonProperty
    def prop1(self):
        return self._prop1

    @prop1.setter
    def prop1(self, value):
        self._prop1 = value
