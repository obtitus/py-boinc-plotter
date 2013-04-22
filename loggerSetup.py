import logging
def loggerSetup(loggerLevel):
    logger = logging.getLogger('boinc')
    logger.setLevel(loggerLevel)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
