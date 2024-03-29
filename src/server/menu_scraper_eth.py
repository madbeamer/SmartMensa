import requests
import os
import json
from time import sleep
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

##############################################################################################################################

# Define Pydantic models for parsing the JSON data
class MealPriceArrayItem(BaseModel):
    price: float
    customer_group_code: int = Field(..., alias='customer-group-code')
    customer_group_position: int = Field(..., alias='customer-group-position')
    customer_group_desc: str = Field(..., alias='customer-group-desc')
    customer_group_desc_short: str = Field(..., alias='customer-group-desc-short')

class MealClassArrayItem(BaseModel):
    code: int
    position: int
    desc_short: str = Field(..., alias='desc-short')
    desc: str

class AllergenArrayItem(BaseModel):
    code: int
    position: int
    desc_short: str = Field(..., alias='desc-short')
    desc: str

class OriginArrayItem(BaseModel):
    code: int
    position: int
    desc_short: str = Field(..., alias='desc-short')
    desc: str

class MeatTypeArrayItem(BaseModel):
    code: int
    position: int
    desc_short: str = Field(..., alias='desc-short')
    desc: str
    origin_array: List[OriginArrayItem] = Field(..., alias='origin-array')

class OriginArrayItem1(BaseModel):
    code: int
    position: int
    desc_short: str = Field(..., alias='desc-short')
    desc: str

class FishingMethodArrayItem(BaseModel):
    code: int
    position: int
    desc_short: str = Field(..., alias='desc-short')
    desc: str
    origin_array: List[OriginArrayItem1] = Field(..., alias='origin-array')

class Meal(BaseModel):
    line_id: int = Field(..., alias='line-id')
    name: str
    description: str
    price_unit_code: int = Field(..., alias='price-unit-code')
    price_unit_desc: str = Field(..., alias='price-unit-desc')
    price_unit_desc_short: str = Field(..., alias='price-unit-desc-short')
    meal_price_array: List[MealPriceArrayItem] = Field(..., alias='meal-price-array')
    meal_class_array: Optional[List[MealClassArrayItem]] = Field(
        None, alias='meal-class-array'
    )
    allergen_array: Optional[List[AllergenArrayItem]] = Field(None, alias='allergen-array')
    meat_type_array: Optional[List[MeatTypeArrayItem]] = Field(
        None, alias='meat-type-array'
    )
    fishing_method_array: Optional[List[FishingMethodArrayItem]] = Field(
        None, alias='fishing-method-array'
    )

class LineArrayItem(BaseModel):
    name: str
    meal: Optional[Meal] = None

class MealTimeArrayItem(BaseModel):
    name: str
    time_from: str = Field(..., alias='time-from')
    time_to: str = Field(..., alias='time-to')
    line_array: List[LineArrayItem] = Field(..., alias='line-array')

class OpeningHourArrayItem(BaseModel):
    time_from: str = Field(..., alias='time-from')
    time_to: str = Field(..., alias='time-to')
    meal_time_array: List[MealTimeArrayItem] = Field(..., alias='meal-time-array')

class DayOfWeekArrayItem(BaseModel):
    day_of_week_code: int = Field(..., alias='day-of-week-code')
    day_of_week_desc: str = Field(..., alias='day-of-week-desc')
    day_of_week_desc_short: str = Field(..., alias='day-of-week-desc-short')
    opening_hour_array: Optional[List[OpeningHourArrayItem]] = Field(
        None, alias='opening-hour-array'
    )

class WeeklyRotaArrayItem(BaseModel):
    weekly_rota_id: int = Field(..., alias='weekly-rota-id')
    facility_id: int = Field(..., alias='facility-id')
    valid_from: str = Field(..., alias='valid-from')
    valid_to: Optional[str] = Field(None, alias='valid-to')  # Making valid_to optional
    day_of_week_array: List[DayOfWeekArrayItem] = Field(..., alias='day-of-week-array')

class Model(BaseModel):
    weekly_rota_array: List[WeeklyRotaArrayItem] = Field(..., alias='weekly-rota-array')

##############################################################################################################################

# Define a function to translate the day of the week from German to English

def translate_day_of_week(day_of_week):
    if day_of_week == 'Montag':
        return 'Monday'
    elif day_of_week == 'Dienstag':
        return 'Tuesday'
    elif day_of_week == 'Mittwoch':
        return 'Wednesday'
    elif day_of_week == 'Donnerstag':
        return 'Thursday'
    elif day_of_week == 'Freitag':
        return 'Friday'
    elif day_of_week == 'Samstag':
        return 'Saturday'
    elif day_of_week == 'Sonntag':
        return 'Sunday'
    else:
        return day_of_week
    
##############################################################################################################################

# Define a function to parse the JSON data to a dictionary and save it as a JSON file

