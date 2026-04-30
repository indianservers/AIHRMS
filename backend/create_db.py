import pymysql

def create_database():
    try:
        connection = pymysql.connect(host='localhost', user='root', password='123456')
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS `AI-HRMS`")
        connection.commit()
        print("Database 'AI-HRMS' created successfully.")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

if __name__ == "__main__":
    create_database()
