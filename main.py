from selenium import webdriver
import time, os, glob, re
import openpyxl
import requests
from PIL import Image


def take_screenshot(driver, save_path, ratio = None):
    # first type
    S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
    driver.set_window_size(S('Width'),S('Height'))
    driver.find_element_by_tag_name('body').screenshot(save_path)
    # second type
    # max_window_height = driver.execute_script('return Math.max('
    #                                           'document.body.scrollHeight, '
    #                                           'document.body.offsetHeight, '
    #                                           'document.documentElement.clientHeight, '
    #                                           'document.documentElement.scrollHeight, '
    #                                           'document.documentElement.offsetHeight);'
    #                                           )
    # driver.set_window_size(1980, max_window_height)
    # driver.find_element_by_tag_name('body').screenshot(save_path)

    im = Image.open(save_path)
    rgb_im = im.convert('RGB')
    if ratio is not None:
        w, h = rgb_im.size
        if h / w > float(ratio):
            rgb_im = rgb_im.crop((0, 0, w, w * ratio))
    rgb_im.save(save_path)


def url_pretty(school_url):
    if school_url[:4] == 'http':
        return school_url
    else:
        return 'http://{}'.format(school_url)


def download_docs(driver: webdriver, # selenuim webdriver
                    destination_path: str = '', # string of path where the dir 'documents' will be created for documents
                    extensions: list = ['.pdf', '.doc', '.xls', '.jpg'],
                    root_url: str = '', # in case of relative pathes
                    cookies: str = None
                    ): # optional extensions to look for
    '''
    searches for links of documents within provided list of extensions (default list included) and downloads all of them
    requires: Selenuim WebDriver, requests, glob, os
    '''

    forbidden = ['<', '>', ':', '"', '\\', '|', '?', '*', ';', '/'] # excluding the forbidden symbols for the files pathes
    if not os.path.exists(f'{destination_path}/documents'):
        os.makedirs(f'{destination_path}/documents')
    for extension in extensions:
        try:
            documents = driver.find_elements_by_xpath("//a[contains(@href, '{}')]".format(extension))
            print('{} DOCUMENTS FOUND ON PAGE: {}'.format(extension, len(documents)))
            for document in documents:
                document_url = document.get_attribute('href')

                if document_url[:4] != 'http':
                    ''.join(root_url.strip('/'), document_url)

                document_name = document.text
                document_name = ''.join([i for i in document_name[:100] if i not in forbidden])

                exsisting_files = [f for f in os.listdir(os.path.join(destination_path, 'documents')) if os.path.isfile(os.path.join(destination_path, 'documents', f))]
                if len(exsisting_files) == 0:
                    document_name = '_'.join(['1', document_name])
                elif len(exsisting_files) > 0:
                    indexes = [int(x) for x in re.findall(r'(\d+)_', ''.join(exsisting_files))]
                    document_name = '_'.join([str(max(indexes) + 1), document_name])
                else:
                    pass

                path = f'{destination_path}/documents/{document_name}{extension}'

                if 'edusite' in document_url: # for edusite hosting, to avoid clickwall
                    headers = {'origin': 'https://cp.edusite.ru', 'referer': 'https://cp.edusite.ru/'}
                else:
                    headers = None

                try: # downloading the document
                    data = requests.get(document_url, 
                                        allow_redirects=True, 
                                        verify=False,
                                        cookies=cookies,
                                        headers=headers
                                        ).content
                    with open(path, 'wb') as handler:
                        handler.write(data)
                except Exception as e:
                    print(f'>>> {e} happened, document {document_name} skipped <<<')
                    continue

                print(f'>>> Document {document_name}{extension} downloaded <<<')
        except Exception as e:
            print(e)


