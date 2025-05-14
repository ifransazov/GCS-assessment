import requests          # for API calls
from pathlib import Path # for favorites file

### 
### Ivan Fransazov
###
### Below is my completed Activity 1 for the GCS Coding Assessment that leverages the OpenWeather API
### to create a command line interface weather app. I store favorited cities between sessions 
### via the weather_favorites.txt file, it comes pre-loaded with Seattle and Philadelphia
###

API_KEY = "b9b4071b038907390512a552c4bb44fc" # default API key from openweather I generated

BASE_URL = "https://api.openweathermap.org/data/2.5/weather" # URL used for the API calls

UNIT = "metric"

FAV_FILE = Path.cwd() / "weather_favorites.txt" # location of the favorites file

curr_favorites = [] # session-local list of favorite cities

###
### fetch_weather is a helper function that fetches the weather from OpenWeather given a city as a string
### I decided to put the try/catch blocks in other functions to give better error messages
###
def fetch_weather(city):
    params = {"q": city, "appid": API_KEY, "units": UNIT}
    r = requests.get(BASE_URL, params=params, timeout=5)
    r.raise_for_status()
    try:
        d = r.json()
    except ValueError:
        print("Server returned invalid JSON.")
        raise

    return {
        "city":       d["name"],
        "temp":       d["main"]["temp"],
        "feels_like": d["main"]["feels_like"],
        "desc":       d["weather"][0]["description"],
        "humidity":   d["main"]["humidity"],
    }

###
### cmd_weather calls fetch_weather given a city string and formats a nice output for the user to read
###
def cmd_weather(city):
    
    try:
        info = fetch_weather(city)
    except requests.exceptions.HTTPError as e: # catches API call errors, 404 means city not found
        if e.response.status_code == 404:
            print(f"City '{city}' not found. Please check spelling and try again.")
        else: # another API error
            print(f"API error ({e.response.status_code}).")
        return
    except requests.exceptions.RequestException as e: # network error
        print(f"Network error: {e}")
        return

    sym = "°C" if UNIT == "metric" else "°F"
    print(f"{info['city']}: {info['temp']}{sym} (feels like {info['feels_like']}{sym}), {info['desc']}, humidity {info['humidity']}%")

###
### cmd_list_favorite will calls cmd_weather on all cities inside of the curr_favorites list
###
def cmd_list_favorite():
    # case handling
    # if no favorited cities, return early with a message
    if len(curr_favorites) == 0:
        print("You do not currently have any favorites! To add a favorite run: 'add <city>'")
        return
    
    print("Here is your favorites list with their current weather info!\n")
    
    for city in curr_favorites:
        cmd_weather(city)
    print() # make list easier to read

