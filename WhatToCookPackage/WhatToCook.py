import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
import imageio.v3 as iio
import json

def getdata1():
    """
    Scrapes savoringfiji.com for dishes based on the 3 courses present on the site
    :param:
        none
    :returns
        foodlist {str : str} : the foodname and it's respective course
        fooddetails { str : [str],[str] } : the foodname and it's ingredient list and list of steps
        imgList { str : str } : the foodname and the link to it's image
    """
    Courselist = ['breakfast', 'lunch', 'dinner']
    foodlist = {}
    fooddetails = {}
    imglist = {}
    for course in Courselist:
        url = f"https://www.savoringfiji.com/category/{course}/"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, features="html.parser")
        urls = soup.find_all('div', {"id": "main"})
        souper = BeautifulSoup(str(urls), features="html.parser")
        links = souper.find_all('a')
        for link in links:
            if 'href="https://www.savoringfiji.com/recipe/' in str(link) and 'img alt' not in str(link) \
                    and 'class="more-link"' not in str(link) and 'comments' not in str(link):
                r = requests.get(link['href'])
                soup = BeautifulSoup(r.text, features="html.parser")
                ingredients = soup.find_all('li', {'class': 'wpurp-recipe-ingredient'})
                steps = soup.find_all('li', {'class': 'wpurp-recipe-instruction'})
                img = soup.find_all('img', {'class' : 'wpurp-recipe-image'})
                ingredientlist = []
                stepsList = []
                for stuff in ingredients:
                    ingredientlist.append(f"{stuff.get_text()}")
                length = int(len(ingredientlist) / 2)
                for stuff in steps:
                    stepstring = stuff.get_text().replace("\n", "")
                    stepsList.append(f"{stepstring}")
                ingredientlist = ingredientlist[:length]
                foodname = link.get_text()
                fooddetails[foodname] = ingredientlist, stepsList
                foodlist[foodname] = course
                for images in img:
                    imglist[foodname] = images.get('src')
    return foodlist, fooddetails, imglist


def getdata2():
    """
    Scrapes snack recipes from thatfijitaste.com and adds them to the existing food lists
    :param:
        none
    :return:
        foodlist {str : str} : the foodname and it's respective course
        fooddetails { str : [str],[str] } : the foodname and it's ingredient list and list of steps
        imgList { str : str } : the foodname and the link to it's image
    """
    foodlist, fooddetails, imgList = getdata1()
    url = 'https://thatfijitaste.com/category/sweets-snacks/'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    links = soup.find_all('h3', {'class': 'entry-title'})
    for entries in links:
        url = entries.a['href']
        r = requests.get(url)
        soup = BeautifulSoup(r.text, features="html.parser")
        if 'breakfast' in soup.text:
            foodlist[entries.get_text()] = 'breakfast'
        else:
            foodlist[entries.get_text()] = 'snack'
        ingredients = soup.find_all('li', {'class': 'ingredient-item'})
        ingredientList = []
        for ingredient in ingredients:
            ingredientList.append(ingredient.get_text())
        steps = soup.find_all('li', {'class': 'direction-step'})
        stepsList = []
        for step in steps:
            stepsList.append(step.text)
        if len(ingredientList) == 0:
            ingredients = soup.find_all('li', {'class': 'ingredient'})
            steps = soup.find_all('li', {'class': 'instruction'})
            for ingredient in ingredients:
                ingredientList.append(ingredient.text)
            for step in steps:
                stepsList.append(step.text)
        img = soup.find_all('img', {"class": "photo wp-post-image lazy"})
        for imger in img:
            imgList[entries.get_text()] = str(imger.get('data-src')).replace('?x39593', '')
        fooddetails[entries.get_text()] = ingredientList, stepsList
    return foodlist, fooddetails, imgList


