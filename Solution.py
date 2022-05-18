from typing import List
import Utility.DBConnector as Connector
from Utility.DBConnector import ResultSet
from Utility.Status import Status
from Utility.Exceptions import DatabaseException
from Business.File import File
from Business.RAM import RAM
from Business.Disk import Disk
from psycopg2 import sql


# Tables:
# Files: file_id, type, size
# Disks: disk_id, company, speed, free_space, cost
# RAMs: ram_id, size, company
# FilesInDisks: file_id, disk_id
# RAMsInDisks: ram_id, disk_id


def createTables():
    create_files_table_query = "CREATE TABLE Files (" \
                               "file_id INTEGER PRIMARY KEY, " \
                               "type TEXT NOT NULL, " \
                               "size INTEGER NOT NULL, " \
                               "CHECK (file_id > 0), " \
                               "CHECK (size >= 0)" \
                               ");"
    create_disks_table_query = "CREATE TABLE Disks (" \
                               "disk_id INTEGER PRIMARY KEY, " \
                               "company TEXT NOT NULL, " \
                               "speed INTEGER NOT NULL, " \
                               "free_space INTEGER NOT NULL, " \
                               "cost INTEGER NOT NULL, " \
                               "CHECK (disk_id > 0), " \
                               "CHECK (speed > 0), " \
                               "CHECK (cost > 0), " \
                               "CHECK (free_space >= 0)" \
                               ");"
    create_ram_table_query = "CREATE TABLE RAMs (" \
                             "ram_id INTEGER PRIMARY KEY, " \
                             "size INTEGER NOT NULL, " \
                             "company TEXT NOT NULL, " \
                             "CHECK (ram_id > 0), " \
                             "CHECK (size > 0)" \
                             ");"
    create_files_in_disks_table_query = "CREATE TABLE FilesInDisks (" \
                                        "file_id INTEGER, " \
                                        "disk_id INTEGER, " \
                                        "FOREIGN KEY (file_id) REFERENCES Files(file_id) ON DELETE CASCADE, " \
                                        "FOREIGN KEY (disk_id) REFERENCES Disks(disk_id) ON DELETE CASCADE" \
                                        ");"
    create_rams_in_disks_table_query = "CREATE TABLE RAMsInDisks (" \
                                       "ram_id INTEGER, " \
                                       "disk_id INTEGER, " \
                                       "FOREIGN KEY (ram_id) REFERENCES RAMs(ram_id) ON DELETE CASCADE, " \
                                       "FOREIGN KEY (disk_id) REFERENCES Disks(disk_id) ON DELETE CASCADE" \
                                       ");"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(f"BEGIN; "
                        f"{create_files_table_query} "
                        f"{create_disks_table_query} "
                        f"{create_ram_table_query} "
                        f"{create_files_in_disks_table_query} "
                        f"{create_rams_in_disks_table_query} "
                        f"COMMIT;")
        conn.execute(query)
    except DatabaseException:
        conn.rollback()
        return Status.ERROR
    finally:
        if conn:
            conn.close()
        return Status.OK


def clearTables():
    clear_files_table_query = "DELETE FROM Files;"
    clear_disks_table_query = "DELETE FROM Disks;"
    clear_ram_table_query = "DELETE FROM RAMs;"
    clear_files_in_disks_table_query = "DELETE FROM FilesInDisks;"
    clear_rams_in_disks_table_query = "DELETE FROM RAMsInDisks;"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(f"BEGIN; "
                        f"{clear_files_table_query} "
                        f"{clear_disks_table_query} "
                        f"{clear_ram_table_query} "
                        f"{clear_files_in_disks_table_query} "
                        f"{clear_rams_in_disks_table_query} "
                        f"COMMIT;")
        conn.execute(query)
    except DatabaseException:
        conn.rollback()
        return Status.ERROR
    finally:
        if conn:
            conn.close()
        return Status.OK


def dropTables():
    drop_files_table_query = "DROP TABLE Files;"
    drop_disks_table_query = "DROP TABLE Disks;"
    drop_ram_table_query = "DROP TABLE RAMs;"
    drop_files_in_disks_table_query = "DROP TABLE FilesInDisks;"
    drop_rams_in_disks_table_query = "DROP TABLE RAMsInDisks;"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(f"BEGIN; "
                        f"{drop_files_table_query} "
                        f"{drop_disks_table_query} "
                        f"{drop_ram_table_query} "
                        f"{drop_files_in_disks_table_query} "
                        f"{drop_rams_in_disks_table_query} "
                        f"COMMIT;")
        conn.execute(query)
    except DatabaseException:
        conn.rollback()
        return Status.ERROR
    finally:
        if conn:
            conn.close()
        return Status.OK


def addFile(file: File) -> Status:
    return Status.OK


def getFileByID(fileID: int) -> File:
    return File()


def deleteFile(file: File) -> Status:
    return Status.OK


def addDisk(disk: Disk) -> Status:
    return Status.OK


def getDiskByID(diskID: int) -> Disk:
    return Disk()


def deleteDisk(diskID: int) -> Status:
    return Status.OK


def addRAM(ram: RAM) -> Status:
    return Status.OK


def getRAMByID(ramID: int) -> RAM:
    return RAM()


def deleteRAM(ramID: int) -> Status:
    return Status.OK


def addDiskAndFile(disk: Disk, file: File) -> Status:
    return Status.OK


def addFileToDisk(file: File, diskID: int) -> Status:
    return Status.OK


def removeFileFromDisk(file: File, diskID: int) -> Status:
    return Status.OK


def addRAMToDisk(ramID: int, diskID: int) -> Status:
    return Status.OK


def removeRAMFromDisk(ramID: int, diskID: int) -> Status:
    return Status.OK


def averageFileSizeOnDisk(diskID: int) -> float:
    return 0


def diskTotalRAM(diskID: int) -> int:
    return 0


def getCostForType(type: str) -> int:
    return 0


def getFilesCanBeAddedToDisk(diskID: int) -> List[int]:
    return []


def getFilesCanBeAddedToDiskAndRAM(diskID: int) -> List[int]:
    return []


def isCompanyExclusive(diskID: int) -> bool:
    return True


def getConflictingDisks() -> List[int]:
    return []


def mostAvailableDisks() -> List[int]:
    return []


def getCloseFiles(fileID: int) -> List[int]:
    return []


def main():
    assert(createTables() == Status.OK)
    assert(clearTables() == Status.OK)
    assert(dropTables() == Status.OK)


if __name__ == "__main__":
    main()
