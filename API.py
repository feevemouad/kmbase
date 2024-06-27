import requests

class API:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.base_headers = {"token": f"{token}"}

    # User-related methods
    def get_all_users(self):
        try:
            response = requests.get(f"{self.base_url}/users", headers=self.base_headers)
            return response.json()
        except:
            return None

    def create_user(self, username, first_name, last_name, password, email, role):
        try:
            data = {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "password": password,
                "email": email,
                "role": role
            }
            response = requests.post(f"{self.base_url}/users", json=data, headers=self.base_headers)
            return response.json()
        except:
            return None

    def get_user(self, user_id):
        try:
            response = requests.get(f"{self.base_url}/users/{user_id}", headers=self.base_headers)
            return response.json()
        except:
            return None

    def get_user_by_username(self, username):
        try:
            response = requests.get(f"{self.base_url}/users/{username}", headers=self.base_headers)
            return response.json()
        except :
            return None


    def update_user(self, user_id, data):
        try:
            response = requests.put(f"{self.base_url}/users/{user_id}", json=data, headers=self.base_headers)
            return response.json()
        except:
            return None

    def delete_user(self, user_id):
        try:
            response = requests.delete(f"{self.base_url}/users/{user_id}", headers=self.base_headers)
            return response.json()
        except:
            return None

    # PDF-related methods
    def get_all_pdfs(self):
        try:
            response = requests.get(f"{self.base_url}/pdfs", headers=self.base_headers)
            return response.json()
        except:
            return None

    def upload_pdf(self, user_id, file_name, file_path):
        try:
            data = {
                "user_id": user_id,
                "file_name": file_name,
                "file_path": file_path
            }
            response = requests.post(f"{self.base_url}/pdfs", json=data, headers=self.base_headers)
            return response.json()
        except:
            return None

    def get_pdf(self, pdf_id):
        try:
            response = requests.get(f"{self.base_url}/pdfs/{pdf_id}", headers=self.base_headers)
            return response.json()
        except:
            return None

    def add_pdf_metadata(self, pdf_id, description, file_size):
        try:
            data = {
                "description": description,
                "file_size": file_size
            }
            response = requests.post(f"{self.base_url}/pdfs/{pdf_id}/metadata", json=data, headers=self.base_headers)
            return response.json()
        except:
            return None

    def get_pdf_metadata(self, pdf_id):
        try:
            response = requests.get(f"{self.base_url}/pdfs/{pdf_id}/metadata", headers=self.base_headers)
            return response.json()
        except:
            return None

    def delete_pdf(self, pdf_id):
        try:
            response = requests.delete(f"{self.base_url}/pdfs/{pdf_id}", headers=self.base_headers)
            return response.json()
        except:
            return None

    # You can add authentication methods here if needed, similar to your example
    def login(self, username, password):
        try:
            response = requests.post(f"{self.base_url}/auth/login", json={
                "username": username,
                "password": password
            })
            body = response.json()
            token = body.get("token") if isinstance(body, dict) else None
            return token
        except:
            return None
        
    def register(self, username, password, first_name, last_name, email, role ):
        try:
            response = requests.post(f"{self.base_url}/auth/register", json={
                "username": username,
                "password": password
            })
            body = response.json()
            token = body.get("token") if isinstance(body, dict) else None
            return token
        except:
            return None

    def is_logged_in(self):
        try:
            response = requests.get(f"{self.base_url}/auth/is_logged_in", headers=self.base_headers)
            return response.status_code == 201
        except:
            return False