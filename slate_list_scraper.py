import argparse
import time
import glob
from collections import OrderedDict
from scraping_common import *
from selenium.webdriver.common.action_chains import ActionChains


def extract_slate_sport(driver, sport):
    """Selects the function specified for sport.
    """
    sports_functions = {
        'https://www.fantasyalarm.com/mlb/projections':globals()['extract_slate_MLB'],
        # 'https://www.fantasyalarm.com/nfl/projections':globals()['extract_slate_NFL'],
        'https://www.fantasyalarm.com/nba/projections':globals()['extract_slate_NBA'],
        # 'https://www.fantasyalarm.com/nhl/projections':'',
        'https://www.fantasyalarm.com/pga/projections':globals()['extract_slate_PGA']
    }
    pass
    data_1 = sports_functions[sport](driver, 'DraftKings', sport)
    data_2 = sports_functions[sport](driver, 'FanDuel', sport)

    data = create_data_for_database(data_1, data_2)


def create_data_for_database(data1, data2):
    """Create the format to save on database.
    """
    pass


def make_login_fantasy_sports(driver, sport):
    """Makes login to fantasy sports.
    """
    email = 'johnscotthayse@gmail.com'
    passwd = 'fantasyfun2019'
    
    wait = WebDriverWait(driver, 10)
    driver.get(sport)

    try:
        skip_button = driver.find_element_by_xpath(
            '//a[contains(@class, "introjs-button introjs-skipbutton")]')
        ActionChains(driver).move_to_element(skip_button).click().perform()
        time.sleep(0.5)
        print('Clicked')
    except NoSuchElementException:
        print("Error skip button.")

    try:
        login_dropdown_button = wait.until(
            EC.presence_of_element_located((By.XPATH,
            '//a[contains(@class, " dropdown-toggle")]'))
        )
        # login_dropdown_button = driver.find_element_by_xpath(
        #     '//a[contains(@class, " dropdown-toggle")]')
        ActionChains(driver).move_to_element(login_dropdown_button)\
            .click().perform()
        time.sleep(0.5)
    except NoSuchElementException:
        print("Error skip button.")
    
    try:
        email_textfield = driver.find_element_by_xpath(
            '//input[contains(@name, "email")]')
        ActionChains(driver).move_to_element(email_textfield).click().send_keys(email)\
            .perform()
        time.sleep(0.5)
    except NoSuchElementException:
        print('Error inserting email')

    try:
        passwd_textfield = driver.find_element_by_xpath(
            '//input[contains(@name, "password")]')
        ActionChains(driver).move_to_element(passwd_textfield).click().send_keys(passwd)\
            .perform()
        time.sleep(0.5)
    except NoSuchElementException:
        print('Error inserting email')
    
    try:
        login_button = driver.find_element_by_xpath(
            '//button[contains(@class, "btn btn-block blue uppercase") and '\
                'contains(@type, "submit")]')
        ActionChains(driver).move_to_element(login_button).click().perform()
        time.sleep(10)
    except NoSuchElementException:
        print('Error login.')
    print('Logged in.')
        

def extract_slate_NBA(driver, score):
    """Extracts the slates list from sport.
    """
    wait = WebDriverWait(driver, 10)

    try:
        skip_button = driver.find_element_by_xpath(
            '//a[contains(@class, "introjs-button introjs-skipbutton")]')
        ActionChains(driver).move_to_element(skip_button).click().perform()
        time.sleep(0.5)
        print('Clicked')
    except NoSuchElementException:
        print("Error skip button.")

    try:
        projections_button = wait.until(
            EC.presence_of_element_located((By.ID, 
            "mobile-click-i-class-fa-fa-line-chart-aria-hidden-true-i-projections"))
        )
        ActionChains(driver).move_to_element(projections_button).click().perform()
        time.sleep(2)
    except NoSuchElementException:
        print("Error clicking at projections.")

    slate_list = driver.find_element_by_xpath('//div[contains(text(), "Slates")]')
    slates = dict()

    for slate in slate_list.find_elements_by_xpath(
        './/parent::div//following-sibling::a'):
        ActionChains(driver).move_to_element(slate).click().perform()
        time.sleep(3)
    
        # Clicks the score and download the file
        slate_button = wait.until(
            EC.presence_of_element_located((By.XPATH,
            '//a[contains(text(), "{}")]'.format(score)))
        )
        ActionChains(driver).move_to_element(slate_button).click().perform()
        time.sleep(1)
        try:
            csv_button = wait.until(
                EC.presence_of_element_located((By.XPATH, 
                "//span[contains(text(), 'CSV')]/parent::a"))
            )
            ActionChains(driver).move_to_element(csv_button).click().perform()
            time.sleep(2)
        except NoSuchElementException:
            print('Download button not found.')
        except Exception as e:
            print('Not downloaded due to:\n{}'.format(e))
        
        # Extracts data from file and deletes it
        slate_data = extract_csv_data()
        slates[slate.text.replace(' ', '')] = slate_data

    return slates


