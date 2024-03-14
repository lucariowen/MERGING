# Python
import pickle

# Vulnerable code
def load_data(data):
    return pickle.loads(data)

# Malicious data can be deserialized and executed
malicious_data = b'...' # Replace with a malicious serialized object
load_data(malicious_data)
