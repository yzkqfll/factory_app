
import  os
import shutil
import zipfile

RELEASE_DIR = 'ibaby-release'

release_file = 'ibaby.zip'

class ReleasePacket:
    def __init__(self):
        self.files = ['start.bat', 'start.py', '.config', '.log', 'pyserial-2.7.win32.exe', 'python-2.7.10.msi',
                      'ReleaseNote', 'LICENSE']

    def start(self):
        if os.path.exists(RELEASE_DIR):
            shutil.rmtree(RELEASE_DIR)

        os.mkdir(RELEASE_DIR)
		
        if os.path.isfile(release_file):
            os.remove(release_file)

        for root, dirname, filenames in os.walk('.\\'):
            if root== '.\\':
                for file in filenames:
                    if file.endswith('pyc'):
                        self.files.append(file)

        for file in self.files:
            shutil.copyfile(file, RELEASE_DIR + os.sep + file)

        # zip dir
        files = []
        for root, dirname, filenames in os.walk(RELEASE_DIR):
            for file in filenames:
                files.append(os.path.join(root, file))
        zip = zipfile.ZipFile(release_file, "w", zipfile.zlib.DEFLATED)
        for file in files:
            zip.write(file)
        zip.close()

if __name__ == '__main__':
    packet = ReleasePacket()
    packet.start()