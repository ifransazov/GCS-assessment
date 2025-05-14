import requests          # for API calls
from pathlib import Path # for favorite file

API_KEY = "b9b4071b038907390512a552c4bb44fc" # default API key from openweather

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
UNIT = "metric"  # or "imperial"

FAV_FILE = Path.cwd() / ".weather_favorites.txt"

curr_favorites = []

temp_favorites = ["Seattle", "Philadelphia"]

def fetch_weather(city):
    params = {"q": city, "appid": API_KEY, "units": UNIT}
    r = requests.get(BASE_URL, params=params)
    r.raise_for_status()
    d = r.json()
    return {
        "city":       d["name"],
        "temp":       d["main"]["temp"],
        "feels_like": d["main"]["feels_like"],
        "desc":       d["weather"][0]["description"],
        "humidity":   d["main"]["humidity"],
    }

def cmd_weather(city):
    
    try:
        info = fetch_weather(city)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"City '{city}' not found.")
        else:
            print(f"API error ({e.response.status_code}).")
        return
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return

    sym = "°C" if UNIT == "metric" else "°F"
    print(f"{info['city']}: {info['temp']}{sym} (feels like {info['feels_like']}°), {info['desc']}, humidity {info['humidity']}%")

def cmd_list_favorite():

    if len(curr_favorites) == 0:
        print("You do not currently have any favorites! To add a favorite run: 'add <city>'")
        return

    print("Here is your favorites list with their current weather info!")
    
    for city in curr_favorites:
        try:
            cmd_weather(city)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"City '{city}' not found in OpenWeather. Please check the name and try again.")
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")


def cmd_add_favorite(city):
    if len(curr_favorites) >= 3:
        print("Cannot add to favorites list, max size is 3. If you would like to remove a city run the command: 'remove' ")
        return
    if city in curr_favorites:
        print(f"{city} is already in favorites list!")
        return
    
    try:
        info = fetch_weather(city)
    except requests.exceptions.HTTPError as e:
        # OpenWeather sends 404 for unknown city
        if e.response.status_code == 404:
            print(f"City '{city}' not found in OpenWeather.")
        else:
            print(f"Weather API error ({e.response.status_code}): {e.response.text}")
        
        print("If you would like to still add this city to favorites type Y, if not type anything else")
        response = input("# ")
        if response == "Y":
            curr_favorites.append(city)    
            print(f"Appended {city} to list!")
        else:
            print(f"Skipped adding {city}")
        return
    
    except requests.exceptions.RequestException as e:
        # network / other errors
        print(f"Network error: {e}")
        print("If you would like to still add this city to favorites type Y, if not type anything else")
        response = input("# ")
        if response == "Y":
            curr_favorites.append(city)
            print(f"Appended {city} to list!")    
        else:
            print(f"Skipped adding {city}")
        return

    curr_favorites.append(city)
    print(f"Appended {city} to list!")

def remove_favorite():
    print("Here is your current favorites list: ")
    for city in curr_favorites:
        print(city)
    print("If you would like to remove a city enter the city name below, if you would like to exit, type: 'quit'")
    response = input("# ")
    if response == "quit":
        print("Quitting without removing any favorites")
        return
    if response in curr_favorites:
        print(f"Removing {response} from favorites list")
        curr_favorites.remove(response)
    else:
        print("Command not recognized, returning to main command line")

def switch_units():
    global UNIT
    old = UNIT
    UNIT = "imperial" if UNIT == "metric" else "metric"
    print(f"Units switched from: {old} to {UNIT}")

def help_msg():
    print("Available commands: " \
    "\n   help                              - displays available commands, " \
    "\n   weather <city>                    - shows current weather for a given city, " \
    "\n   add <city>                        - adds city to list of favorites, " \
    "\n   list                              - lists cities in favorites list with the current weather, " \
    "\n   remove                            - shows current favorites list and prompts which to remove, " \
    "\n   switch_units                      - switches between Metric and Imperial units, " \
    "\n   save                              - saves current favorites list" \
    "\n   load                              - loads last saved favorites list" \
    "\n   quit")


def save_favorites():
    print("Saving current favorite cities:")
    for city in curr_favorites:
        print(city)

    try:
        FAV_FILE.write_text("\n".join(curr_favorites))
    except Exception as e:
        print(f"Could not save favorites: {e}")
    
    print("Successfully saved favorite cities, to load on next session run: 'load'")

def load_favorites():
    return

def main():
    
    print(f"Hello! Welcome to the CLI Weather App, you are using {UNIT} units")
    help_msg()

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
        
        if cmd == "help":
            help_msg()
        
        elif cmd == "weather":
            if len(parts) < 2:
                print("Usage: weather <city>")
            else: 
                city = " ".join(parts[1:])
                cmd_weather(city)
        
        elif cmd == "add":
            if len(parts) < 2:
                print("Usage: add <city>")
            else:
                city = " ".join(parts[1:])
                cmd_add_favorite(city)
        
        elif cmd == "list":
            cmd_list_favorite()
        
        elif cmd == "remove":
            remove_favorite()
        
        elif cmd == "switch_units":
            switch_units()

        elif cmd == "save":
            save_favorites()

        elif cmd == "load":
            load_favorites()
        
        elif cmd in ("quit", "exit"):
            print("Bye!")
            break

        else:
            print(f"Unknown command '{cmd}'")
            help_msg()
    

if __name__ == "__main__":
    main()