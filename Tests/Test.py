import unittest
import Solution
from Utility.Status import Status
from Tests.abstractTest import AbstractTest
from Business.File import File
from Business.RAM import RAM
from Business.Disk import Disk

'''
    Simple test, create one of your own
    make sure the tests' names start with test_
'''


class Test(AbstractTest):

    def test_files(self) -> None:
        self.assertEqual(Status.OK, Solution.addFile(File(fileID=1, type="jpg", size=2)), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(File(fileID=2, type="jpg", size=4)), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(File(fileID=3, type="pdf", size=10)), "Should work")
        self.assertEqual(Status.ALREADY_EXISTS, Solution.addFile(File(fileID=2, type="pdf", size=5)),
                         "ID 2 already exists")
        self.assertEqual(Status.BAD_PARAMS, Solution.addFile(File(fileID=1, type="pdf", size=-7)),
                         "Size is negative")
        file = Solution.getFileByID(fileID=3)
        assert file.getFileID() == 3
        assert file.getType() == "pdf"
        assert file.getSize() == 10
        file = Solution.getFileByID(fileID=9)
        assert file.getFileID() is None
        assert file.getType() is None
        assert file.getSize() is None
        self.assertEqual(Status.OK, Solution.deleteFile(File(fileID=2, type="jpg", size=4)), "Should work")
        file = Solution.getFileByID(fileID=2)
        assert file.getFileID() is None
        assert file.getType() is None
        assert file.getSize() is None
        self.assertEqual(Status.OK, Solution.clearTables(), "Should work")
        file = Solution.getFileByID(fileID=1)
        assert file.getFileID() is None
        assert file.getType() is None
        assert file.getSize() is None

    def test_disks(self) -> None:
        self.assertEqual(Status.OK, Solution.addDisk(Disk(diskID=1, company="jpg", speed=2, free_space=500, cost=5)),
                         "Should work")
        self.assertEqual(Status.ALREADY_EXISTS,
                         Solution.addDisk(Disk(diskID=1, company="jpg", speed=2, free_space=500, cost=5)),
                         "ID 1 already exists")
        self.assertEqual(Status.BAD_PARAMS,
                         Solution.addDisk(Disk(diskID=2, company="jpg", speed=2, free_space=500, cost=-5)),
                         "cost is negative")
        disk = Solution.getDiskByID(diskID=1)
        assert disk.getDiskID() == 1
        disk = Solution.getDiskByID(diskID=9)
        assert disk.getDiskID() is None

        self.assertEqual(Status.OK, Solution.deleteDisk(diskID=1), "Should work")
        disk = Solution.getDiskByID(diskID=1)
        assert disk.getDiskID() is None

        self.assertEqual(Status.OK, Solution.addDisk(Disk(diskID=1, company="jpg", speed=2, free_space=500, cost=5)),
                         "Should work")
        self.assertEqual(Status.OK, Solution.clearTables(), "Should work")
        disk = Solution.getDiskByID(diskID=1)
        assert disk.getDiskID() is None

    def test_rams(self) -> None:
        self.assertEqual(Status.OK, Solution.addRAM(RAM(ramID=1, company="pdf", size=10)),
                         "Should work")
        self.assertEqual(Status.ALREADY_EXISTS,
                         Solution.addRAM(RAM(ramID=1, company="pdf", size=10)),
                         "ID 1 already exists")
        self.assertEqual(Status.BAD_PARAMS,
                         Solution.addRAM(RAM(ramID=5, company="pdf", size=-10)),
                         "size is negative")
        ram = Solution.getRAMByID(ramID=1)
        assert ram.getRamID() == 1
        ram = Solution.getRAMByID(ramID=9)
        assert ram.getRamID() is None

        self.assertEqual(Status.OK, Solution.deleteRAM(ramID=1), "Should work")
        ram = Solution.getRAMByID(ramID=1)
        assert ram.getRamID() is None

        self.assertEqual(Status.OK, Solution.addRAM(RAM(ramID=1, company="pdf", size=10)),
                         "Should work")
        self.assertEqual(Status.OK, Solution.clearTables(), "Should work")
        ram = Solution.getRAMByID(ramID=1)
        assert ram.getRamID() is None

    def test_add_disk_and_file(self) -> None:
        disk = Disk(diskID=1, company="pdf", speed=10, free_space=92, cost=87)
        file = File(fileID=8, type="jpg", size=976)
        self.assertEqual(Status.OK, Solution.addDiskAndFile(disk=disk, file=file),
                         "Should work")

        disk = Disk(diskID=11, company="pdf", speed=10, free_space=92, cost=87)
        file = File(fileID=81, type="jpg", size=-976)
        self.assertEqual(Status.BAD_PARAMS, Solution.addDiskAndFile(disk=disk, file=file),
                         "File's size is negative")

        disk = Solution.getDiskByID(1)
        assert disk.getDiskID() == 1

        file = Solution.getFileByID(8)
        assert file.getFileID() == 8

        disk = Solution.getDiskByID(11)
        assert disk.getDiskID() is None

    def test_files_on_disks(self) -> None:
        disk = Disk(diskID=1, company="pdf", speed=10, free_space=92, cost=87)
        file = File(fileID=8, type="jpg", size=50)
        self.assertEqual(Status.OK, Solution.addDiskAndFile(disk=disk, file=file),
                         "Should work")
        self.assertEqual(Status.OK, Solution.addFileToDisk(file=file, diskID=1),
                         "Should work")
        self.assertEqual(Status.ALREADY_EXISTS, Solution.addFileToDisk(file=file, diskID=1),
                         "Disk and file already exist")
        file = File(fileID=10, type="jpg", size=5000)
        self.assertEqual(Status.OK, Solution.addFile(file), "Should work")
        self.assertEqual(Status.BAD_PARAMS, Solution.addFileToDisk(file=file, diskID=1),
                         "File is too big")
        file = File(fileID=99, type="jpg", size=10)
        self.assertEqual(Status.NOT_EXISTS, Solution.addFileToDisk(file=file, diskID=1),
                         "File does not exist")
        file = File(fileID=8, type="jpg", size=50)
        self.assertEqual(Status.OK, Solution.removeFileFromDisk(file, 1))
        self.assertEqual(Status.OK, Solution.removeFileFromDisk(file, 1))

    def test_rams_on_disks(self) -> None:
        disk = Disk(diskID=1, company="pdf", speed=10, free_space=92, cost=87)
        ram = RAM(ramID=1, company="ramox", size=500)
        self.assertEqual(Status.NOT_EXISTS, Solution.addRAMToDisk(ramID=1, diskID=1), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram), "Should work")
        self.assertEqual(Status.NOT_EXISTS, Solution.addRAMToDisk(ramID=1, diskID=1), "Disk does not exist")
        self.assertEqual(Status.OK, Solution.addDisk(disk), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(1, 1), "Should work")
        self.assertEqual(Status.OK, Solution.removeRAMFromDisk(1, 1), "Should work")
        self.assertEqual(Status.NOT_EXISTS, Solution.removeRAMFromDisk(1, 2), "RAM does not exist")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(1, 1), "Should work")
        ram = RAM(ramID=2, company="ramox", size=432)
        self.assertEqual(Status.OK, Solution.addRAM(ram), "Should work")
        self.assertEqual(Status.NOT_EXISTS, Solution.removeRAMFromDisk(ramID=2, diskID=1),
                         "RAM and Disk are not paired")

    def test_averageFileSizeOnDisk(self) -> None:
        disk = Disk(diskID=1, company="pdf", speed=10, free_space=92, cost=87)
        file = File(fileID=12, type="jpg", size=2)
        self.assertEqual(Status.OK, Solution.addDiskAndFile(disk=disk, file=file),
                         "Should work")
        self.assertEqual(Status.OK, Solution.addFileToDisk(file=file, diskID=1),
                         "Should work")
        for i in range(1, 10):
            self.assertEqual(Status.OK, Solution.addFile(File(i, "jpg", 2)), "Should work")
            self.assertEqual(Status.OK, Solution.addFileToDisk(file=File(i, "jpg", 2), diskID=1),
                             "Should work")
        self.assertEqual(2.0, Solution.averageFileSizeOnDisk(1), "Should Work")
        self.assertEqual(0.0, Solution.averageFileSizeOnDisk(2), "Should get None - there is no diskID 2")
        disk = Disk(diskID=2, company="pdf", speed=10, free_space=92, cost=87)
        self.assertEqual(Status.OK, Solution.addDisk(disk=disk), "Should work")
        self.assertEqual(0.0, Solution.averageFileSizeOnDisk(2), "Should get None - there are no files on diskID 2")

    def test_diskTotalRAM(self) -> None:
        disk = Disk(diskID=1, company="pdf", speed=10, free_space=92, cost=87)
        self.assertEqual(Status.OK, Solution.addDisk(disk=disk), "Should work")
        for i in range(1, 10):
            self.assertEqual(Status.OK, Solution.addRAM(RAM(ramID=i, size=2, company="comp")), "Should work")
            self.assertEqual(Status.OK, Solution.addRAMToDisk(ramID=i, diskID=1), "Should work")
        self.assertEqual(18, Solution.diskTotalRAM(1), "Should Work")
        self.assertEqual(0, Solution.diskTotalRAM(2), "Should get None - there is no diskID 2")
        disk = Disk(diskID=2, company="pdf", speed=10, free_space=92, cost=87)
        self.assertEqual(Status.OK, Solution.addDisk(disk=disk), "Should work")
        self.assertEqual(0, Solution.diskTotalRAM(2), "Should get None - there are no files on diskID 2")

    def test_getCostForType(self) -> None:
        disk1 = Disk(diskID=1, company="disks", speed=10, free_space=92, cost=10)
        disk2 = Disk(diskID=2, company="disks", speed=10, free_space=92, cost=20)
        file1 = File(fileID=1, type="jpg", size=20)
        file2 = File(fileID=2, type="jpg", size=50)
        file3 = File(fileID=3, type="word", size=5)
        self.assertEqual(Status.OK, Solution.addDisk(disk1), "Should work")
        self.assertEqual(Status.OK, Solution.addDisk(disk2), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file1), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file2), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file3), "Should work")

        self.assertEqual(Status.OK, Solution.addFileToDisk(file=file1, diskID=1), "Should work")
        self.assertEqual(Status.OK, Solution.addFileToDisk(file=file2, diskID=2), "Should work")
        self.assertEqual(Status.OK, Solution.addFileToDisk(file=file3, diskID=2), "Should work")

        self.assertEqual(10 * 20 + 20 * 50, Solution.getCostForType("jpg"), "Should work")
        self.assertEqual(20 * 5, Solution.getCostForType("word"), "Should work")
        self.assertEqual(0, Solution.getCostForType("pdf"), "There are no pdf files!")

    def test_getFilesCanBeAddedToDisk(self) -> None:
        disk1 = Disk(diskID=1, company="disks", speed=10, free_space=92, cost=10)
        disk2 = Disk(diskID=2, company="disks", speed=10, free_space=20, cost=20)
        file1 = File(fileID=1, type="jpg", size=20)
        file2 = File(fileID=2, type="jpg", size=50)
        file3 = File(fileID=3, type="word", size=5)
        file4 = File(fileID=4, type="word", size=5)
        file5 = File(fileID=5, type="word", size=53)
        file6 = File(fileID=6, type="word", size=52)
        self.assertEqual(Status.OK, Solution.addDisk(disk1), "Should work")
        self.assertEqual(Status.OK, Solution.addDisk(disk2), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file1), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file2), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file3), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file4), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file5), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file6), "Should work")

        self.assertEqual([1, 2, 3, 4, 5], Solution.getFilesCanBeAddedToDisk(diskID=1), "Should work")
        self.assertEqual([1, 3, 4], Solution.getFilesCanBeAddedToDisk(diskID=2), "Should work")

     def test_getFilesCanBeAddedToDiskAndRAM(self) -> None:
        disk1 = Disk(diskID=1, company="disks", speed=10, free_space=92, cost=10)
        disk2 = Disk(diskID=2, company="disks", speed=10, free_space=20, cost=20)
        ram1 = RAM(ramID=1, company="raminc", size=25)
        ram2 = RAM(ramID=2, company="raminc", size=25)
        ram3 = RAM(ramID=3, company="raminc", size=5)
        file1 = File(fileID=1, type="jpg", size=20)
        file2 = File(fileID=2, type="jpg", size=50)
        file3 = File(fileID=3, type="word", size=5)
        file4 = File(fileID=4, type="word", size=5)
        file5 = File(fileID=5, type="word", size=53)
        file6 = File(fileID=6, type="word", size=52)
        self.assertEqual(Status.OK, Solution.addDisk(disk1), "Should work")
        self.assertEqual(Status.OK, Solution.addDisk(disk2), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file1), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file2), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file3), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file4), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file5), "Should work")
        self.assertEqual(Status.OK, Solution.addFile(file6), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram1), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram2), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram3), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(1, 1), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(2, 1), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(3, 2), "Should work")

        self.assertEqual([1, 2, 3, 4], Solution.getFilesCanBeAddedToDiskAndRAM(diskID=1), "Should work")
        self.assertEqual([3, 4], Solution.getFilesCanBeAddedToDiskAndRAM(diskID=2), "Should work")

     def test_isCompanyExclusive(self) -> None:
        disk1 = Disk(diskID=1, company="disks", speed=10, free_space=92, cost=10)
        disk2 = Disk(diskID=2, company="disks", speed=10, free_space=20, cost=20)
        ram1 = RAM(ramID=1, company="disks", size=4)
        ram2 = RAM(ramID=2, company="disks", size=476)
        ram3 = RAM(ramID=3, company="disks", size=423)
        ram4 = RAM(ramID=4, company="disks", size=49)
        ram5 = RAM(ramID=5, company="disks", size=41)
        ram6 = RAM(ramID=6, company="disks", size=42)
        ram7 = RAM(ramID=7, company="bad_disks", size=65)
        ram8 = RAM(ramID=8, company="disks", size=32)
        self.assertEqual(Status.OK, Solution.addDisk(disk1), "Should work")
        self.assertEqual(Status.OK, Solution.addDisk(disk2), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram1), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram2), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram3), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram4), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram5), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram6), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram7), "Should work")
        self.assertEqual(Status.OK, Solution.addRAM(ram8), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(ramID=1, diskID=1), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(ramID=2, diskID=1), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(ramID=3, diskID=1), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(ramID=4, diskID=2), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(ramID=5, diskID=2), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(ramID=6, diskID=2), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(ramID=7, diskID=2), "Should work")
        self.assertEqual(Status.OK, Solution.addRAMToDisk(ramID=8, diskID=2), "Should work")
        self.assertEqual(True, Solution.isCompanyExclusive(1), "All companies are the same")
        self.assertEqual(False, Solution.isCompanyExclusive(2), "RAM with ramID=7 is of different company")
        

# *** DO NOT RUN EACH TEST MANUALLY ***
if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
