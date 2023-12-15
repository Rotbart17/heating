import sqlite3

conn = sqlite3.connect("./heizung.db")
cursor=conn.cursor()
def  addnewdata():
    try:
        cursor.execute(''' INSERT INTO users (name, age) VALUES(?,?) ''',(name.value, age.value))
        conn.commit()



def get_all_data():
    cursor.execute('''SELECT * FROM uers; ''')
    res= cursor.fetchall()
    result=[]
    for row in res:
        # covert JASON ARRAY to DICT 
        data={}
        for i, col in enumerate(cursor.description):
            data[col[0]]=row[i]
        result.append(data)
        print (result)


