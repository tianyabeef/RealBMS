from django.test import TestCase

# Create your tests here.
if __name__ == '__main__':
    a = "18A0009"
    b = list(a)
    c = ""
    if 65<= ord(b[-1])<= 90:
        print(ord(b[-1]))
        b[-1] = chr(ord(b[-1])+1)
        for i in b:
            c += i
    elif 48 <= ord(b[-1]) <= 57:
        print("************")
        a += "A"
    print(a)
