import unittest
from dotenv import load_dotenv
import os
from supabase.client import create_client, Client

class TestMethods(unittest.TestCase):
    def test_db_connection(self):
        load_dotenv()
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

        self.assertIsNotNone(SUPABASE_URL, "SUPABASE_URL is not set in environment")
        self.assertIsNotNone(SUPABASE_KEY, "SUPABASE_KEY is not set in environment")

        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.assertIsInstance(client, Client, "Failed to create a Supabase Client connection")

if __name__ == "__main__":
    unittest.main()

# python3 -m unittest -v