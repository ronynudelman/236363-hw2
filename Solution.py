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
                               "file_id INTEGER, " \
                               "type TEXT NOT NULL, " \
                               "size INTEGER NOT NULL, " \
                               "PRIMARY KEY (file_id), " \
                               "CHECK (file_id > 0), " \
                               "CHECK (size >= 0)" \
                               ");"
    create_disks_table_query = "CREATE TABLE Disks (" \
                               "disk_id INTEGER, " \
                               "company TEXT NOT NULL, " \
                               "speed INTEGER NOT NULL, " \
                               "free_space INTEGER NOT NULL, " \
                               "cost INTEGER NOT NULL, " \
                               "PRIMARY KEY (disk_id), " \
                               "CHECK (disk_id > 0), " \
                               "CHECK (speed > 0), " \
                               "CHECK (cost > 0), " \
                               "CHECK (free_space >= 0)" \
                               ");"
    create_ram_table_query = "CREATE TABLE RAMs (" \
                             "ram_id INTEGER, " \
                             "size INTEGER NOT NULL, " \
                             "company TEXT NOT NULL, " \
                             "PRIMARY KEY (ram_id), " \
                             "CHECK (ram_id > 0), " \
                             "CHECK (size > 0)" \
                             ");"
    create_files_in_disks_table_query = "CREATE TABLE FilesInDisks (" \
                                        "file_id INTEGER, " \
                                        "disk_id INTEGER, " \
                                        "FOREIGN KEY (file_id) REFERENCES Files(file_id) ON DELETE CASCADE, " \
                                        "FOREIGN KEY (disk_id) REFERENCES Disks(disk_id) ON DELETE CASCADE, " \
                                        "UNIQUE (file_id, disk_id)" \
                                        ");"
    create_rams_in_disks_table_query = "CREATE TABLE RAMsInDisks (" \
                                       "ram_id INTEGER, " \
                                       "disk_id INTEGER, " \
                                       "FOREIGN KEY (ram_id) REFERENCES RAMs(ram_id) ON DELETE CASCADE, " \
                                       "FOREIGN KEY (disk_id) REFERENCES Disks(disk_id) ON DELETE CASCADE, " \
                                       "UNIQUE (ram_id, disk_id)" \
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
                        f"{clear_files_in_disks_table_query} "
                        f"{clear_rams_in_disks_table_query} "
                        f"{clear_files_table_query} "
                        f"{clear_disks_table_query} "
                        f"{clear_ram_table_query} "
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
                        f"{drop_files_in_disks_table_query} "
                        f"{drop_rams_in_disks_table_query} "
                        f"{drop_files_table_query} "
                        f"{drop_disks_table_query} "
                        f"{drop_ram_table_query} "
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
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(f"INSERT INTO Files VALUES ({file.getFileID()}, '{file.getType()}', {file.getSize()});")
        conn.commit()
    except DatabaseException.NOT_NULL_VIOLATION:
        return Status.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION:
        return Status.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION:
        return Status.ALREADY_EXISTS
    except DatabaseException.ConnectionInvalid:
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def getFileByID(fileID: int) -> File:
    conn = None
    try:
        conn = Connector.DBConnector()
        rows_effected, result = conn.execute(f"SELECT * FROM Files WHERE file_id = {fileID};")
        conn.commit()
    except DatabaseException:
        return File.badFile()
    finally:
        if conn:
            conn.close()
    if not result.isEmpty():
        assert rows_effected == 1
        row = result[0]
        return File(row["file_id"], row["type"], row["size"])
    return File.badFile()


def deleteFile(file: File) -> Status:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(f"DELETE FROM Files "
                     f"WHERE "
                     f"file_id = {file.getFileID()} "
                     f"AND "
                     f"type = '{file.getType()}' "
                     f"AND "
                     f"size = {file.getSize()}"
                     f";")
        conn.commit()
    except DatabaseException:
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def addDisk(disk: Disk) -> Status:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(f"INSERT INTO Disks VALUES ({disk.getDiskID()}, '{disk.getCompany()}', "
                     f"{disk.getSpeed()}, {disk.getFreeSpace()}, {disk.getCost()});")
        conn.commit()
    except DatabaseException.NOT_NULL_VIOLATION:
        return Status.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION:
        return Status.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION:
        return Status.ALREADY_EXISTS
    except DatabaseException.ConnectionInvalid:
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def getDiskByID(diskID: int) -> Disk:
    conn = None
    try:
        conn = Connector.DBConnector()
        rows_effected, result = conn.execute(f"SELECT * FROM Disks WHERE disk_id = {diskID};")
        conn.commit()
    except DatabaseException:
        return Disk.badDisk()
    finally:
        if conn:
            conn.close()
    if not result.isEmpty():
        assert rows_effected == 1
        row = result[0]
        return Disk(row["disk_id"], row["company"], row["speed"], row["free_space"], row["cost"])
    return Disk.badDisk()


