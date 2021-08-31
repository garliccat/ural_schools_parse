from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time, os, glob
import openpyxl


def take_screenshot(driver, path):
    S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
    driver.set_window_size(S('Width'),S('Height'))
    driver.find_element_by_tag_name('body').screenshot(path)

def get_path_for_school(school_name):
    school_folders = glob.glob('output/{}*'.format(school_name))
    if school_folders:
        if len(school_folders) == 1:
            path = 'output/{}_1'.format(school_name)
            os.makedirs(path)
            return path
        else:
            num_school_folders = glob.glob('output/{}_*'.format(school_name))
            numbers = [int(i.split('_')[1]) for i in num_school_folders]
            path = 'output/{}_{}'.format(school_name, str(max(numbers) + 1))
            os.makedirs(path)
            return path
    else:
        path = 'output/{}'.format(school_name)
        os.makedirs(path)
        return path

def url_pretty(url):
    if url[:4] == 'http':
        return url
    else:
        return 'http://{}'.format(url)


def main():
    base_xb = openpyxl.load_workbook(filename='urls.xlsx')
    base_ws = base_xb['Лист1']
    for url, school_name in zip(list(base_ws['D'])[3:20], list(base_ws['C'])[3:20]):
        url = url.value.strip()
        school_name = school_name.value.strip()
        print('\n\n>>>>> {} <<<<<'.format(url_pretty(url)))
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 1080)
        driver.set_page_load_timeout(5)
        try:
            driver.get(url_pretty(url))
            school_path = get_path_for_school(school_name)
            take_screenshot(driver, '{}/main_page.png'.format(school_path))
        except WebDriverException:
            print("Page {} down".format(url))

    driver.quit()


if __name__ == '__main__':
    main()