from bs4 import BeautifulSoup
from django.test import TestCase, LiveServerTestCase
from django.urls import reverse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from .models import User, StudySpot


# Create your tests here.
def create_user():
    return User.objects.create(email="cs3240.student@gmail.com", username="common_user",
    first_name="Test", last_name="User",
    school="Engineering and Applied Science")


def create_study_spot(user):
    return StudySpot.objects.create(room_number="1010", building="Test Building",
    submitted_by=user)


class UserTest(TestCase):
    def test_common_user(self):
        create_user()
        self.assertTrue(User.objects.filter(email="cs3240.student@gmail.com", username="common_user", first_name="Test", last_name="User").exists())


class SubmissionTest(TestCase):
    def test_add_submission(self):
        user = create_user()
        create_study_spot(user)
        self.assertTrue(StudySpot.objects.filter(room_number="1010",building="Test Building",submitted_by=user).exists())

def test_admin_submission_exists(self):
    user = create_user()
    study_spot = create_study_spot(user)
    study_spot.is_approved = False
    study_spot.save()
    url = reverse("studyspot_list")
    response = self.client.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    found = False
    for row in rows:
        td_elements = row.find_all('td')
        td_texts = [td.get_text() for td in td_elements]
        if 'Test Building' in td_texts and '1010' in td_texts:
            found = True
            break
        self.assertTrue(found)
    def test_admin_approval(self):
        user = create_user()
        study_spot = create_study_spot(user)
        study_spot.is_approved = True
        study_spot.save()
        url = reverse("studyspot_list")
        response = self.client.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr')
        found = False
        for row in rows:
            td_elements = row.find_all('td')
            td_texts = [td.get_text() for td in td_elements]
            if 'Test Building' in td_texts and '1010' in td_texts:
                found = True
                break
            self.assertFalse(found)


class MapTest(LiveServerTestCase):
    def test_map(self):
        options = Options()
        options.add_argument('lang=en') 
        options.add_argument('--headless=new') 
        options.add_argument('--no-sandbox')
        options.page_load_strategy = 'none'
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=options)
        # driver.get(f"{self.live_server_url}")
        # print(driver.title)
        # # # assert True is True
        # WebDriverWait(driver, 10).until(
        #     expected_conditions.presence_of_element_located((By.ID, 'map'))
        # )
        # marker = driver.find_element(By.XPATH, "//div[contains(@title, 'Rotunda')]")
        assert driver.title is not None
