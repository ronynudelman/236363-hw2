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


# *** DO NOT RUN EACH TEST MANUALLY ***
if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
