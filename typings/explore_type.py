import inspect

from more_itertools import flatten


def print_class(cls: type):
    parents_attribute_names = list(flatten(dir(base) for base in cls.__bases__))
    print("class " + cls.__name__ + "(" + ",".join([base.__name__ for base in cls.__bases__]) + "):")
    instance = cls()

    for attribute in dir(instance):
        if attribute.startswith("__") or attribute in parents_attribute_names:
            continue
        attr_instance = getattr(instance, attribute)
        attr_type = type(attr_instance)
        if str(attr_type) == "<class 'builtin_function_or_method'>":
            try:
                print(attribute, inspect.signature(attr_instance))
            except ValueError:
                print("    def " + str(attribute) + "(self) -> Unknown: ...")
        else:
            print(attribute, attr_type)
