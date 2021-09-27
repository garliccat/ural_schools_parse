from selenium import webdriver
import os, glob
import requests



def download_docs(driver: webdriver, # selenuim webdriver
                    destination_path: str = '', # string of path where the dir 'documents' will be created for documents
                    extensions: list = ['.pdf', '.doc', '.xls', '.jpg']): # optional extensions to look for
    '''
    searches for links of documents within provided list of extensions (default list included) and downloads all of them
    requires: Selenuim WebDriver, requests, glob, os
    '''

    forbidden = ['<', '>', ':', '"', '\\', '|', '?', '*', ';', '/']
    if not os.path.exists('{}/documents'.format(destination_path)):
        os.makedirs('{}/documents'.format(destination_path))
    for extension in extensions:
        counter = 1
        try:
            documents = driver.find_elements_by_xpath("//a[contains(@href, '{}')]".format(extension))
            print('{} DOCUMENTS FOUND ON PAGE: {}'.format(extension, len(documents)))
            for document in documents:
                document_url = document.get_attribute('href')
                # print('\nCurrent url: {}\n'.format(driver.current_url))
                # print('Document url: {}'.format(document_url))
                document_name = document.text[:200]
                document_name = ''.join([i for i in document_name if i not in forbidden])
                document_name = '_'.join([str(counter), document_name])
                path = '{}/documents/{}{}'.format(destination_path, document_name, extension)
                counter += 1
                # exist_documents = glob.glob('{}/documents/{}*{}'.format(destination_path, document_name, extension))
                # if exist_documents:
                #     if len(exist_documents) == 1:
                #         path = '{}/documents/{}_1{}'.format(destination_path, document_name, extension)
                #     else:
                #         num_docs = glob.glob('{}/documents/{}_*'.format(destination_path, document_name))
                #         numbers = [int(i.split('_')[-1].split('.')[0]) for i in num_docs]
                #         path = '{}/documents/{}_{}{}'.format(destination_path, document_name, str(max(numbers) + 1), extension)
                # else:
                #     path = '{}/documents/{}{}'.format(destination_path, document_name, extension)
                
                try: # downloading the document
                    data = requests.get(document_url, allow_redirects=True, timeout=(10)).content
                    with open(path, 'wb') as handler:
                        handler.write(data)
                except:
                    print('>>> Document {} is too slow for download, skipped <<<'.format(document_name))
                    continue

                print('>>> Document {} downloaded <<<'.format(document_name))
        except Exception as e:
            print(e)


''' https://4zar.uralschool.ru/sveden/objects '''

while True:
    url = input('Please enter URL, or Q to quit: >')

    if url == 'Q':
        break

    driver_options = webdriver.FirefoxOptions()
    driver_options.headless = True
    driver_options.add_argument("--no-sandbox")
    driver_options.add_argument("--disable-gpu")
    driver_options.add_argument("--disable-gpu-sandbox")
    driver = webdriver.Firefox(options=driver_options)

    driver.get(url)

    download_docs(driver, '.')