def getdata3():
    """
    Scrapes dinner recipes from thatfijitaste.com and adds them to the existing food lists, returns the final
    lists of all recipes
    :param:
        none
    :return:
        foodlist {str : str} : the foodname and it's respective course
        fooddetails { str : [str],[str] } : the foodname and it's ingredient list and list of steps
        imgList { str : str } : the foodname and the link to it's image
    """
    foodlist, fooddetails, imgList = getdata2()
    url = 'https://thatfijitaste.com/category/mains-meals/'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    links = soup.find_all('h3', {'class': 'entry-title'})
    for entries in links:
        url = entries.a['href']
        r = requests.get(url)
        soup = BeautifulSoup(r.text, features="html.parser")
        check = soup.find_all('div', {'class': 'page-wrap'})
        if 'Snack' in check:
            bool = 1
        else:
            foodlist[entries.get_text()] = 'dinner'
            ingredients = soup.find_all('li', {'class': 'ingredient-item'})
            ingredientList = []
            for ingredient in ingredients:
                ingredientList.append(ingredient.get_text())
            steps = soup.find_all('li', {'class': 'direction-step'})
            stepsList = []
            for step in steps:
                stepsList.append(step.text)
            if len(ingredientList) == 0:
                ingredients = soup.find_all('li', {'class': 'ingredient'})
                steps = soup.find_all('li', {'class': 'instruction'})
                for ingredient in ingredients:
                    ingredientList.append(ingredient.text)
                for step in steps:
                    stepsList.append(step.text)
            img = soup.find_all('img', {"class": "photo wp-post-image lazy"})
            for imger in img:
                imgList[entries.get_text()] = str(imger.get('data-src')).replace('?x39593', '')
            fooddetails[entries.get_text()] = ingredientList, stepsList
    return foodlist, fooddetails, imgList



def HarvestMonths():
    """
    Reads in the Seasonal.csv file and creates a dictionary with vegetables and their respective months of harvest
    :param:
        none
    :return:
        VegetableMonths {str : str} : A list of vegetables and the months they're harvested in
    """
    seasonfile = pd.read_csv('./Seasonal.csv')
    vegetables = seasonfile['Vegetable']
    VegetableMonths = {}
    for veggies in vegetables:
        months = seasonfile['MonthsOfHarvest'][seasonfile['Vegetable'] == veggies]
        for month in months:
            VegetableMonths[veggies] = month
    return VegetableMonths


def SeasonalVeggies(month = datetime.now().month):
    """
    Creates a list of vegetables that are seasonal to a specific month
    :param:
        month (int) : the month given in a number form
    :return:
        veggieSelection [str] : a list of vegetables that are harvested during the given month
    """
    if month > 12 or month < 1:
        print("Given month doesn't exist")
        return -1
    vegetables = HarvestMonths()
    veggieSelection = []
    for months in vegetables.items():
        strarr = months[1].split(',')
        numarr = []
        for entry in strarr:
            numarr.append(int(entry))
        if month in numarr:
            veggieSelection.append(months[0])
    return veggieSelection


def simple():
    """
    Picks a random recipe from the foodlist and generates a PDF file containing the title, image, ingredients and steps
    :param:
        none
    :return:
        none
    """
    foodlist, fooddetails, imgList = getdata3()
    selection = []
    for keys in foodlist.keys():
        selection.append(keys)
    choice = random.choice(selection)
    imgsrc = imgList[choice]
    if 'thatfijitaste' in imgsrc:
        downloadImageTaste(imgsrc)
    elif 'savoringfiji' in imgsrc:
        downloadImageSavor(imgsrc)
    CreatePDF(choice, fooddetails)


def course_specific(course):
    """
    Picks a random recipe from the foodlist based on the course given and generated a PDF file of said recipe
    :param:
        course (str) : a string containing one of the 4 courses given
    :return:
        none
    """
    foodlist, fooddetails, imgList = getdata3()
    course = course.lower()
    course = course.strip()
    selection = []
    if course not in foodlist.values():
        print("Unknown course, try again")
        quit()
    for item in foodlist.items():
        if item[1] == course:
            selection.append(item[0])
    choice = random.choice(selection)
    imgsrc = imgList[choice]
    if 'thatfijitaste' in imgsrc:
        downloadImageTaste(imgsrc)
    elif 'savoringfiji' in imgsrc:
        downloadImageSavor(imgsrc)
    CreatePDF(choice, fooddetails)


def seasonal(month = datetime.now().month):
    """
    Picks a random recipe based on the vegetables harvested during the given month and generates a PDF file of said recipe
    :param:
        month (int) : a number of the given month, if not given, the default value is the current month
    :return:
        none
    """
    if month > 12 or month < 1:
        print("Given month doesn't exist")
        return -1
    foodlist, fooddetails, imgList = getdata3()
    DuplicateElim = {}
    SeasonalFood = []
    for foodname in fooddetails:
        list1 = fooddetails[foodname][0]
        for veggies in SeasonalVeggies(month):
            for ingredients in list1:
                if veggies in ingredients:
                    DuplicateElim[foodname] = month
    for things in DuplicateElim.keys():
        SeasonalFood.append(things)
    choice = random.choice(SeasonalFood)
    imgsrc = imgList[choice]
    if 'thatfijitaste' in imgsrc:
        downloadImageTaste(imgsrc)
    elif 'savoringfiji' in imgsrc:
        downloadImageSavor(imgsrc)
    CreatePDF(choice, fooddetails)


