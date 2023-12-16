import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import urllib.request


def find_manganame(driver, name):
    elements = driver.find_elements(By.CLASS_NAME, 'manga-list-item__name')
    for element in elements:
        manga_name = element.find_element(By.TAG_NAME, 'span').text
        if manga_name.lower() == name.lower():
            element.click()
            found = True
            return found


def download_images(driver, folder_name, selected_chapters, links, chapters):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    for i in selected_chapters:
        if not os.path.exists(folder_name + f'/{chapters[i]}'):
            os.makedirs(folder_name + f'/{chapters[i]}')

        driver.get(url=links[i])

        count_pages = driver.find_element(By.ID, 'reader-pages').find_elements(By.TAG_NAME, 'option')
        count_pages = int(count_pages[-1].get_attribute('value'))

        for page in range(count_pages):
            driver.implicitly_wait(10)

            image = driver.find_elements(By.TAG_NAME, 'img')[page]
            image_url = image.get_attribute('src')

            filename = folder_name + f'/{chapters[i]}/{page}.png'

            urllib.request.urlretrieve(image_url, filename)

            driver.implicitly_wait(20)

            image.click()
            driver.implicitly_wait(5)


def get_chapters(driver, elements):
    chapters = []
    links = []

    for element in elements:
        chapter = element.find_element(By.CLASS_NAME, 'media-chapter__name')
        link = element.find_element(By.CLASS_NAME, 'link-default').get_attribute('href')
        links.append(link)
        chapters.append(chapter.text)

    print('Список всех глав:')
    zipped_chap = zip(range(len(chapters)), chapters)

    for val, name_chap in zipped_chap:
        print(f'№п/п {val}: {name_chap}')

    selected_chapters = set()
    while True:
        chapter = input('Введите №п/п главы, для выхода введите q:')
        if chapter == 'q':
            break
        else:
            try:
                n = int(chapter)
                # обработка выхода за границы
                if -1 < n <= len(chapters):
                    selected_chapters.add(n)
                else:
                    raise ValueError
            except ValueError:
                print('Нормальный номер введи, а')

    folder_name = driver.find_element(By.CLASS_NAME, 'media-name__main')

    # ! путь к папке
    folder_name = '/Users/shiva/PycharmProjects/MLP_2_parser/' + folder_name.text

    download_images(driver, folder_name, selected_chapters, links, chapters)


def get_manga(site_url):
    options = webdriver.ChromeOptions()
    #    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url=site_url)
        driver.implicitly_wait(20)
        try:
            elements = driver.find_element(By.ID, "search-link")
            elements.click()
            driver.implicitly_wait(20)

            name = input('Введите оригинальное название: ')

            elements = driver.find_element(By.CLASS_NAME, "search__input")
            elements.click()
            elements.clear()
            elements.send_keys(name)
            driver.implicitly_wait(20)

            if elements:
                found = find_manganame(driver, name)

                if found:
                    elements = driver.find_elements(By.CLASS_NAME,
                                                    'tabs__item')[1]
                    elements.click()
                    driver.implicitly_wait(20)

                    #
                    # Листаем вниз, мы хотим все главы
                    #

                    driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
                    driver.implicitly_wait(20)
                    elements = driver.find_elements(By.CLASS_NAME, 'media-chapter')

                    if elements:
                        get_chapters(driver, elements)
                    else:
                        print('В манге ещё нет глав :(')
            else:

                #
                # некоторая манга не видна не авторизированным
                # пользователям :(
                #

                print('Ничего не найдено :(')
        except NoSuchElementException:
            print("[Exception] NoSuchElementException")
    except Exception as _ex:
        print(_ex)
    driver.close()
    driver.quit()


if __name__ == '__main__':
    url = 'https://mangalib.me/'

    # Пользователь может ввести название манги в консоль.
    # Название вводится транслитом с оригинального названия но английскими буквами,
    # например "Я мачеха, но моя дочь слишком милая" будет
    # "gyemoinde ttal-i neomu gwiyeowo".

    # После ввода названия у пользователя должен появиться список глав этой манги/манхвы и т.п.
    # После выбора конкретной главы или нескольких глав,
    # появляется папка или папки с картинками всех страниц конкретных глав

    # "kkum-eseo jayulo"
    get_manga(url)
