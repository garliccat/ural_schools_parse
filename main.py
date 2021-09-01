from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time, os, glob
import openpyxl
import requests
import re


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


def url_pretty(school_url):
    if school_url[:4] == 'http':
        return school_url
    else:
        return 'http://{}'.format(school_url)


def get_file(school_url, path):
    data = requests.get(school_url).content
    with open(path, 'wb') as handler:
        handler.write(data)
    pass


def document_path(school_path, document_name, extension=''):
    forbidden = ['<', '>', ':', '"', '\\', '|', '?', '*']
    document_name = ''.join([i for i in document_name if i not in forbidden])
    exist_documents = glob.glob('{}/documents/{}*{}'.format(school_path, document_name, extension))
    if exist_documents:
        if len(exist_documents) == 1:
            path = '{}/documents/{}_1{}'.format(school_path, document_name, extension)
            return path
        else:
            num_docs = glob.glob('{}/documents/{}_*'.format(school_path, document_name))
            numbers = [int(i.split('_')[-1].split('.')[0]) for i in num_docs]
            path = '{}/documents/{}_{}{}'.format(school_path, document_name, str(max(numbers) + 1), extension)
            return path
    else:
        return '{}/documents/{}{}'.format(school_path, document_name, extension)


def download_all_docs(driver, school_path):
    extensions = ['.pdf', '.doc', '.xls']
    return None


def main():
    startline = 50 # base = 3
    
    base_xb = openpyxl.load_workbook(filename='urls.xlsx')
    base_ws = base_xb['Лист1']
    for nn, school_url, school_name in zip(list(base_ws['A'])[startline:startline + 20], 
                                    list(base_ws['D'])[startline:startline + 20], 
                                    list(base_ws['C'])[startline:startline + 20]):
        school_url = url_pretty(school_url.value.strip())
        school_name = '{} - {}'.format(nn.value, school_name.value.strip())
        print('\n\n>>>>> {} <<<<<'.format(school_url))
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 1080)
        driver.set_page_load_timeout(5)
        try: # just in case of 404 or some random connection bullshit like RKN
            driver.get(school_url)
            # time.sleep(5)
            school_path = get_path_for_school(school_name)
            take_screenshot(driver, '{}/main_page.png'.format(school_path))

            try:
                try: # жмём на Сведения об образовательной организации take 1
                    school_details_page = driver.find_element_by_partial_link_text('Сведения об')
                    # school_details_page = driver.find_elements_by_xpath("//*[contains(text(), 'Сведения об')]")
                    school_details_page.click()
                    print('Переход на Севедения об организации')
                    # time.sleep(5)
                    take_screenshot(driver, '{}/сведения об.png'.format(school_path))
                except:
                    print('Кликнуть на "Сведения об" не получилось.')

                try: # жмём на кнопку Документы
                    documents_page = driver.find_element_by_partial_link_text('Документы')
                    # documents_page = driver.find_elements_by_xpath("//*[contains(text(), 'Документы')]")
                    documents_page.click()
                    print('Переход на Документы')
                    # time.sleep(5)
                except: 
                    print('Кликнуть на "Документы" не получилось.')

                try:
                    documents = driver.find_elements_by_xpath("//a[contains(@href, '.pdf')]")
                    if not os.path.exists('{}/documents'.format(school_path)):
                        os.makedirs('{}/documents'.format(school_path))
                    for document in documents:
                        document_url = document.get_attribute('href')
                        document_name = document.text
                        get_file(document_url, document_path(school_path, document_name, '.pdf'))
                        print('>>> Документ {} загружен.'.format(document_name))
                except Exception as e:
                    print(e)
                
                try: # идём 
                    pass
                except Exception as e:
                    print(e)

            except Exception as e:
                print(e)


        except WebDriverException:
            print("Page {} down".format(school_url))

    driver.quit()


if __name__ == '__main__':
    main()