def extract_slate_MLB(driver, score):
    """Extracts the slates list from sport.
    """
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)
    sport = driver.current_url

    try:
        projections_button = wait.until(
            # EC.presence_of_element_located((By.ID, 
            # "mobile-click-i-class-fa-fa-line-chart-aria-hidden-true-i-daily-projections"))
            EC.presence_of_element_located((By.XPATH, 
            '//a[contains(text(), "Daily Projections") and '\
            '@id="mobile-click-i-class-fa-fa-line-chart-aria-hidden-true-i-daily-'\
                'projections"]'))
        )
        actions.move_to_element(projections_button).click().perform()
        time.sleep(7)
    except NoSuchElementException:
        print("Error clicking at projections.")
    finally:
        del(projections_button)
        del(actions)

    # slate_list = driver.find_element_by_xpath('//div[contains(text(), "Slates")]')
    slate_list = wait.until(
        EC.presence_of_element_located((By.XPATH, 
        '//div[contains(text(), "Slates")]'))
    )
    
    driver.execute_script('arguments[0].scrollIntoView();', driver.find_element_by_xpath(
        '//a[@id="mobile-click-all-pos"]'
    ))
    slates = dict()

    for slate in slate_list.find_elements_by_xpath(
        './/parent::div//following-sibling::a'):
        new_actions = ActionChains(driver)
        new_actions.move_to_element(slate).click().perform()
        time.sleep(3)
    
        # Clicks the score and download the file
        driver.execute_script('arguments[0].scrollIntoView();', driver.find_element_by_xpath(
            '//a[@id="mobile-click-all-pos"]'
        ))
        slate_button = wait.until(
            EC.presence_of_element_located((By.XPATH,
            '//a[contains(text(), "{}")]'.format(score)))
        )
        slate_button.click()
        # actions.move_to_element(slate_button).click().perform()
        time.sleep(1)
        try:
            csv_button = wait.until(
                EC.presence_of_element_located((By.XPATH, 
                "//span[contains(text(), 'CSV')]/parent::a"))
            )
            actions.move_to_element(csv_button).click().perform()
            time.sleep(3)
        except NoSuchElementException:
            print('Download button not found.')
        except Exception as e:
            print('Not downloaded due to:\n{}'.format(e))
        
        # Extracts data from file and deletes it
        slate_data = extract_csv_data()
        slates[slate.text.replace(' ', '')] = slate_data

    return slates


def extract_slate_PGA(driver, score, sport_url):
    """Extracts the slates list from sport.
    """
    wait = WebDriverWait(driver, 10)
    driver.get(sport_url)

    # try:
    #     projections_button = wait.until(
    #         EC.presence_of_element_located((By.ID, 
    #         "mobile-click-i-class-fa-fa-line-chart-aria-hidden-true-i-projections"))
    #     )
    #     ActionChains(driver).move_to_element(projections_button).click().perform()
    #     time.sleep(2)
    # except NoSuchElementException:
    #     print("Error clicking at projections.")

    # # Clicks the score and download the file
    # try:
    #     slate_button = wait.until(
    #         EC.presence_of_element_located((By.XPATH,
    #         '//a[contains(text(), "{}")]'.format(score)))
    #     )
    #     ActionChains(driver).move_to_element(slate_button).click().perform()
    #     time.sleep(5)
    # except NoSuchElementException:
    #     print('Score button not found.')
    # except Exception as e:
    #     print('Not clicked score button due to:\n{}'.format(e))
    # finally:
    #     del(slate_button)
    if score == 'FanDuel':
        driver.get('https://www.fantasyalarm.com/pga/projections/daily/FD/')
    
    if score == 'DraftKings':
        driver.get('https://www.fantasyalarm.com/pga/projections/daily/DK/')

    try:
        csv_button = wait.until(
            EC.presence_of_element_located((By.XPATH, 
            "//span[contains(text(), 'CSV')]/parent::a"))
        )
        ActionChains(driver).move_to_element(csv_button).click().perform()
        time.sleep(2)
    except NoSuchElementException:
        print('Download button not found.')
    except Exception as e:
        print('Not downloaded due to:\n{}'.format(e))
    
    # Extracts data from file and deletes it
    slate_data = extract_csv_data()
    return slate_data


def extract_csv_data():
    """Opens downloaded file, loads its content to Python object 
    and delete it.
    """
    data = list()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    for file in glob.glob("*.csv"):
        with open(file, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for raw in csv_reader:
                data.append(raw)
        os.remove(file)
    return data



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
        'Module that extracts slates list and projection data.')
    parser.add_argument('-s', '--sport', metavar='S', type=str,
        help='Determines the sport to extract data from.')
    args = vars(parser.parse_args())
    
    sports = {'MLB':'https://www.fantasyalarm.com/mlb/projections',
              'NFL':'https://www.fantasyalarm.com/nfl/projections',
              'NBA':'https://www.fantasyalarm.com/nba/projections',
              'NHL':'https://www.fantasyalarm.com/nhl/projections',
              'PGA':'https://www.fantasyalarm.com/pga/projections'}

    driver = get_geckodriver()
    driver.set_window_position(0, 0)
    driver.set_window_size(1920, 1080)
    make_login_fantasy_sports(driver, sports[args['sport']])


    try:
        extract_slate_sport(driver, sports[args['sport']])
    except Exception as e:
        print('Stopped due to: \n{}'.format(e))
    finally:
        driver.close()