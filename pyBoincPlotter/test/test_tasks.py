# Standard python imports
import unittest

# This project
import tasks

class TestTasks(unittest.TestCase):   
    def setUp(self):
        pass
    
    def test_name(self):
        pass
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTasks)
    unittest.TextTestRunner(verbosity=2).run(suite)