def combined(course, month = datetime.now().month):
    """
    Picks a random recipe based on the vegetables harvested during the given month, as well as the course given
    and generates a PDF file of said recipe
    :param:
    course (str) : a string containing one of the 4 courses given
    month (int) : a number of the given month, if not given, the default value is the current month
    :return:
        none
    """
    if month > 12 or month < 1:
        print("Given month doesn't exist")
        return -1
    foodlist, fooddetails, imgList = getdata3()
    DuplicateElim = {}
    SeasonalFood = []
    if course not in foodlist.values():
        print("Unknown course, try again")
        quit()
    for foodname in fooddetails:
        list1 = fooddetails[foodname][0]
        for veggies in SeasonalVeggies(month):
            for ingredients in list1:
                if veggies in ingredients:
                       DuplicateElim[foodname] = month
        for things in DuplicateElim.keys():
            SeasonalFood.append(things)
    FinalSelection = []
    DuplicateElim.clear()
    for food in SeasonalFood:
        if foodlist[food] == course:
            DuplicateElim[food] = 'yes'
    for foods in DuplicateElim.keys():
        FinalSelection.append(foods)
    if len(FinalSelection) == 0:
        print("There's no recipe that correlates with the requirements, try choosing other criteria.")
    else:
        choice = random.choice(SeasonalFood)
        imgsrc = imgList[choice]
        if 'thatfijitaste' in imgsrc:
            downloadImageTaste(imgsrc)
        elif 'savoringfiji' in imgsrc:
            downloadImageSavor(imgsrc)
        CreatePDF(choice, fooddetails)


def downloadImageSavor(imgsrc):
    """
    Downloads the image from the savoring fiji data source and saves it as the title parameter
    :param:
        imgsrc (str) : a link to the desired image
    :return:
        none
    """
    image = iio.imread(imgsrc)
    iio.imwrite(f'dishimage.jpg', image)

def downloadImageTaste(imgsrc):
    """
        Downloads the image from the thatfijitaste data source and saves it as the title parameter
        :param:
            imgsrc (str) : a link to the desired image
        :return:
            none
        """
    r = requests.get(imgsrc).content
    with open(f'dishimage.jpg', 'wb') as f:
        f.write(r)

def GetFijiFacts(title):
    """
    returns facts on fiji from the country API
    :param:
        title (str) : the dish name
    :return:
        FijiText (str) : a string text about Fiji
    """
    api_url = "https://countryapi.io/api/name/fiji?apikey=SYm8ErPZikmOBTcnetralZtPtO1U82MZhDEvd1C4"
    response = requests.get(api_url)
    jason_data = json.loads(response.text)
    FijiText = f"{jason_data['fj']['name']} or {jason_data['fj']['official_name']} is a country in the region of " \
               f"{jason_data['fj']['region']}. {title} and many more meals like this are enjoyed" \
               f" by a population of {jason_data['fj']['population']} people," \
               f" their cuisine now has the change of being enjoyed by the entire world. I hope you enjoy this unique taste of the " \
               f"{jason_data['fj']['official_name']} region."
    return FijiText

def CreatePDF(choice, fooddetails):
    """
    Creates a PDF file based on the recipe given through choice and extracts the ingredients and steps from fooddetails
    :param:
        choice (str) : the name of the recipe randomly chosen by one of the 4 methods
        fooddetails : a list containing all the steps and ingredient to every recipe
    :return:
        none
    """
    title = choice
    ingredientlist = fooddetails[choice][0]
    steplist = fooddetails[choice][1]
    FijiText = GetFijiFacts(title)

    doc = SimpleDocTemplate(f"output.pdf", pagesize=letter)
    content = []
    styles = getSampleStyleSheet()

    content.append(Paragraph(title))

    imager = Image('dishimage.jpg', width=150, height=150)
    content.append(imager)

    content.append(Paragraph("<br/>Ingredients:"))

    for items in ingredientlist:
        wrapped_text = Paragraph(items, styles["Normal"])
        content.append(wrapped_text)

    content.append(Paragraph("<br/>Steps:"))

    for items in steplist:
        text = items.replace('⅓', '1/3')
        wrapped_text = Paragraph(text, styles["Normal"])
        content.append(wrapped_text)
    content.append(Paragraph("<br/>"+FijiText))

    doc.build(content)
    print("Recipe Created!")




