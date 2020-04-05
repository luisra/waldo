from datetime import datetime
from flask import request
from app import app
import unittest

class FlaskTestCase(unittest.TestCase):
    
    # Test route
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
     
    # Test html
    def test_home(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'Weapons Detection and Localization' in response.data)
        
    # Test results
    def test_ui(self):
        
        data = {'conf':0.7, 'buff':0}
        f = open('static/cop.jpg', 'rb')
        data['file'] = (f, 'test.jpg')
        
        tester = app.test_client(self)
        response = tester.post('/', data=data, follow_redirects=True,
                              content_type='multipart/form-data')
        
        f.close()
        self.assertEqual(response.status_code, 200)
    
    # Test api results
    def test_api(self):
        
        data = {'conf':0.7, 'buff':0}
        f = open('static/guns.mp4', 'rb')
        data['file'] = (f,'test.mp4')
        
        tester = app.test_client(self)
        response = tester.post('/api', data=data, follow_redirects=True, 
                               content_type='multipart/form-data')
        
        f.close()
        self.assertEqual(response.status_code, 200)
                
if __name__ == '__main__':
    unittest.main()
    
    
    
