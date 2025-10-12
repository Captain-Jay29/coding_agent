from .operations import add, subtract, multiply, divide, modulo

class Calculator:
    def add(self, a, b):
        return add(a, b)

    def subtract(self, a, b):
        return subtract(a, b)

    def multiply(self, a, b):
        return multiply(a, b)

    def divide(self, a, b):
        return divide(a, b)

    def modulo(self, a, b):
        return modulo(a, b)
