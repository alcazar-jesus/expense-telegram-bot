class MyObject:
    def __init__(self, name):
        self.name = name

# Creamos una instancia de MyObject
my_instance = MyObject("Objeto Original")



print(f"Antes de setattr: {hasattr(my_instance, 'new_attribute')}") # False

some_data = {"key": "value", "number": 123}

# Usamos setattr para añadir un nuevo atributo
setattr(my_instance, "new_attribute", some_data)

print(f"Después de setattr: {hasattr(my_instance, 'new_attribute')}") # True
print(f"Valor del nuevo atributo: {my_instance.new_attribute}") # {'key': 'value', 'number': 123}

# También podemos modificar un atributo existente (aunque para 'name' sería más común my_instance.name = "Nuevo Nombre")
setattr(my_instance, "name", "Objeto Modificado")
print(f"Nombre modificado: {my_instance.name}") # Objeto Modificado