my_dict = {"a": 1, "b": 2, "c": 3}

keys = [key for key in my_dict]
values = [my_dict[key] for key in my_dict]

print(keys)   # output: ['a', 'b', 'c']
print(values) # output: [1, 2, 3]