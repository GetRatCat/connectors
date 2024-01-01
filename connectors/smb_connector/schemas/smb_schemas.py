from dataclasses import dataclass

from connectors.base.schemas import BaseFile

@dataclass
class SMBFile(BaseFile):
    is_dir: bool
    read_only: bool