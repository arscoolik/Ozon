import pandas
import requests
from check import detect_type
import ast

#I deleted the Alert function, because it made no sense when testing on a local network with no access to the mattermost server

class dlp:
    def __init__(self, filename):
        self.filename = filename
        self.header = {}
        try:
            self.db = pandas.read_csv(self.filename, header=None, dtype="string")
        except:
            self.fl = False
            return
        self.check()
        self.crm()
        self.fl = True

    def check(self):
        for i in self.db.columns:
            tmp = detect_type(str(self.db[i][0])).name
            if tmp in self.header:
                self.header[tmp].append(i)
            else:
                self.header[tmp] = [i]
     

    def find_key(self, val):
        for i in self.header:
            if self.header[i][0] == int(val):
                return i
        return "QUESTION"

    def crm(self):
        masks = requests.post('http://127.0.0.1:8000/api/danger_level_service/', json={"action_type":"validate_danger_data","data_list": list(self.header.keys())})
        masks  = (masks.content).decode()
        masks = ast.literal_eval(masks)
        for i in masks:
            for j in range(len(self.db[self.header[i][0]])):
                tmp = len(self.db[self.header[i][0]][j])
                self.db[self.header[i][0]][j] =  self.db[self.header[i][0]][j].strip()
                if tmp < 10:
                    self.db[self.header[i][0]][j] = '*'*tmp
                else:
                    self.db[self.header[i][0]][j] = self.db[self.header[i][0]][j][0] + '*'*(tmp-2) + self.db[self.header[i][0]][j][-1]
        for i in self.header["QUESTION"]:
            for j in range(len(self.db[i])):
                tmp = len(self.db[i][j])
                self.db[i][j] =  self.db[i][j].strip()
                if tmp < 10:
                    self.db[i][j] = '*'*tmp
                else:
                    self.db[i][j] = self.db[i][j][0] + '*'*(tmp-2) + self.db[i][j][-1] 

    def ret(self):
        if self.fl:
            return self.db
        return "Error"

# instead of "user_data.csv" you need to add the PATH to your csv file
test = dlp("user_data.csv")
print(test.ret())
