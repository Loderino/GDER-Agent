from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload
from agent.GD import SCOPES
from agent.constants import GD_CREDENTIALS_FILE, AUTH_DATA_DIR
import pandas as pd
import json
from agent.exceptions import GoogleDriveAuthError

class GDRequestor:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._creds = None
            try:
                with open(GD_CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                    info = json.load(f)
                if "installed" in info:
                    self._auth(use_cache=True)
                else:
                    self._auth_from_service_account()
                self._service = build('drive', 'v3', credentials=self._creds)
            except FileNotFoundError as exc:
                raise GoogleDriveAuthError(f"Credentials file not found by path {GD_CREDENTIALS_FILE}") from exc
            except Exception as exc:
                raise GoogleDriveAuthError(str(exc)) from exc

    def _auth(self, use_cache=True):
        if use_cache and (AUTH_DATA_DIR / "token.json").exists():
            self._creds = Credentials.from_authorized_user_file(AUTH_DATA_DIR / "token.json", SCOPES)
        if not self._creds or not self._creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(GD_CREDENTIALS_FILE, SCOPES)
            self._creds = flow.run_local_server(port=0)
            with open(AUTH_DATA_DIR / 'token.json', 'w', encoding="utf-8") as token:
                token.write(self._creds.to_json())
    
    def _auth_from_service_account(self):
        self._creds = service_account.Credentials.from_service_account_file(GD_CREDENTIALS_FILE, scopes=SCOPES)

    def list_files(self):
        query = "mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or " \
            "mimeType='application/vnd.ms-excel'"# or mimeType='application/vnd.google-apps.spreadsheet'"
        results = self._service.files().list(
            q=query,
            spaces='drive',
            fields="files(id, name)",
            pageSize=1000
        ).execute()
        files = results.get('files', [])
        return files
    
    def read_excel(self, file_id):
        """
        Читает Excel-файл с Google Drive и возвращает данные в виде DataFrame

        Args:
            file_id (str): ID файла на Google Drive

        Returns:
            pandas.DataFrame: Данные из Excel-файла
        """
        #if self._servise.files().get(fileId=file_id).execute()['mimeType'] != "application/vnd.google-apps.spreadsheet":

        request = self._service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        file_content.seek(0)
        df = pd.read_excel(file_content)
        print(df.head())
        return df.to_dict(orient='records')

if __name__ == "__main__":
    a = GDRequestor()
    a.read_excel(a.list_files()[0]["id"])