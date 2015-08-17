
import  os
import shutil

RELEASE_DIR = 'ibaby-release'

release_file = ()

class ReleasePacket:
    def __init__(self):
        self.files = ['main.py']

    def start(self):
        if os.path.exists(RELEASE_DIR):
            shutil.rmtree(RELEASE_DIR)

        os.mkdir(RELEASE_DIR)

        for parent, dirname, filenames in os.walk('.\\'):
            if parent== '.\\':
                for file in filenames:
                    if file.endswith('pyc'):
                        self.files.append(file)

        for file in self.files:
            shutil.copyfile(file, RELEASE_DIR + '\\' + file)

if __name__ == '__main__':
    packet = ReleasePacket()
    packet.start()