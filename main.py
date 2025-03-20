import base64 as b, os as o, sys as s, hashlib as h  
from handlers import bot  
from functions import DataManager  

# developer.txt
# attack.txt
# main.py  
# in teeno script ko modified mat karo 😑  

e = ["YXR0YWNrLnR4dA==", "ZGV2ZWxvcGVyLnR4dA=="]  
r = [b.b64decode(i).decode('utf-8') for i in e]  

for f in r:  
    if not o.path.isfile(f):  
        print(f"{f} nahi mila. Script band kiya jaa raha hai.")  
        s.exit()  

with open('developer.txt', 'r') as d:  
    o_t = d.read()  

with open('attack.txt', 'r') as a:  
    e_h = a.read().strip()  

def g_h(t):  
    return h.sha256(t.encode()).hexdigest()  

c_h = g_h(o_t)  

if c_h == e_h:  
    print(o_t)  
else:  
    print(b.b64decode("RE9OVCBDSEFOR0UgVEhFIERFVkVMT1BFUiBORU1FCi8vIEZHIC0tIEBwYl9YMDE=").decode())  
    s.exit()  

if __name__ == "__main__":  
    DataManager.load_data()  
    print("\n\n" + b.b64decode("wr8gRERvUyBCb3QgU3RhcnRlZCE=").decode())  
    bot.infinity_polling()  
