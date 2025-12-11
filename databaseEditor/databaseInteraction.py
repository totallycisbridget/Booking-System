import sqlite3, os, sys

#region presentTables
def tableNames(cur): #list tables in database
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';") #geet table names
    return [row[0] for row in cur.fetchall()] #reeturn list

def tableColumns(cur, tableName): #column names in specific table
    cur.execute(f"PRAGMA table_info({tableName});") #get table info
    return [row[1] for row in cur.fetchall()] #return column names
#endregion

#region insertData
def tableInsert(conn,  tableName, columns): #insert data into table
    cur = conn.cursor()

    inputs = []
    for col in columns: #go throug each column and get user input
        val = input(f"{col}: ") 
        inputs.append(val)

    placeholders = ",".join("?" for _ in columns) #parametised queries. prevent SQL injection
    query = f"INSERT INTO {tableName} ({','.join(columns)}) VALUES ({placeholders});"
    
    try:
        cur.execute(query, inputs) #execute insert query
        conn.commit() #commit changes to database
        print(f"\nData insertion into {tableName}, successful\n") 

    except sqlite3.IntegrityError as e: #inforrm userr of integrity errors
        print(f"\nIntegrity error: {e} \n")
        input("Press enter to continue")

    except sqlite3.OperationalError as e: #inform user of operational errors
        print(f"\nSQL error: {e} \n")
        input("Press enter to continue")

    except sqlite3.Error as e: #inform user of general database errors
        print(f"\nError: {e} \n")
        input("Press enter to continue")
#endregion

#region viewData


def viewData(tableName, cur): #leets user vieew conteents of table
    cur.execute(f"SELECT * FROM {tableName}") #select all data from table

    rows = cur.fetchall()#get all rows

    if not rows: #inform user of no data in the table
        print(f"\n(No data in {tableName})\n")
        return
    
    print(f"Format of {tableName}: \n") #present format of table to user
    columns = tableColumns(cur, tableName)


    for row in rows:
        print(" | ".join(str(x) for x in row)) #show contents of table

#endregion

def main():
    baseDir = os.path.join(os.getcwd()) #directory of this file


    dbFiles = [f for f in os.listdir(baseDir) if f.endswith(".db")] #just the databasee files
    
    print("Database files found:")
    for i, f in enumerate(dbFiles): #print each database file with a number (1- database.db))
        print(f"{i}- {f}") 


    dbName = input("Enter the SQLite database filename (excluding .db): ")
    print("A new database will be created if it does not exist.") #just what sqlite does, prrobably can stop it but cant be bothered
    dbName += ".db" #add the .db file extension to name
    dbPath = os.path.join(baseDir, dbName)


    try:
        conn = sqlite3.connect(dbPath) #connect to the database at the given location
        cur = conn.cursor()
        print("\nConnected successfully!\n") 

    #inform user of connection error
    except sqlite3.Error as e: 
        print("Failed to connect:", e)
        input("Press enter to continue")
        return

    while True:
        table = tableNames(cur) #list the tables
        print("Tables in database:")
        for i, t in enumerate(table): #show each table name with number
            print(f"{i}- {t}") 

        choice = input("\nSelect a table number to view or edit or 'q' to exit: ") 
        if choice.lower() == 'q':
            sys.exit()
        
        elif not choice.isdigit() or not (0 <= int(choice) <= len(table)): #check if user has input a number according to the amount of tables
            print("\nInvalid choice.\n")
            continue

        tableName = table[int(choice)] #get the selected table name

        columns = tableColumns(cur, tableName) #column names
        print(f"\nColumns in {tableName}: {columns}") #print contents of table

        while True:
            choice = input("View (1) or edit (2) or 'q' to go back:  ")

            if choice.lower() == "q":
                break
            elif choice == "1":
                viewData(tableName, cur) #get data of desired table:
            elif choice == "2":
                tableInsert(conn, tableName, columns) #insert desired data
            else:
                print("\nInvalid choice.\n")
                continue
                
    conn.close() #close cursor

if __name__ == "__main__":
    main()
