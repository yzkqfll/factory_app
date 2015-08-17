
import  os
import shutil

RELEASE_DIR = 'ibaby-release'

class ReleasePacket:
    def __init__(self):
        pass


    def start(self):
        if os.path.exists(RELEASE_DIR):
            shutil.rmtree(RELEASE_DIR)

if __name__ == '__main__':
    packet = ReleasePacket()
