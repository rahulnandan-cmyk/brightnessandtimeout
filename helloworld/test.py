"""This script separates even and odd numbers from a given set."""
x = {1, 2, 3, 4, 5, 6}

a = {n for n in x if n % 2 == 0}
b = {n for n in x if n % 2 != 0}

print("The a holds even number", a)
print("The b holds odd number", b)

print(a,b)
