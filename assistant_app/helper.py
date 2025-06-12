import pyautogui

screenshot = pyautogui.screenshot()
screenshot.save("test_screenshot.png")
print("Saved screenshot to test_screenshot.png")
