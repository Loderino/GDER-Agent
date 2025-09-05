import io
import json
import pandas as pd
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from agent.constants import GD_CREDENTIALS_FILE, AUTH_DATA_DIR
from agent.exceptions import GoogleDriveAuthError, GoogleDriveError
from agent.GD import SCOPES


class GDRequestor:
    """
    A singleton class to interact with Google drive.
    """
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
            except AttributeError as exc:
                raise GoogleDriveAuthError("Timeout for authorize pass.") from exc
            except Exception as exc:
                raise GoogleDriveAuthError(str(exc)) from exc

    def _auth(self, use_cache: bool = True) -> None:
        """
        Makes connection with Google drive with credentials file.

        Args:
            use_cache (bool): If True it will be use cached token after interactive authentication.
        """
        if use_cache and (AUTH_DATA_DIR / "token.json").exists():
            self._creds = Credentials.from_authorized_user_file(AUTH_DATA_DIR / "token.json", SCOPES)
        if not self._creds or not self._creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(GD_CREDENTIALS_FILE, SCOPES)
            self._creds = flow.run_local_server(port=0, timeout_seconds=5)
            with open(AUTH_DATA_DIR / 'token.json', 'w', encoding="utf-8") as token:
                token.write(self._creds.to_json())
    
    def _auth_from_service_account(self) -> None:
        """
        Makes connection with Google drive with service account file.
        """
        self._creds = service_account.Credentials.from_service_account_file(GD_CREDENTIALS_FILE, scopes=SCOPES)

    def list_files(self) -> list[dict]:
        """
        Search a excel files on the Google Drive.

        Returns:
            list[dict]: List of dicts with files info im format `{"id: file_id, "name": file_name}`

        Raises:
            GoogleDriveError: if problem with google drive connection.
        """
        return [{"id": "file1", "name": "Новая таблица.xlsx"}]
        query = "mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or " \
            "mimeType='application/vnd.ms-excel'"# or mimeType='application/vnd.google-apps.spreadsheet'"
        try:
            results = self._service.files().list(
                q=query,
                spaces='drive',
                fields="files(id, name)",
                pageSize=1000
            ).execute()
            files = results.get('files', [])
            return files
        except Exception as exc:
            raise GoogleDriveError(str(exc)) from exc
    
    def read_excel(self, file_id: str) -> dict:
        """
        Reads an excel file from Google drive

        Args:
            file_id (str): file id on Google Drive

        Returns:
            dict: the data from Excel file

        Raises:
            GoogleDriveError: if problem with google drive connection.
        """
        #if self._servise.files().get(fileId=file_id).execute()['mimeType'] != "application/vnd.google-apps.spreadsheet":

        try:
            request = self._service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        except Exception as exc:
            raise GoogleDriveError(str(exc)) from exc
        file_content.seek(0)
        df = pd.read_excel(file_content)
        print(df.head())
        return df.to_dict(orient='records')

if __name__ == "__main__":
    a = GDRequestor()
    a.read_excel(a.list_files()[0]["id"])