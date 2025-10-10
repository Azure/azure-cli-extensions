# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from functools import wraps, singledispatch


def validatedclass(cls):
    """
    Decorator that monkey patches a given class to be "validatable"
    :param cls: class to patch
    """
    cls._validators = []
    for name in dir(cls):
        method = getattr(cls, name)
        if hasattr(method, "_validator"):
            cls._validators.append(name)
    setattr(cls, "validate", validate)
    return cls


def validator(fn):
    """
    Decorator that marks a class method as a validator
    :param fn: function to patch
    """
    fn._validator = True
    return fn


def validate(self, client):
    """
    Invokes all methods marked as validators on this instance
    """
    for name in self._validators:
        getattr(self, name)(client)


def enforcetype(cls):
    """
    Enforces a type on a property setter for some class. Throws an error if the
    type of the value provided to the setter is not the exact type provided or
    a subclass of that type
    """

    def decorator(f):
        def wrapper(self, val, *args, **kwargs):
            if (
                not isinstance(val, cls)
                and type(val) is not cls
                and not issubclass(type(val), cls)
            ):
                raise TypeError(
                    "Type '{}' is not compatible with property {}. Requires {}".format(
                        type(val), f.__name__, cls
                    )
                )
            return f(self, val, *args, **kwargs)

        return wrapper

    return decorator


def method_dispatch(f):
    """
    This decorator modifies the behavior of singledispatch to support
    overloading based on the type of the SECOND argument in a function instead
    of the first. As the name suggests this is useful for method overloading
    since the first argument in a class method is always 'self'. TODO(jakedern):
    Remove this in favor of functools.singledispatchmethod after upgrading to
    python3.8
    :param f: the function to wrap
    :returns: Function that is singularly dispatched based on the second argument
    """
    dispatcher = singledispatch(f)

    @wraps(dispatcher)
    def wrapper(*args, **kwargs):
        return dispatcher.dispatch(args[1].__class__)(*args, **kwargs)

    wrapper.register = dispatcher.register
    return wrapper
