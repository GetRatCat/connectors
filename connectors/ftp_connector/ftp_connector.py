import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from ftplib import FTP
from typing import IO

from connectors.base import BaseConnector

from connectors.ftp_connector.schemas import FTPFile


class FTPConnector(BaseConnector):

    def __init__(self, timeout: float = 10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = FTP(
            host=self._host,
            user=self._username,
            passwd=self._password,
            timeout=timeout,
        )
        self.conn.encoding = "latin-1"

    def connect(self):
        assert self.conn.connect(host=self._host, port=self._port)
        self.conn.login(user=self._username, passwd=self._password)

    def delete_file(self, filename: str) -> str:
        return self.conn.delete(filename=filename)

    def delete_files_by_extension(self, extension: str, dirname: str = ""):
        files = [file for file in self.get_all_files(dirname) if file.name.endswith(extension)]
        for file in files:
            self.delete_file(file.name)

    @contextmanager
    def get_file(self, filename: str) -> Iterator[IO[bytes]]:
        file_obj = tempfile.NamedTemporaryFile()
        try:

            def callback(data):
                file_obj.write(data)

            self.conn.retrbinary(cmd=f"RETR {filename}", callback=callback)
            yield file_obj.file
        finally:
            file_obj.close()

    def get_all_files(self, dirname: str = "") -> list[FTPFile]:
        return [FTPFile(name=file) for file in self.conn.nlst(dirname)]

    def upload_file(self, filename: str, file: IO[bytes]):
        return self.conn.storbinary(cmd=f"STOR {filename}", fp=file)
