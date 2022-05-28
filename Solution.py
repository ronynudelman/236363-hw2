from typing import List
import Utility.DBConnector as Connector
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
                        f"COMMIT;").format()
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
                        f"COMMIT;").format()
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
                        f"COMMIT;").format()
        conn.execute(query)
    except DatabaseException:
        conn.rollback()
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def addFile(file: File) -> Status:
    add_file_query = "INSERT INTO Files VALUES ({id}, {type}, {size});"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(add_file_query).format(id=sql.Literal(file.getFileID()),
                                               type=sql.Literal(file.getType()),
                                               size=sql.Literal(file.getSize()))
        conn.execute(query)
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
    get_file_query = "SELECT * FROM Files WHERE file_id = {id};"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(get_file_query).format(id=sql.Literal(fileID))
        rows_effected, result = conn.execute(query)
        conn.commit()
    except DatabaseException:
        return File.badFile()
    finally:
        if conn:
            conn.close()
    if not result.isEmpty():
        row = result[0]
        return File(row["file_id"], row["type"], row["size"])
    return File.badFile()


def deleteFile(file: File) -> Status:
    file_to_delete = "SELECT file_id " \
                     "FROM Files " \
                     "WHERE file_id = {id} " \
                     "AND " \
                     "type = {type} " \
                     "AND " \
                     "size = {size}"
    disks_with_file = "SELECT disk_id " \
                      "FROM FilesInDisks " + \
                      f"WHERE file_id IN ({file_to_delete})"
    update_disks_free_space_query = "UPDATE Disks " \
                                    "SET free_space = free_space + {size} " + \
                                    f"WHERE disk_id IN ({disks_with_file})"
    delete_file_query = "DELETE FROM Files " + \
                        f"WHERE file_id IN ({file_to_delete})"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(f"BEGIN; "
                        f"{update_disks_free_space_query}; "
                        f"{delete_file_query}; "
                        f"COMMIT;").format(id=sql.Literal(file.getFileID()),
                                           type=sql.Literal(file.getType()),
                                           size=sql.Literal(file.getSize()))
        conn.execute(query)
    except DatabaseException:
        conn.rollback()
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def addDisk(disk: Disk) -> Status:
    add_disk_query = "INSERT INTO Disks VALUES ({id}, {company}, {speed}, {free_space}, {cost});"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(add_disk_query).format(id=sql.Literal(disk.getDiskID()),
                                               company=sql.Literal(disk.getCompany()),
                                               speed=sql.Literal(disk.getSpeed()),
                                               free_space=sql.Literal(disk.getFreeSpace()),
                                               cost=sql.Literal(disk.getCost()))
        conn.execute(query)
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
    get_disk_query = "SELECT * FROM Disks WHERE disk_id = {id};"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(get_disk_query).format(id=sql.Literal(diskID))
        rows_effected, result = conn.execute(query)
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
    delete_disk_query = "DELETE FROM Disks WHERE disk_id = {id};"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(delete_disk_query).format(id=sql.Literal(diskID))
        conn.execute(query)
        conn.commit()
    except DatabaseException:
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def addRAM(ram: RAM) -> Status:
    add_ram_query = "INSERT INTO RAMs VALUES ({id}, {size}, {company});"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(add_ram_query).format(id=sql.Literal(ram.getRamID()),
                                              size=sql.Literal(ram.getSize()),
                                              company=sql.Literal(ram.getCompany()))
        conn.execute(query)
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
    get_ram_query = "SELECT * FROM RAMs WHERE ram_id = {id};"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(get_ram_query).format(id=sql.Literal(ramID))
        rows_effected, result = conn.execute(query)
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
    delete_ram_query = "DELETE FROM RAMs WHERE ram_id = {id};"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(delete_ram_query).format(id=sql.Literal(ramID))
        conn.execute(query)
        conn.commit()
    except DatabaseException:
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def addDiskAndFile(disk: Disk, file: File) -> Status:
    add_disk_query = "INSERT INTO Disks VALUES (" \
                     "{disk_id}, " \
                     "{disk_company}, " \
                     "{disk_speed}, " \
                     "{disk_free_space}, " \
                     "{disk_cost}" \
                     ")"
    add_file_query = "INSERT INTO Files VALUES (" \
                     "{file_id}, " \
                     "{file_type}, " \
                     "{file_size}" \
                     ")"
    conn = None
    try:
        conn = Connector.DBConnector()

        query = sql.SQL(f"BEGIN; "
                        f"{add_disk_query}; "
                        f"{add_file_query}; "
                        f"COMMIT;").format(disk_id=sql.Literal(disk.getDiskID()),
                                           disk_company=sql.Literal(disk.getCompany()),
                                           disk_speed=sql.Literal(disk.getSpeed()),
                                           disk_free_space=sql.Literal(disk.getFreeSpace()),
                                           disk_cost=sql.Literal(disk.getCost()),
                                           file_id=sql.Literal(file.getFileID()),
                                           file_type=sql.Literal(file.getType()),
                                           file_size=sql.Literal(file.getSize()))
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
    insert_file_to_disk_query = "INSERT INTO FilesInDisks VALUES ({file_id}, {disk_id});"
    update_free_space_query = "UPDATE Disks " \
                              "SET free_space = free_space - {file_size} " \
                              "WHERE disk_id = {disk_id}" \
                              ";"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(f"BEGIN; "
                        f"{insert_file_to_disk_query} "
                        f"{update_free_space_query} "
                        f"COMMIT;").format(file_id=sql.Literal(file.getFileID()),
                                           disk_id=sql.Literal(diskID),
                                           file_size=sql.Literal(file.getSize()))
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
    file_to_delete = "SELECT file_id " \
                     "FROM Files " \
                     "WHERE file_id = {file_id} " \
                     "AND " \
                     "type = {file_type} " \
                     "AND " \
                     "size = {file_size}"
    disk_with_file = "SELECT disk_id " \
                     "FROM FilesInDisks " \
                     "WHERE disk_id = {disk_id} AND file_id IN" + f"({file_to_delete})"
    update_free_space_query = "UPDATE Disks " \
                              "SET free_space = free_space + {file_size} " \
                              "WHERE disk_id IN" + f"({disk_with_file})"
    remove_file_from_disk_query = f"DELETE FROM FilesInDisks WHERE " \
                                  f"file_id IN ({file_to_delete}) AND disk_id IN ({disk_with_file})"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(f"BEGIN; "
                        f"{update_free_space_query}; "
                        f"{remove_file_from_disk_query}; "
                        f"COMMIT;").format(file_id=sql.Literal(file.getFileID()),
                                           file_type=sql.Literal(file.getType()),
                                           file_size=sql.Literal(file.getSize()),
                                           disk_id=sql.Literal(diskID))
        conn.execute(query)
    except DatabaseException:
        conn.rollback()
        return Status.ERROR
    finally:
        if conn:
            conn.close()
    return Status.OK