def deleteDisk(diskID: int) -> Status:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(f"DELETE FROM Disks WHERE disk_id = {diskID};")
        conn.commit()
    except DatabaseException:
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def addRAM(ram: RAM) -> Status:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(f"INSERT INTO RAMs VALUES ({ram.getRamID()}, {ram.getSize()}, '{ram.getCompany()}');")
        conn.commit()
    except DatabaseException.NOT_NULL_VIOLATION:
        return Status.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION:
        return Status.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION:
        return Status.ALREADY_EXISTS
    except DatabaseException.ConnectionInvalid:
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def getRAMByID(ramID: int) -> RAM:
    conn = None
    try:
        conn = Connector.DBConnector()
        rows_effected, result = conn.execute(f"SELECT * FROM RAMs WHERE ram_id = {ramID};")
        conn.commit()
    except DatabaseException:
        return RAM.badRAM()
    finally:
        if conn:
            conn.close()
    if not result.isEmpty():
        assert rows_effected == 1
        row = result[0]
        return RAM(row["ram_id"], row["size"], row["company"])
    return RAM.badRAM()


def deleteRAM(ramID: int) -> Status:
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(f"DELETE FROM RAMs WHERE ram_id = {ramID};")
        conn.commit()
    except DatabaseException:
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def addDiskAndFile(disk: Disk, file: File) -> Status:
    conn = None
    try:
        conn = Connector.DBConnector()
        add_file = f"INSERT INTO Files VALUES ({file.getFileID()}, '{file.getType()}', {file.getSize()});"
        add_disk = f"INSERT INTO Disks VALUES ({disk.getDiskID()}, '{disk.getCompany()}', " \
                   f"{disk.getSpeed()}, {disk.getFreeSpace()}, {disk.getCost()});"
        query = sql.SQL(f"BEGIN; "
                        f"{add_disk} "
                        f"{add_file} "
                        f"COMMIT;")
        conn.execute(query)
    except DatabaseException.NOT_NULL_VIOLATION:
        conn.rollback()
        return Status.BAD_PARAMS
    except DatabaseException.CHECK_VIOLATION:
        conn.rollback()
        return Status.BAD_PARAMS
    except DatabaseException.UNIQUE_VIOLATION:
        conn.rollback()
        return Status.ALREADY_EXISTS
    except DatabaseException.ConnectionInvalid:
        conn.rollback()
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def addFileToDisk(file: File, diskID: int) -> Status:
    insert_file_to_disk_query = f"INSERT INTO FilesInDisks VALUES ({file.getFileID()}, {diskID});"
    update_free_space_query = f"UPDATE Disks " \
                              f"SET free_space = free_space - {file.getSize()} " \
                              f"WHERE disk_id = {diskID}" \
                              f";"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(f"BEGIN; "
                        f"{insert_file_to_disk_query} "
                        f"{update_free_space_query} "
                        f"COMMIT;")
        conn.execute(query)
    except DatabaseException.FOREIGN_KEY_VIOLATION:
        conn.rollback()
        return Status.NOT_EXISTS
    except DatabaseException.UNIQUE_VIOLATION:
        conn.rollback()
        return Status.ALREADY_EXISTS
    except DatabaseException.CHECK_VIOLATION:
        conn.rollback()
        return Status.BAD_PARAMS
    except DatabaseException.ConnectionInvalid:
        conn.rollback()
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def removeFileFromDisk(file: File, diskID: int) -> Status:
    remove_file_from_disk_query = f"DELETE FROM FilesInDisks WHERE file_id = {file.getFileID()} AND disk_id = {diskID};"
    update_free_space_query = f"UPDATE Disks " \
                              f"SET free_space = free_space + {file.getSize()} " \
                              f"WHERE disk_id = {diskID} AND EXISTS (SELECT * FROM FilesInDisks WHERE " \
                              f"file_id = {file.getFileID()} AND disk_id = {diskID})" \
                              f";"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(f"BEGIN; "
                        f"{update_free_space_query} "
                        f"{remove_file_from_disk_query} "
                        f"COMMIT;")
        conn.execute(query)
    except DatabaseException:
        conn.rollback()
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def addRAMToDisk(ramID: int, diskID: int) -> Status:
    insert_file_to_disk_query = f"INSERT INTO RAMsInDisks VALUES ({ramID}, {diskID});"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(f"BEGIN; "
                        f"{insert_file_to_disk_query} "
                        f"COMMIT;")
        conn.execute(query)
    except DatabaseException.FOREIGN_KEY_VIOLATION:
        conn.rollback()
        return Status.NOT_EXISTS
    except DatabaseException.UNIQUE_VIOLATION:
        conn.rollback()
        return Status.ALREADY_EXISTS
    except DatabaseException.ConnectionInvalid:
        conn.rollback()
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def removeRAMFromDisk(ramID: int, diskID: int) -> Status:
    conn = None
    try:
        conn = Connector.DBConnector()
        rows_effected, _ = conn.execute(f"DELETE FROM RAMsInDisks WHERE ram_id = {ramID} AND disk_id = {diskID};")
        conn.commit()
    except DatabaseException:
        conn.rollback()
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    if rows_effected == 0:
        return Status.NOT_EXISTS
    return Status.OK


