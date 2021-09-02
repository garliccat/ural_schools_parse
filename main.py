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


def download_docs(driver: webdriver, # selenuim webdriver
                    destination_path: str = '', # string of path where the dir 'documents' will be created for documents
                    extensions: list = ['.pdf', '.doc', '.xls', '.jpg']): # optional extensions to look for
    '''
    searches for links of documents within provided list of extensions (default list included) and downloads all of them
    requires: Selenuim WebDriver, requests, glob, os
    '''

    forbidden = ['<', '>', ':', '"', '\\', '|', '?', '*', ';', '/']
    for extension in extensions:
        try:
            documents = driver.find_elements_by_xpath("//a[contains(@href, '{}')]".format(extension))
            if not os.path.exists('{}/documents'.format(destination_path)):
                os.makedirs('{}/documents'.format(destination_path))
                for document in documents:
                    document_url = document.get_attribute('href')
                    # print('Current url: {}'.format(driver.current_url))
                    # print('Document url: {}'.format(document_url))
                    document_name = document.text[:200]
                    document_name = ''.join([i for i in document_name if i not in forbidden])
                    exist_documents = glob.glob('{}/documents/{}*{}'.format(destination_path, document_name, extension))
                    if exist_documents:
                        if len(exist_documents) == 1:
                            path = '{}/documents/{}_1{}'.format(destination_path, document_name, extension)
                        else:
                            num_docs = glob.glob('{}/documents/{}_*'.format(destination_path, document_name))
                            numbers = [int(i.split('_')[-1].split('.')[0]) for i in num_docs]
                            path = '{}/documents/{}_{}{}'.format(destination_path, document_name, str(max(numbers) + 1), extension)
                    else:
                        path = '{}/documents/{}{}'.format(destination_path, document_name, extension)
                    
                    try: # downloading the document
                        data = requests.get(document_url, allow_redirects=True, timeout=(2, 3)).content
                        with open(path, 'wb') as handler:
                            handler.write(data)
                    except:
                        print('>>> Document {} is too slow for download, skipped <<<'.format(document_name))
                        continue

                    print('>>> Document {} downloaded <<<'.format(document_name))
        except Exception as e:
            print(e)
    return None


def main():
    startline = 266 # base = 3
    driver_options = webdriver.ChromeOptions()
    driver_options.headless = True
    driver_options.add_argument("--no-sandbox")
    driver_options.add_argument("--disable-gpu")
    driver_options.add_argument("--disable-gpu-sandbox")
    driver_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=driver_options)
    driver.set_window_size(1920, 1080)
    driver.set_page_load_timeout(5)
    
    base_xb = openpyxl.load_workbook(filename='urls.xlsx')
    base_ws = base_xb['Лист1']
    for nn, school_url, school_name in zip(list(base_ws['A'])[startline:startline + 20], 
                                    list(base_ws['D'])[startline:startline + 20], 
                                    list(base_ws['C'])[startline:startline + 20]):
        school_url = url_pretty(school_url.value.strip())
        school_name = '{} - {}'.format(nn.value, school_name.value.strip())
        print('\n\n>>>>> {} <<<<<'.format(school_url))
        try: # just in case of 404 or some random connection bullshit like RKN
            driver.get(school_url)
            # time.sleep(5)
            school_path = get_path_for_school(school_name)

            try: # in case of Внимание, перейти ли в раздел домашнего обучения?
                annoying_shit = driver.find_element_by_xpath('//button[text()="Нет, позже"]')
                annoying_shit.click()
                print('Banner with remote education closed.')
                time.sleep(2)
            except:
                pass
            take_screenshot(driver, '{}/main_page.png'.format(school_path)) # screenshot of the main page

            try: # jerking the categories
                sub_categories = [
                    'Документы',
                    'Основные сведения',
                    'Структура и органы управления', 
                    'Образование',
                    'Образовательные стандарты',
                    'Руководство. Педагог',
                    'Материально-техническое',
                    'Стипендии и меры',
                    'Платные образовательные',
                    'Финансово-хозяйственная',
                    'Вакантные места',
                    'Доступная среда',
                    'Международное',
                    'Специальные сведения',
                    'Дополнительные сведения'
                    ]
                svedeniya_screen_took = False
                for sub_category in sub_categories:
                    try: # жмём на Сведения об образовательной организации take 1
                        school_details_page = driver.find_element_by_partial_link_text('Сведения об')
                        # school_details_page = driver.find_elements_by_xpath("//*[contains(text(), 'Сведения об')]")
                        school_details_page.click()
                        print('Переход на Севедения об организации')
                        # time.sleep(5)
                        if not svedeniya_screen_took:
                            take_screenshot(driver, '{}/сведения об.png'.format(school_path))
                            svedeniya_screen_took = True
                    except:
                        print('Кликнуть на "Сведения об" не получилось.')

                    try: # trying to push the button of the current category
                        documents_page = driver.find_element_by_partial_link_text(sub_category)
                        # documents_page = driver.find_elements_by_xpath("//*[contains(text(), 'Документы')]")
                        documents_page.click()
                        print('Переход на {}'.format(sub_category))
                        time.sleep(2)
                        take_screenshot(driver, '{}/{}.png'.format(school_path, sub_category))
                    except: 
                        print('Кликнуть на "{}" не получилось.'.format(sub_category))
                    
                    download_docs(driver, school_path) # downloading all the documents out of the current page
                    driver.get(school_url) # getting back to main page

            except Exception as e:
                print(e)


        except Exception as e:
            print(e)
            print("Couldn't reach {} , somehow.".format(school_url))

    driver.quit()


if __name__ == '__main__':
    main()