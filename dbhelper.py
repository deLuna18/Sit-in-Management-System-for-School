from sqlite3 import connect,Row

database:str = 'usermanagement.db'

def getprocess(sql: str, params: tuple = ()) -> list:
    db = connect(database)
    cursor: object = db.cursor()
    cursor.row_factory = Row
    cursor.execute(sql, params)
    data: list = cursor.fetchall()
    db.close()
    return [dict(row) for row in data] 
    
def postprocess(sql: str, params: tuple = ()) -> bool:
    db = connect(database)
    cursor: object = db.cursor()
    cursor.execute(sql, params)
    db.commit()
    db.close()
    return cursor.rowcount > 0
    
def get_all_users() -> list:
    sql = "SELECT * FROM users"
    return getprocess(sql)

def get_username(username: str) -> list:
    sql = "SELECT * FROM users WHERE username = ?"
    return getprocess(sql, (username,))

def register_user(lastname: str, firstname: str, middlename: str, 
                  course: str, year_level: str, email_address: str, 
                  username: str, password: str) -> bool:
    
    if get_username(username):
        return False  
    
    default_profile_picture = "profile_picture.png" 

    sql = """INSERT INTO users (lastname, firstname, middlename, course, year_level, 
                                email_address, username, password, profile_picture) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
             
    return postprocess(sql, (lastname, firstname, middlename, course, year_level, 
                             email_address, username, password, default_profile_picture))

def update_profile_picture(username: str, filename: str) -> bool:
    sql = "UPDATE users SET profile_picture = ? WHERE username = ?"
    return postprocess(sql, (filename, username))


def get_student_by_username(username: str) -> dict:
    sql = "SELECT * FROM users WHERE username = ?"
    student_list = getprocess(sql, (username,))

    if student_list:
        student = student_list[0]
        student["profile_picture"] = student.get("profile_picture") or "profile_picture.png"
        return student

    return None


def update_student_profile(username: str, firstname: str, middlename: str, lastname: str, 
                           course: str, year_level: str, email_address: str, address: str, 
                           profile_picture: str) -> bool:
    sql = """UPDATE users SET 
                firstname = ?, 
                middlename = ?, 
                lastname = ?, 
                course = ?, 
                year_level = ?, 
                email_address = ?, 
                address = ?, 
                profile_picture = ? 
            WHERE username = ?"""
    
    return postprocess(sql, (firstname, middlename, lastname, course, year_level, 
                             email_address, address, profile_picture, username))