def addRAMToDisk(ramID: int, diskID: int) -> Status:
    insert_ram_to_disk_query = "INSERT INTO RAMsInDisks VALUES ({ram_id}, {disk_id})"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(f"BEGIN; "
                        f"{insert_ram_to_disk_query}; "
                        f"COMMIT;").format(ram_id=sql.Literal(ramID),
                                           disk_id=sql.Literal(diskID))
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
    remove_ram_from_disk_query = "DELETE FROM RAMsInDisks WHERE ram_id = {ram_id} AND disk_id = {disk_id};"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(remove_ram_from_disk_query).format(ram_id=sql.Literal(ramID),
                                                           disk_id=sql.Literal(diskID))
        rows_effected, _ = conn.execute(query)
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
    files_on_disk = "SELECT file_id FROM FilesInDisks WHERE disk_id = {disk_id}"
    avg_files_size_query = f"SELECT AVG(size) FROM Files WHERE file_id IN ({files_on_disk})"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(avg_files_size_query).format(disk_id=sql.Literal(diskID))
        rows_affected, result = conn.execute(query)
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
    ram_on_disk = "SELECT ram_id FROM RAMsInDisks WHERE disk_id = {disk_id}"
    disk_total_ram_query = f"SELECT SUM(size) FROM RAMs WHERE ram_id IN ({ram_on_disk})"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(disk_total_ram_query).format(disk_id=sql.Literal(diskID))
        rows_affected, result = conn.execute(query)
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
    get_cost_for_type_query = "SELECT SUM(F.size * D.cost) " \
                              "FROM Files F, Disks D, FilesInDisks FD " \
                              "WHERE " \
                              "F.type = {type} " \
                              "AND " \
                              "F.file_id = FD.file_id " \
                              "AND " \
                              "D.disk_id = FD.disk_id" \
                              ";"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(get_cost_for_type_query).format(type=sql.Literal(type))
        rows_affected, result = conn.execute(query)
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
    disk_size = "SELECT free_space FROM Disks WHERE disk_id = {disk_id}"
    get_files_query = f"SELECT file_id " \
                      f"FROM Files " \
                      f"WHERE size <= ({disk_size}) " \
                      f"ORDER BY file_id ASC " \
                      f"LIMIT 5" \
                      f";"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(get_files_query).format(disk_id=sql.Literal(diskID))
        rows_affected, result = conn.execute(query)
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
    disk_size = "SELECT free_space FROM Disks WHERE disk_id = {disk_id}"
    rams_in_disk = "SELECT ram_id FROM RAMsInDisks WHERE disk_id = {disk_id}"
    ram_size = f"SELECT SUM(size) FROM RAMs WHERE ram_id IN ({rams_in_disk})"
    get_files_query = f"SELECT file_id FROM Files WHERE size <= ({disk_size})" \
                      f"AND size <= ({ram_size}) " \
                      f"ORDER BY file_id ASC " \
                      f"LIMIT 5" \
                      f";"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(get_files_query).format(disk_id=sql.Literal(diskID))
        rows_affected, result = conn.execute(query)
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
    rams_on_disk = "SELECT ram_id " \
                   "FROM RAMsInDisks " \
                   "WHERE disk_id = {disk_id}"
    rams_companies = f"SELECT DISTINCT company " \
                     f"FROM RAMs " \
                     f"WHERE ram_id IN ({rams_on_disk})"
    exclusive_comp_query = "SELECT disk_id " \
                           "FROM Disks " \
                           "WHERE disk_id = {disk_id} AND company =ALL " + f"({rams_companies})" + \
                           ";"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(exclusive_comp_query).format(disk_id=sql.Literal(diskID))
        rows_affected, result = conn.execute(query)
        conn.commit()
    except DatabaseException:
        return False
    finally:
        if conn:
            conn.close()
    return not result.isEmpty()