###
### cmd_add_favorite will add a city to the favorites list given that it does not already exist in the list,
### and that the list does not already contain 3 other cities. Once the list has been altered it will also save to the text file
### 
### I also decided that if the city is not found by the API to let the user know, but still provide the add option for them.
###
def cmd_add_favorite(city):
    
    # case handling
    # if there are already 3 other favorited cities, let user know
    if len(curr_favorites) >= 3:
        print("Cannot add to favorites list, max size is 3. If you would like to remove a city run the command: 'remove' ")
        return
    # if city already exists in list
    if city in curr_favorites:
        print(f"{city} is already in favorites list!")
        return
    
    # check that city exists in API
    try:
        info = fetch_weather(city)
    except requests.exceptions.HTTPError as e:
        # OpenWeather sends 404 for unknown city
        if e.response.status_code == 404:
            print(f"City '{city}' not found in OpenWeather.")
        else:
            print(f"Weather API error ({e.response.status_code}): {e.response.text}")
        
        # allow user to still add city to list even if API failed
        print("If you would like to still add this city to favorites type Y, if not type anything else")

        # wrap user input in try/catch to catch ctrl+c for nice exit
        try:
            response = input("# ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return
        
        if response == "Y":
            curr_favorites.append(city)    
            save_favorites()
            print(f"Appended {city} to list!")
            return

        else:
            print(f"Skipped adding {city}")
        return
    
    # if there is a network error, still allow user to add city to the list same as if there was an API error
    except requests.exceptions.RequestException as e:
        # network / other errors
        print(f"Network error: {e}")

        print("If you would like to still add this city to favorites type Y, if not type anything else")
        
        # wrap user input in try/catch for nice exit
        try:
            response = input("# ").strip() # to ignore extra white space
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return
        
        if response == "Y":
            curr_favorites.append(city)
            save_favorites()
            print(f"Appended {city} to list!")
            return

        else:
            print(f"Skipped adding {city}")
        return

    # if no cases need handling, add city directly
    curr_favorites.append(city)
    save_favorites()
    print(f"Appended {city} to list!")

###
### remove_favorite allows the user to remove a favorited city from the list by first providing the list upfront
### and then the user type one in to be removed, once the list has been altered it will be saved automatically
###
def remove_favorite():
    # case handling
    # if there are no favorited cities, display message and exit
    if len(curr_favorites) == 0:
        print("Favorites list is empty! If you would like to add a favorite, run: 'add <city>'")
        return
    
    # provide the current favorites list
    print("Here is your current favorites list: ")
    for city in curr_favorites:
        print("   ", city)
    print("If you would like to remove a city enter the city name below, if you would like to exit, type: 'quit'")
    
    # wrap user input in try/catch for nice exit message
    try:
        response = input("# ").strip() # strips to ignore extra white space
    except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return
    
    if response == "quit":
        print("Quitting without removing any favorites")
        return
    
    # if the city they wish to remove exists in the favorites list, then remove it and exit
    if response in curr_favorites:
        print(f"Removing {response} from favorites list")
        curr_favorites.remove(response)
        save_favorites() # saves mutation to favorites text file
        return
    # otherwise, command is not a city in the list or quit, display message and exit
    else:
        print("Command/City not recognized, returning to main command line")
        return

###
### switch_units switches the unit between metric and imperial and displays a message for the user
###
def switch_units():
    global UNIT
    old = UNIT
    UNIT = "imperial" if UNIT == "metric" else "metric"
    print(f"Units switched from: {old} to {UNIT}")

###
### help_msg just prints a long string formatted nicely for the user to see the available commands with their descriptions
###
def help_msg():
    print("Available commands: " \
    "\n   help                              - displays available commands, " \
    "\n   weather <city>                    - shows current weather for a given city, " \
    "\n   add <city>                        - adds city to list of favorites and saves, " \
    "\n   list                              - lists cities in favorites list with the current weather, " \
    "\n   remove                            - shows current favorites list and prompts which to remove then saves, " \
    "\n   switch_units                      - switches between Metric and Imperial units, " \
    "\n   save                              - saves current favorites list" \
    "\n   load                              - loads last saved favorites list" \
    "\n   quit                              - quits the CLI")

###
### save_favorites will save the current favorites list into the weather_favorites.txt file
### I decided not to prevent users from saving an empty list
###
def save_favorites():
    print("Saving current favorite cities:")
    for city in curr_favorites:
        print("   ", city)

    try:
        FAV_FILE.write_text("\n".join(curr_favorites))
    except Exception as e:
        print(f"Could not save favorites: {e}")
    
    print("Successfully saved favorite cities, to load on next session run: 'load'")

###
### load_favorites will overwrite the curr_favorites list with the contents from weather_favorites.txt
### if there is no favorites file, it will do nothing
###
def load_favorites():
    global curr_favorites
    if FAV_FILE.exists():
        lines = FAV_FILE.read_text().splitlines()
        curr_favorites = [c.strip() for c in lines if c.strip()]
        print(f"Loaded favorites: {curr_favorites}")
    else:
        print("No favorites file found; doing nothing.")


###
### main displays the initial welcome message with the app name, current units, help message, and attempts to load favorites
### then it goes into a perpetual while loop with replies from the user to interact as they please until they quit
###
def main():
    
    # welcome message
    print(f"Hello! Welcome to the CLI Weather App, you are using {UNIT} units, attempting to load previous favorites")
    help_msg()
    load_favorites() # load previous favorites

    # reply loop between user input and CLI functions
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        parts = line.strip().split()
        
        if not parts:
            continue

        cmd = parts[0].lower()
        
        if cmd == "help": # display help message
            help_msg()
        
        elif cmd == "weather": # display weather given a city
            if len(parts) < 2: # if command does not contain a second part, display proper usage
                print("Usage: weather <city>")
            else: 
                city = " ".join(parts[1:]) # if there is a second part, get the second string as the city
                cmd_weather(city)
        
        elif cmd == "add": # add a city to favorites list
            if len(parts) < 2: # if command does not contain a second part, display proper usage
                print("Usage: add <city>")
            else:
                city = " ".join(parts[1:]) # if there is a second part, get the second string as the city
                cmd_add_favorite(city)
        
        elif cmd == "list": # list all favorited cities with their current weather
            cmd_list_favorite()
        
        elif cmd == "remove": # remove a city from the favorites list
            remove_favorite()
        
        elif cmd == "switch_units": # switch units between metric/imperial
            switch_units()

        elif cmd == "save": # save current favorites list to txt file
            save_favorites()

        elif cmd == "load": # load txt file into current favorites
            load_favorites()
        
        elif cmd in ("quit", "exit"): # quit while loop
            print("Bye!")
            break

        else:
            print(f"Unknown command '{cmd}'") #unknown input, display help message again
            help_msg()
    

if __name__ == "__main__":
    main()