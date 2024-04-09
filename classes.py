class Class1:
    def method1(self):
        print("Method 1 from Class 1")

class Class2:
    def __init__(self):
        # Creating an instance of Class1 within Class2
        self.class1_instance = Class1()

    def call_method1_of_class1(self):
        # Calling method1 of Class1 using the instance created in __init__
        self.class1_instance.method1()