def main():
    startline = 3 # base = 3
    forbidden = ['<', '>', ':', '"', '\\', '|', '?', '*', ';', '/']

    # driver_options = webdriver.FirefoxOptions()
    driver_options = webdriver.ChromeOptions()

    driver_options.headless = True
    driver_options.add_argument("--no-sandbox")
    driver_options.add_argument("--disable-gpu")
    driver_options.add_argument("--disable-gpu-sandbox")
    driver_options.add_experimental_option("excludeSwitches", ["enable-automation"]) # Chrome only !
    
    # driver = webdriver.Firefox(options=driver_options)
    driver = webdriver.Chrome(options=driver_options)

    driver.set_window_size(1920, 1080)
    driver.set_page_load_timeout(5)
    
    base_xb = openpyxl.load_workbook(filename='urls.xlsx')
    base_ws = base_xb['Лист1']

    with open('categories.txt', 'r', encoding='utf-8') as f: # loading the categories list from file
        sub_categories = f.read().split('\n')

    for nn, county, inn, school_name, school_url, flag in zip(
                                    list(base_ws['A'])[startline:],
                                    list(base_ws['B'])[startline:],
                                    list(base_ws['C'])[startline:],
                                    list(base_ws['D'])[startline:],
                                    list(base_ws['E'])[startline:],
                                    list(base_ws['F'])[startline:]
                                    ):
        if flag.value == 1: # using flag to process selected schools, in case of some distinct problems
            ### cleaning the variables
            if school_url.value.split('/')[-1] == '':
                school_url_for_name = school_url.value.split('/')[-2]
            else:
                school_url_for_name = school_url.value.split('/')[-1]
            school_url_for_name = ''.join([i for i in school_url_for_name if i not in forbidden])
            
            county = ''.join([i for i in county.value.strip() if i not in forbidden])

            inn = inn.value

            school_name = ''.join([i for i in school_name.value.strip() if i not in forbidden])
            school_name = '{}_{}_{}'.format(str(inn), school_url_for_name, school_name)

            school_url = url_pretty(school_url.value.strip())
            
            print(f'\n\n>>>>> {county}  ---  {school_url} <<<<<')


            ### checking and creating the paths for school
            if not os.path.exists('counties'):
                os.mkdir('counties')
            if not os.path.exists(os.path.join('counties', county)):
                os.mkdir(os.path.join('counties', county))
            if not os.path.exists(os.path.join('counties', county, school_name)):
                os.mkdir(os.path.join('counties', county, school_name))

            school_path = os.path.join('counties', county, school_name)
            
            if len(os.listdir(school_path)) <= 5:
                print(f'\n======= ALMOST EMPTY SCHOOL! {county} - {school_name} ========\n')

            if len(os.listdir(school_path)) == 0:
                try: # just in case of 404 or some random connection bullshit like RKN
                    driver.get(school_url)
                except Exception as e:
                    print(f"!!!!! Couldn't reach {school_url} , {e} happened, skipping")
                    continue

                try: # in case of Внимание, перейти ли в раздел домашнего обучения?
                    annoying_shit = driver.find_element_by_xpath('//button[text()="Нет, позже"]')
                    annoying_shit.click()
                    print('Banner with remote education closed.')
                    time.sleep(2)
                except:
                    pass

                take_screenshot(driver, '{}/main_page.jpg'.format(school_path), ratio=3) # screenshot of the main page

                try: # жмём на Сведения об образовательной организации
                    school_details_page = driver.find_element_by_partial_link_text('Сведения об')
                    # school_details_page = driver.find_element_by_xpath("//*[contains(translate(., 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'сведения об')]")
                    school_details_page.click()
                    print('Переход на Севедения об организации')
                    take_screenshot(driver, f'{school_path}/сведения об организации.jpg', ratio=3)
                except:
                    try:
                        school_details_page = driver.find_element_by_partial_link_text('СВЕДЕНИЯ ОБ')
                        school_details_page.click()
                        print('Переход на Севедения об организации')
                        take_screenshot(driver, f'{school_path}/сведения об организации.jpg', ratio=3)
                    except:
                        print('Кликнуть на "Сведения об" не получилось.')

                finally:
                    cats_urls = {}
                    for sub_category in sub_categories:
                        try:
                            link = driver.find_element_by_partial_link_text(sub_category).get_attribute('href')
                            cats_urls[sub_category] = link
                        except Exception as e:
                            print(e)

                for sub_category, sub_url in cats_urls.items():
                    try: # trying to push the button of the current category
                        driver.get(sub_url)
                        print(f'Переход на {sub_category}')
                        time.sleep(2)
                        take_screenshot(driver, f'{school_path}/{sub_category}.jpg', ratio=3)
                        download_docs(driver, school_path, root_url=school_url) # downloading all the documents out of the current page
                    except Exception as e: 
                        print(f'{e} occured, cant go to {sub_category}')
                    
                    time.sleep(2)

    driver.quit()

if __name__ == '__main__':
    main()
