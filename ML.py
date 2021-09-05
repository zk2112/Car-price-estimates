from mysql import connector
from sklearn import tree
import mysql.connector
from mysql.connector import errorcode
from sklearn.preprocessing import LabelEncoder

cnx=mysql.connector.connect(user='root',host='127.0.0.1',database='carDB')
cursor=cnx.cursor()

try:
    cursor.execute('SELECT * FROM car')
except mysql.connector.Error as err:
    print(err)
    
List=list(cursor) 
x1=[]
y=[]
x=[]
for item in List :
    x1.append(item[1:8])
    y.append(item[8])

lb=LabelEncoder()
for temp in x1:
    x.append(lb.fit_transform(temp))



clf=tree.DecisionTreeClassifier()
clf=clf.fit(x,y)

newdata=[lb.fit_transform(['پراید','۱۳۱','SE',2000,1398,'سفید','سالم و بی خط و خش'])]       # TODO  input

print(clf.predict(newdata))





