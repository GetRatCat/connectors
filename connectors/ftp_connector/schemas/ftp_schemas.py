from dataclasses import dataclass

from connectors.base.schemas import BaseFile


@dataclass
class FTPFile(BaseFile):
    ...