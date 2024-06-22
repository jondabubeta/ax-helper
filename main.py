import requests
import time
import os
import platform

# Replace with your actual Eventbrite API key
api_key = 'JHRO6CIZZJNFTVURCTZT'
event_id = '911682285257'
url = f'https://www.eventbriteapi.com/v3/events/{event_id}/ticket_classes/'

headers = {
    'Authorization': f'Bearer {api_key}',
}

previous_status = None


def play_alarm():
    from playsound import playsound
    playsound('C:/Users/jonda/PycharmProjects/EventBritePinger/resources/alarm_sound.mp3')  # Ensure you have an alarm sound file


def check_ticket_status():
    global previous_status
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            ticket_classes = response.json()
            for ticket_class in ticket_classes['ticket_classes']:
                current_status = ticket_class['on_sale_status']
                print(f"Ticket Name: {ticket_class['name']}")
                print(f"Available: {current_status}")

                if previous_status == "SOLD_OUT" and current_status != "SOLD_OUT":
                    play_alarm()

                previous_status = current_status
        else:
            print(f"Failed to retrieve ticket classes: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def ping_host(host="8.8.8.8"):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    response = os.system(" ".join(command))
    if response == 0:
        print(f"Ping to {host} successful.")
    else:
        print(f"Ping to {host} failed.")


def main():
    while True:
        ping_host()
        check_ticket_status()
        time.sleep(5)  # Wait for 5 seconds before making the next call


if __name__ == "__main__":
    main()
