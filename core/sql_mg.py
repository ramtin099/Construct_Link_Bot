import mysql.connector


class SQL:
    def __init__(self, host, user, password, database):
        self.db_config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.connect_db()

    def connect_db(self):
        try:
            self.con = mysql.connector.connect(**self.db_config)
            self.cursor = self.con.cursor()
            print("MySQL is connected.")
        except mysql.connector.Error as err:
            print(f"Error1: {err}")
            self.con = None
            self.cursor = None

    def close_db(self):
        """This method closes the database connection properly."""
        if self.cursor:
            self.cursor.close()
        if self.con:
            self.con.close()
        print("MySQL connection closed.")

    def check_user_auth(self, userid):
        data = (userid, )
        query = "SELECT * FROM Authentication WHERE user_id = %s"
        self.cursor.execute(query, data)
        user = self.cursor.fetchone()
        print(user)
        return user

    def insert_into_auth_table(self, userid, phone_number, first_name, last_name, company_name, license_number, user_type):
        data = (userid, phone_number, first_name, last_name, company_name, license_number, user_type)
        query = """
            INSERT INTO Authentication (user_id, phone_number, first_name, last_name, company_name, license_number, user_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        try:
            self.cursor.execute(query, data)
            self.con.commit()
            print("User added successfully.")
        except mysql.connector.Error as err:
            print(f"Error2: {err}")
        else:
            print("User already exists.")

    def consume_unread_results(self):
        # Consume any unread results
        while self.cursor.nextset():
            pass
    def show_all_new_users(self):
        if not self.con or not self.cursor:
            print("No active connection to the database.")
            return []

        query = ("SELECT user_id, phone_number, first_name, last_name, "
                 "company_name, license_number, user_type "
                 "FROM Authentication WHERE auth = 'pending';")

        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(f"Error fetching results: {err}")
            return []
    def reject(self, user_id):
        if not self.con or not self.cursor:
            print("No active connection to the database.")
            return
        data = (user_id,)

        query = """
            UPDATE Authentication
            SET auth = 'rejected'
            WHERE user_id = %s;
            """
        try:
            self.cursor.execute(query, data)
            self.con.commit()
            print("Authentication rejected successfully.")
        except mysql.connector.Error as err:
            print(f"Error3: {err}")

    def accept(self, user_id):
        if not self.con or not self.cursor:
            print("No active connection to the database.")
            return

        # بستن هر نتیجه‌ای که از قبل باز مانده
        try:
            while self.cursor.nextset():
                pass
        except mysql.connector.Error as err:
            print(f"Error while clearing results: {err}")

        data = (user_id,)
        query = """
            UPDATE Authentication
            SET auth = 'approved'
            WHERE user_id = %s;
            """
        try:
            self.cursor.execute(query, data)
            self.con.commit()
            print("Authentication accepted successfully.")
        except mysql.connector.Error as err:
            print(f"Error4: {err}")

    def check_user_auth_status(self, user_id):
        query = "SELECT auth FROM Authentication WHERE user_id = %s"
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def check_phone_duplicate(self, phone_number):
        self.consume_unread_results()
        query = "SELECT auth FROM Authentication WHERE phone_number = %s"

        try:
            self.cursor.execute(query, (phone_number,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(f"Error checking phone number: {err}")
            return None

    def insert_into_demand_table(self, user_id, material_type, total_floors, underground_floors, surface_area,
                                 total_building_area, location, proposed_price, approximate_address):
        if not self.con or not self.cursor:
            print("No active connection to the database.")
            return

        query = """
            INSERT INTO demands (user_id, material_type, total_floors, underground_floors,
             surface_area, total_building_area, location, proposed_price, approximate_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        data = (user_id, material_type, total_floors, underground_floors, surface_area, total_building_area, location,
                proposed_price, approximate_address)

        try:
            self.cursor.execute(query, data)
            self.con.commit()
            print("Demand request inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def get_demands(self):
        if not self.con or not self.cursor:
            print("No active connection to the database.")
            return []

        query = "SELECT * FROM demands;"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error retrieving demands: {err}")
            return []

    def insert_into_offers(self, user_id, material_type, license_level, location):
        if not self.con or not self.cursor:
            print("No active connection to the database.")
            return

        data = (user_id, material_type, license_level, location)
        query = """
            INSERT INTO offers (user_id, material_type, license_level, location)
            VALUES (%s, %s, %s, %s);
        """
        try:
            self.cursor.execute(query, data)
            self.con.commit()
            print("Offer inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error inserting offer: {err}")

    def get_filtered_requests(self, request_type, material_type, location):
        try:
            table_name = request_type
            query = f"""
                    SELECT {table_name}.*, 
                           auth.first_name, 
                           auth.last_name, 
                           auth.phone_number, 
                           auth.company_name
                    FROM {table_name}
                    JOIN Authentication auth 
                    ON {table_name}.user_id = auth.user_id
                    WHERE {table_name}.material_type = %s
                    AND {table_name}.location = %s
                    """

            self.cursor.execute(query, (material_type, location))

            result = self.cursor.fetchall()

            return result

        except Exception as e:
            print(f"Error fetching filtered requests: {e}")
            return None

    def delete_requests(self, id, table_name):

        data = (id,)
        query =f"""
        DELETE FROM {table_name} WHERE id = %s
        """
        try:
            self.cursor.execute(query, data)
            self.con.commit()
            print(f"{table_name} deleted id={id} successfully.")
        except mysql.connector.Error as err:
            print(f"Error deleting data id={id}: {err}")

    def get_offer_details_offer(self, selected_offer_id):

        query = "SELECT * FROM offers WHERE id = %s"

        try:
            self.cursor.fetchall()
            self.cursor.execute(query, (selected_offer_id, ))
            print(f"offers get detailed id={selected_offer_id} successfully.")
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(f"Error data id={selected_offer_id}: {err}")

    def get_offer_details_demand(self, selected_offer_id):

        query = "SELECT * FROM demands WHERE id = %s"
        try:
            self.cursor.fetchall()
            self.cursor.execute(query, (selected_offer_id, ))
            print(f"offers get detailed id={selected_offer_id} successfully.")
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(f"Error data id={selected_offer_id}: {err}")
