# this is the python scripts fo encryption and decryption

# HOW TO ADD YOUR OWN ENCRYPTION AND DECREPTION

# 1) the function encrypt will encrypt your message and send it to the server
# 2) the function decrypt will decrypt the message and give back it to tyou
# 3) ho can define as many function as you want
# 4) but the encrtypt function must take plain text and return encrypted message
# 5) decrypt function must take encrypted message and return plain text

# i will provide you the simplest encryption in universe as an example

def encrypt(message):
    """
    DOCSTRING: this function will get a plain text message and return it encrypted
    message:   plain text
    """

    encrypted = ""
    for character in message: encrypted += chr(ord(character) + 1)

    return encrypted

def decrypt(message):
    """
    DOCSTRING: this function will get a encrypted message and return decrypted plain text
    message: encrypted message
    """

    decrypted = ""
    for character in message: decrypted += chr(ord(character) - 1)

    return decrypted