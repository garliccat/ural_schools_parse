from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time, os, glob
import openpyxl
import requests


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

def get_file(url, path):
    data = requests.get(url).content
    with open(path, 'wb') as handler:
        handler.write(data)
    pass


def main():
    startline = 6
    
    base_xb = openpyxl.load_workbook(filename='urls.xlsx')
    base_ws = base_xb['Лист1']
    for nn, url, school_name in zip(list(base_ws['A'])[startline:20], list(base_ws['D'])[startline:20], list(base_ws['C'])[startline:20]):
        url = url.value.strip()
        school_name = '{} - {}'.format(nn.value, school_name.value.strip())
        print('\n\n>>>>> {} <<<<<'.format(url_pretty(url)))
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 1080)
        driver.set_page_load_timeout(5)
        try: # just in case of 404 or some random connection bullshit like RKN
            driver.get(url_pretty(url))
            driver.implicitly_wait(3)
            school_path = get_path_for_school(school_name)
            # take_screenshot(driver, '{}/main_page.png'.format(school_path))

            try:
                try: # жмём на Сведения об образовательной организации take 1
                    school_details_page = driver.find_element_by_xpath("//*[contains(text(), 'Сведения об')]")
                    school_details_page.click()
                    print('Переход на Севедения об организации')
                    driver.implicitly_wait(3)
                    take_screenshot(driver, '{}/сведения об.png'.format(school_path))
                except:
                    print('Кликнуть на "Сведения об" не получилось.')

                try: # жмём на кнопку Документы
                    documents_page = driver.find_element_by_xpath("//*[contains(text(), 'Документы')]")
                    documents_page.click()
                    print('Переход на Документы')
                    driver.implicitly_wait(3)
                except:
                    print('Кликнуть на "Документы" не получилось.')

                try:
                    documents = driver.find_elements_by_xpath("//a[contains(@href, '.pdf')]")
                    if not os.path.exists('{}/documents'.format(school_path)):
                        os.makedirs('{}/documents'.format(school_path))
                    for document in documents:
                        document_url = document.get_attribute('href')
                        document_file_path = '{}/documents/{}'.format(school_path, document_url.split('/')[-1])
                        get_file(document_url, document_file_path)
                        print('>>> Документ {} загружен.'.format(document_file_path))
                except:
                    print('PDF найти не удалось')

            except Exception as e:
                print(e)


        except WebDriverException:
            print("Page {} down".format(url))

    driver.quit()


if __name__ == '__main__':
    main()