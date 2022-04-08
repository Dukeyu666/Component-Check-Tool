from configparser import ConfigParser

def readout(filename=None):

    config=ConfigParser()
    config.read(filename)
    filesets=config.items('FILESETS')
    
    return list(dict(filesets).values())