def averageFileSizeOnDisk(diskID: int) -> float:
    conn = None
    try:
        conn = Connector.DBConnector()
        files_on_disk = f"SELECT file_id FROM FilesInDisks WHERE disk_id = {diskID}"
        rows_affected, result = conn.execute(f"SELECT AVG(size) FROM Files WHERE file_id IN ({files_on_disk})")
        conn.commit()
    except DatabaseException:
        return -1.0
    finally:
        if conn:
            conn.close()
    assert result.size() == 1
    row = result[0]
    if row['avg'] is None:
        return 0.0
    return row['avg']


def diskTotalRAM(diskID: int) -> int:
    conn = None
    try:
        conn = Connector.DBConnector()
        ram_on_disk = f"SELECT ram_id FROM RAMsInDisks WHERE disk_id = {diskID}"
        rows_affected, result = conn.execute(f"SELECT SUM(size) FROM RAMs WHERE ram_id IN ({ram_on_disk})")
        conn.commit()
    except DatabaseException:
        return -1
    finally:
        if conn:
            conn.close()
    assert result.size() == 1
    row = result[0]
    if row['sum'] is None:
        return 0
    return row['sum']


def getCostForType(type: str) -> int:
    conn = None
    try:
        conn = Connector.DBConnector()
        rows_affected, result = conn.execute(f"SELECT SUM(F.size * D.cost) "
                                             f"FROM Files F, Disks D, FilesInDisks FD "
                                             f"WHERE "
                                             f"F.type = '{type}' "
                                             f"AND "
                                             f"F.file_id = FD.file_id "
                                             f"AND "
                                             f"D.disk_id = FD.disk_id"
                                             f";")
        conn.commit()
    except DatabaseException:
        return -1
    finally:
        if conn:
            conn.close()
    assert result.size() == 1
    row = result[0]
    if row['sum'] is None:
        return 0
    return row['sum']


def getFilesCanBeAddedToDisk(diskID: int) -> List[int]:
    conn = None
    try:
        conn = Connector.DBConnector()
        disk_size = f"SELECT free_space FROM Disks WHERE disk_id = {diskID}"
        rows_affected, result = conn.execute(f"SELECT file_id FROM Files WHERE size <= ({disk_size}) "
                                             f"ORDER BY file_id ASC "
                                             f"LIMIT 5"
                                             f";")
        conn.commit()
    except DatabaseException:
        return []
    finally:
        if conn:
            conn.close()
    list_res = []
    for i in range(result.size()):
        row = result[i]
        list_res.append(row['file_id'])
    return list_res


def getFilesCanBeAddedToDiskAndRAM(diskID: int) -> List[int]:
    conn = None
    try:
        conn = Connector.DBConnector()
        disk_size = f"SELECT free_space FROM Disks WHERE disk_id = {diskID}"
        rams_in_disk = f"SELECT ram_id FROM RAMsInDisks WHERE disk_id = {diskID}"
        ram_size = f"SELECT SUM(size) FROM RAMs WHERE ram_id IN ({rams_in_disk})"
        rows_affected, result = conn.execute(f"SELECT file_id FROM Files WHERE size <= ({disk_size})"
                                             f"AND size <= ({ram_size}) "
                                             f"ORDER BY file_id ASC "
                                             f"LIMIT 5"
                                             f";")
        conn.commit()
    except DatabaseException:
        return []
    finally:
        if conn:
            conn.close()
    list_res = []
    for i in range(result.size()):
        row = result[i]
        list_res.append(row['file_id'])
    return list_res


def isCompanyExclusive(diskID: int) -> bool:
    return True


def getConflictingDisks() -> List[int]:
    return []


def mostAvailableDisks() -> List[int]:
    return []


def getCloseFiles(fileID: int) -> List[int]:
    return []

