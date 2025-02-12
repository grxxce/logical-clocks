import sqlite3


class DatabaseManager:
    @staticmethod
    def get_contacts():
        """Register a new user."""
        print("IN GET CONTACTS")
        try:
            with sqlite3.connect('users.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT username FROM users')
                results = cursor.fetchall()
                usernames = []
                for row in results:
                    usernames.append(row[0])
                print(usernames)
                return usernames
        # except sqlite3.IntegrityError:
        #     return "ERROR§Username already exists"
        except Exception as e:
            print(f"ERROR§Fetching contacts failed: {str(e)}")
            return f"ERROR§Fetching contacts failed: {str(e)}"

    # @staticmethod
    def get_limits(username):
        print("IN GET CONTACTS")
        try:
            with sqlite3.connect('users.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT username FROM users')
                results = cursor.fetchall()
                usernames = []
                for row in results:
                    usernames.append(row[0])
                print(usernames)
                return usernames
        # except sqlite3.IntegrityError:
        #     return "ERROR§Username already exists"
        except Exception as e:
            print(f"ERROR§Fetching contacts failed: {str(e)}")
            return f"ERROR§Fetching contacts failed: {str(e)}"