def parseToJson(url, facility_id):
    # Fetch the webpage content
    response = requests.get(url)
    if response.status_code == 200:
        print(f'{"STATUS:":<15} Page successfully accessed!')
    else:
        print("Failed to fetch the webpage.")
        return None
    parsed_data = Model(**json.loads(response.content))

    # Initialize an empty dictionary to store the extracted data
    menu_details_per_day = {}

    # Loop through the parsed data to extract menu names and their meal details per weekday
    for weekly_rota in parsed_data.weekly_rota_array:
        for day_of_week in weekly_rota.day_of_week_array:
            day_of_week_menu = translate_day_of_week(day_of_week.day_of_week_desc)
            menu_details_per_day[day_of_week_menu] = {"Lunch": [], "Dinner": []}  # Initialize Lunch and Dinner lists for the day
            
            for opening_hour in day_of_week.opening_hour_array or []:
                for meal_time in opening_hour.meal_time_array:
                    for line in meal_time.line_array:
                        # Check if line has meal information
                        if hasattr(line, 'meal') and line.meal:
                            meal_name = line.meal.name if hasattr(line.meal, 'name') else ""
                            meal_description = line.meal.description if hasattr(line.meal, 'description') else ""
                            allergens = [allergen.desc for allergen in line.meal.allergen_array] if line.meal and line.meal.allergen_array else []
                            meal_class = [meal_class.desc for meal_class in line.meal.meal_class_array] if line.meal and line.meal.meal_class_array else []
                        else:
                            meal_name = ""
                            meal_description = ""
                            allergens = []
                            meal_class = []
                        
                        # Check for meat-type-array and fishing-method-array
                        meat_info = []
                        fish_info = []

                        if line.meal and line.meal.meat_type_array:
                            for meat_type_item in line.meal.meat_type_array:
                                meat_desc = meat_type_item.desc
                                meat_origin = [origin.desc for origin in meat_type_item.origin_array] if meat_type_item.origin_array else []
                                meat_info.append({"type": meat_desc, "origin": meat_origin})

                        if line.meal and line.meal.fishing_method_array:
                            for fishing_method_item in line.meal.fishing_method_array:
                                fish_desc = fishing_method_item.desc
                                fish_origin = [origin.desc for origin in fishing_method_item.origin_array] if fishing_method_item.origin_array else []
                                fish_info.append({"desc": fish_desc, "origin": fish_origin})

                        # Extract price information for students, internals, and externals
                        price_info = {}
                        if hasattr(line, 'meal') and line.meal:
                            for price_item in line.meal.meal_price_array:
                                if price_item.customer_group_desc.lower() == 'students' or 'studierende' in price_item.customer_group_desc.lower():
                                    price_info['students'] = price_item.price
                                elif price_item.customer_group_desc.lower() == 'internal' or 'interne' in price_item.customer_group_desc.lower():
                                    price_info['internal'] = price_item.price
                                elif price_item.customer_group_desc.lower() == 'external' or 'extern' in price_item.customer_group_desc.lower():
                                    price_info['external'] = price_item.price
                                elif price_item.customer_group_desc.lower() == 'all visitors' or 'alle besucher' in price_item.customer_group_desc.lower():
                                    price_info['students'] = price_item.price
                                    price_info['internal'] = price_item.price
                                    price_info['external'] = price_item.price

                        # Replace \n with " "
                        meal_description = meal_description.replace('\n', ' ')

                        meal_info = {
                            "line_name": line.name,
                            "meal_name": meal_name,
                            "meal_description": meal_description,
                            "allergens": allergens,
                            "meal_class": meal_class,
                            "meat_info": meat_info,
                            "fish_info": fish_info,
                            "price_info": price_info
                        }
                        
                        # Categorize meals into Lunch and Dinner based on meal-time-array.name
                        meal_time_name = meal_time.name
                        if "lunch" in meal_time_name.lower() or "mittagessen" in meal_time_name.lower() or "mittag" in meal_time_name.lower():
                            menu_details_per_day[day_of_week_menu]["Lunch"].append(meal_info)
                        else:
                            menu_details_per_day[day_of_week_menu]["Dinner"].append(meal_info)

    print(f'{"STATUS:":<15} Menus of facility {facility_id} successfully crawled!')

    # Define the subfolder name
    subfolder = 'menus-as-json'

    # Check if the subfolder exists, if not, create it
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    # Path to the file in the subfolder
    file_path = os.path.join(subfolder, f'menus-facility-{facility_id}.json')

    # Save the extracted data as a JSON file
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(menu_details_per_day, json_file, indent=2, ensure_ascii=False)

    print(f'{"STATUS:":<15} menus-facility-{facility_id}.json successfully stored!')

##############################################################################################################################

# Compute the date range for the current week
def compute_date_range():
    # Get today's date and time in UTC
    today_utc = datetime.utcnow()

    # Shift UTC time to UTC+01:00 for Europe/Zurich
    utc_offset = timedelta(hours=1)
    today_zurich = today_utc + utc_offset

    # Calculate the difference between today in Zurich and the previous Monday
    days_since_monday = today_zurich.weekday()
    days_to_previous_monday = (7 + days_since_monday) % 7
    previous_monday = today_zurich - timedelta(days=days_to_previous_monday)

    # Calculate the next Monday
    next_monday = previous_monday + timedelta(weeks=1)

    # Format the dates
    valid_after = previous_monday.strftime("%Y-%m-%d")
    valid_before = next_monday.strftime("%Y-%m-%d")
    return valid_after, valid_before

##############################################################################################################################

def main():
    # Generate the URL for the current week for each facility
    def generate_url(facility_id, valid_after, valid_before, language):
        return f'https://idapps.ethz.ch/cookpit-pub-services/v1/weeklyrotas/?client-id=ethz-wcms&lang={language}&rs-first=0&rs-size=50&valid-after={valid_after}&valid-before={valid_before}&facility={facility_id}'
    
    # Define the facility IDs for the different ETHZ facilities
    facility_ids = [ 3, 5, 7, 8, 9, 10, 11,  # Zentrum
                    14, 16, 17, 18, 19, 20, 21, 22,  # Hönggerberg
                    23  # Oerlikon
                    ]
    
    valid_after, valid_before = compute_date_range()

    language = "de"
    
    for facility_id in facility_ids:
        print(f'{ "FACILITY ID:":<15} Processing facility {facility_id}...')
        url = generate_url(facility_id, valid_after, valid_before, language)
        parseToJson(url, facility_id)
        sleep(1)
        
    print(f'{"STATUS:":<15} All ETH menus successfully stored!')

if __name__ == "__main__":
    main()
