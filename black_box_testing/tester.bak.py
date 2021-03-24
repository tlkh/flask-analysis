import time
import requests
from seleniumwire import webdriver

driver = webdriver.Chrome("./chromedriver_mac")

# Check if server is running - check homepage

driver.get("http://localhost:5000")
hw_text = driver.find_element_by_id("helloworld").get_attribute("innerHTML")
print(hw_text)
assert hw_text == "Hello, World!"

# Check 404

driver.get("http://localhost:5000/404")

page_title = driver.title 
assert page_title == "404 Not Found"
print(page_title)

# Check escaping inputs

driver.get("http://localhost:5000/inputs")
search_box = driver.find_element_by_id("inputbox")
search_box.send_keys("<h1 id='unsafe_element'>Unsafe Element</h1>")
search_box.submit()
display_out = driver.find_element_by_id("displayout").get_attribute("innerHTML")
print("SAFE:", display_out)
try:
    unsafe_element = driver.find_element_by_id("unsafe_element").get_attribute("innerHTML")
    print("Fail:", unsafe_element)
except:
    print("Pass: Unsafe element not found!")

# Check escaping inputs - UNSAFE

driver.get("http://localhost:5000/inputs_unsafe");
search_box = driver.find_element_by_id("inputbox")
search_box.send_keys("<h1 id='unsafe_element'>Unsafe Element</h1>")
search_box.submit()
display_out = driver.find_element_by_id("displayout").get_attribute("innerHTML")
print("UNSAFE:", display_out)
try:
    unsafe_element = driver.find_element_by_id("unsafe_element").get_attribute("innerHTML")
    print("Fail:", unsafe_element)
except:
    print("Pass: Unsafe element not found!")
    
# Check headers

res = requests.get("http://localhost:5000/test_headers")
print(res.headers)

# Test cookies

driver.delete_all_cookies()

driver.get("http://localhost:5000/test_cookie_options")

cookies = driver.get_cookies()

print("First visit cookies:", len(cookies))

for c in cookies:
    print(c)
    
print("")
    
time.sleep(2)

driver.get("http://localhost:5000/test_cookie_options")

cookies = driver.get_cookies()

print("Second visit cookies:", len(cookies))

for i, c in enumerate(cookies):
    print(i, c)

print("")

# Test exception (see if debugger shows up)

driver.get("http://localhost:5000/test_exception")

try:
    traceback = driver.find_elements_by_class_name("debugger")
    traceback_contents = [t.get_attribute("innerHTML") for t in traceback]
    print("traceback_contents (truncated):", str(traceback_contents)[:100])
except Exception as e:
    print("Unable to find debugger")
    print(e)
    
driver.quit()
