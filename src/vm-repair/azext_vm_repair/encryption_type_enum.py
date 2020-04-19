# Python code to demonstrate enumerations
# Access and comparison
# importing enum for enumerations
import enum
# creating enumerations using class


class encryption(enum.Enum):
    not_encrypted = 1
    single_with_kek = 2
    single_without_kek = 3
    dual = 4
