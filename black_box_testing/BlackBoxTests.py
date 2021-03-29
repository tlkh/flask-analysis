import os
import time
import random
import unittest
import requests
from seleniumwire import webdriver

#CHROMEDRIVER_PATH = "./chromedriver_mac"
CHROMEDRIVER_PATH = "./chromedriver_linux"

BASE_URL = "http://localhost:5000/"


class TestHTTPServerRunning(unittest.TestCase):
    """Check if server is running by checking homepage (HTTP)"""

    def setUp(self):
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)

    def test(self):
        self.driver.get("http://localhost:5000/")
        hw_text = self.driver.find_element_by_id(
            "helloworld").get_attribute("innerHTML")
        self.assertEqual(hw_text, "Hello, World!")

    def tearDown(self):
        self.driver.quit()


class AA_TestHTTPSServerRunning(unittest.TestCase):
    """Check if server is running by checking homepage (HTTPS)"""

    def setUp(self):
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)

    def test(self):
        global BASE_URL
        self.driver.get("https://localhost:5000/")
        hw_text = self.driver.find_element_by_id(
            "helloworld").get_attribute("innerHTML")
        self.assertEqual(hw_text, "Hello, World!")
        BASE_URL = "https://localhost:5000/"
        print("Since HTTPS is working, we switch to that for testing")

    def tearDown(self):
        self.driver.quit()


class Test404Page(unittest.TestCase):
    """Check 404 page"""

    def setUp(self):
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)

    def test(self):
        global BASE_URL
        self.driver.get(BASE_URL+"invalid_page")
        page_title = self.driver.title
        self.assertEqual(page_title, "404 Not Found")

    def tearDown(self):
        self.driver.quit()


class TestEscapeHTMLInputs(unittest.TestCase):
    """Check that HTML in inputs are escaped"""

    def setUp(self):
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)

    def test(self):
        global BASE_URL
        self.driver.get(BASE_URL+"inputs")
        search_box = self.driver.find_element_by_id("inputbox")
        search_box.send_keys("<h1 id='unsafe_element'>Unsafe Element</h1>")
        search_box.submit()
        display_out = self.driver.find_element_by_id(
            "displayout").get_attribute("innerHTML")
        try:
            unsafe_element = driver.find_element_by_id(
                "unsafe_element").get_attribute("innerHTML")
            unsafe_element_found = True
        except:
            unsafe_element_found = False
        self.assertEqual(unsafe_element_found, False)

    def tearDown(self):
        self.driver.quit()


class TestEscapeCSSInputs(unittest.TestCase):
    """Check that CSS in inputs are escaped"""

    def setUp(self):
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)

    def test(self):
        global BASE_URL
        self.driver.get(BASE_URL+"inputs")
        search_box = self.driver.find_element_by_id("inputbox")
        search_box.send_keys(
            "<style>#pagetitle{background-color:red !important}</style>")
        pagetitle = self.driver.find_element_by_id("pagetitle")
        bgcolor = pagetitle.value_of_css_property("background-color")
        self.assertEqual(bgcolor, "rgba(255, 255, 255, 1)")

    def tearDown(self):
        self.driver.quit()


class TestEscapeJSInputs(unittest.TestCase):
    """Check that JS in inputs are escaped"""

    def setUp(self):
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)

    def test(self):
        global BASE_URL
        self.driver.get(BASE_URL+"inputs")
        search_box = self.driver.find_element_by_id("inputbox")
        JAVASCRIPT = "<script>var pagetitle = document.getElementById('pagetitle');pagetitle.innerHTML+='pwned!';</script>"
        search_box.send_keys(JAVASCRIPT)
        pagetitle = self.driver.find_element_by_id(
            "pagetitle").get_attribute("innerHTML")
        if "pwned" in pagetitle:
            unsafe_element_found = True
        else:
            unsafe_element_found = False
        self.assertEqual(unsafe_element_found, False)

    def tearDown(self):
        self.driver.quit()


class TestRandomInputs(unittest.TestCase):
    """Check that random strings in inputs do not crash application"""

    def setUp(self):
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)

    def test(self, iterations=30):
        global BASE_URL
        self.driver.get(BASE_URL+"inputs")
        for i in range(iterations):
            search_box = self.driver.find_element_by_id("inputbox")
            length = random.randint(10, 100)
            BYTESTRING = str(os.urandom(length))
            search_box.send_keys(BYTESTRING)
            search_box.submit()
        self.driver.get(BASE_URL)
        hw_text = self.driver.find_element_by_id(
            "helloworld").get_attribute("innerHTML")
        self.assertEqual(hw_text, "Hello, World!")

    def tearDown(self):
        self.driver.quit()


class TestSecurityHeaders(unittest.TestCase):
    """Check security headers on test page"""

    def setUp(self):
        pass

    def test(self):
        global BASE_URL
        res_headers = requests.get(
            BASE_URL+"test_headers", verify='cert.pem').headers
        correct_headers = {'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                           'Content-Security-Policy': "default-src 'self'",
                           'X-Content-Type-Options': 'nosniff',
                           'X-Frame-Options': 'SAMEORIGIN',
                           'X-XSS-Protection': '1; mode=block'}
        for k in list(correct_headers.keys()):
            self.assertEqual(res_headers[k], correct_headers[k])

    def tearDown(self):
        pass


class TestServerFingerprint(unittest.TestCase):
    """Check Flask server is able to hide fingerprint"""

    def setUp(self):
        pass

    def test(self):
        global BASE_URL
        res_headers = requests.get(
            BASE_URL+"test_headers", verify='cert.pem').headers
        self.assertEqual(res_headers["Server"], "None")

    def tearDown(self):
        pass


class TestCookieLifetime(unittest.TestCase):
    """Test cookie lifetime is properly set"""

    def setUp(self):
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)
        self.driver.delete_all_cookies()

    def test(self):
        global BASE_URL
        self.driver.get(BASE_URL+"test_cookie_options")
        initial_cookies = self.driver.get_cookies()
        assert len(initial_cookies) > 0
        time.sleep(2)
        self.driver.get(BASE_URL+"test_cookie_options")
        second_cookies = self.driver.get_cookies()
        # we should have more cookies
        self.assertGreater(len(second_cookies), len(initial_cookies))
        # but some cookies from initial visit should expire
        self.assertLess(len(second_cookies), len(initial_cookies)*2)

    def tearDown(self):
        self.driver.quit()


class TestDebuggerVisibility(unittest.TestCase):
    """Test debugger is not visible"""

    def setUp(self):
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)

    def test(self):
        global BASE_URL
        self.driver.get(BASE_URL+"test_exception")
        try:
            traceback = self.driver.find_elements_by_class_name("debugger")
            if len(traceback) > 0:
                traceback_found = True
            else:
                traceback_found = False
        except:
            traceback_found = False
        self.assertEqual(traceback_found, False)

    def tearDown(self):
        self.driver.quit()