def getConflictingDisks() -> List[int]:
    get_conf_disks_query = f"SELECT DISTINCT FD1.disk_id AS disk_id " \
                           f"FROM FilesInDisks FD1, FilesInDisks FD2 " \
                           f"WHERE FD1.disk_id <> FD2.disk_id " \
                           f"AND FD1.file_id = FD2.file_id " \
                           f"ORDER BY FD1.disk_id ASC;"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(get_conf_disks_query).format()
        rows_affected, result = conn.execute(query)
        conn.commit()
    except DatabaseException:
        return []
    finally:
        if conn:
            conn.close()
    list_res = []
    for i in range(result.size()):
        row = result[i]
        list_res.append(row['disk_id'])
    return list_res


def mostAvailableDisks() -> List[int]:
    most_avail_disks_query = f"SELECT disk_id FROM Disks " \
                             f"ORDER BY free_space DESC, speed DESC, disk_id ASC " \
                             f"LIMIT 5" \
                             f";"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(most_avail_disks_query).format()
        rows_affected, result = conn.execute(query)
        conn.commit()
    except DatabaseException:
        return []
    finally:
        if conn:
            conn.close()
    list_res = []
    for i in range(result.size()):
        row = result[i]
        list_res.append(row['disk_id'])
    return list_res


def getCloseFiles(fileID: int) -> List[int]:
    disks_counter = "SELECT COUNT(disk_id) FROM FilesInDisks WHERE file_id = {file_id}"
    disks_with_file_id = "SELECT disk_id FROM FilesInDisks WHERE file_id = {file_id}"
    close_files_query = "SELECT file_id " \
                        "FROM FilesInDisks " \
                        "WHERE file_id <> {file_id} AND disk_id IN " + f"({disks_with_file_id}) " + \
                        "GROUP BY file_id " \
                        "HAVING COUNT(*) >= " + f"({disks_counter}) " + "/ 2.0 " \
                        "ORDER BY file_id ASC " \
                        "LIMIT 10" \
                        ";"
    conn = None
    try:
        conn = Connector.DBConnector()
        query = sql.SQL(close_files_query).format(file_id=sql.Literal(fileID))
        rows_affected, result = conn.execute(query)
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
