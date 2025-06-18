import json
import os
from datetime import datetime, timedelta

# Filenames for storing bookings and seat availability data persistently
BOOKING_FILE = "bookings.json"
SEATS_FILE = "seats.json"

# Dictionary containing movies and their available showtimes
movies = {
    "RRR": ["6:00 PM", "9:00 PM"],
    "Pushpa": ["5:00 PM", "8:00 PM"],
    "Bahubali": ["2:00 PM", "5:00 PM"]
}

# List of seat labels from A1 to A10
ALL_SEATS = [f"A{i}" for i in range(1, 11)]

def print_line():
    # Helper function to print a separator line for UI clarity
    print("-" * 50)

def generate_dates():
    # Generates a list of 3 dates starting from 2025-06-15
    start = datetime.strptime("2025-06-15", "%Y-%m-%d")
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(3)]

def load_bookings():
    # Loads existing bookings from JSON file if it exists
    if os.path.exists(BOOKING_FILE):
        with open(BOOKING_FILE, "r") as f:
            return json.load(f)
    # Returns empty list if file doesn't exist
    return []

def save_bookings(bookings):
    # Saves the current bookings list into the JSON file
    with open(BOOKING_FILE, "w") as f:
        json.dump(bookings, f, indent=4)

def load_seats():
    # Loads the seat availability data if the file exists
    if os.path.exists(SEATS_FILE):
        with open(SEATS_FILE, "r") as f:
            return json.load(f)
    # If no file exists, initialize the seats dictionary for all movies, dates, and times with False (not booked)
    seats = {}
    for movie in movies:
        seats[movie] = {}
        for date in generate_dates():
            seats[movie][date] = {}
            for time in movies[movie]:
                seats[movie][date][time] = {seat: False for seat in ALL_SEATS}
    return seats

def save_seats(seats):
    # Saves the current seat booking status into a JSON file
    with open(SEATS_FILE, "w") as f:
        json.dump(seats, f, indent=4)

def select_date():
    # Displays available dates and asks user to select one
    dates = generate_dates()
    print("Available Dates:")
    for i, d in enumerate(dates, 1):
        print(f"{i}. {d}")
    while True:
        try:
            choice = int(input("Select date number: "))
            if 1 <= choice <= len(dates):
                return dates[choice - 1]
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")

def show_movies_for_date(date):
    # Shows the movies available on the selected date along with their showtimes
    print(f"\nMovies on {date}:")
    for i, (movie, times) in enumerate(movies.items(), 1):
        print(f"{i}. {movie} | Showtimes: {', '.join(times)}")
    return list(movies.keys())

def select_movie(movie_list):
    # Allows user to select a movie from the list shown
    while True:
        try:
            choice = int(input("Enter movie number: "))
            if 1 <= choice <= len(movie_list):
                return movie_list[choice - 1]
        except:
            pass
        print("Invalid input.")

def select_time(movie):
    # Shows available showtimes for the selected movie and lets user choose one
    times = movies[movie]
    print("Available Showtimes:")
    for i, t in enumerate(times, 1):
        print(f"{i}. {t}")
    while True:
        try:
            choice = int(input("Select time number: "))
            if 1 <= choice <= len(times):
                return times[choice - 1]
        except:
            pass
        print("Invalid input.")

def show_available_seats(seat_data):
    # Prints seat availability status: ✓ for available, X for booked
    print("Available Seats:")
    for seat in ALL_SEATS:
        status = "✓" if not seat_data[seat] else "X"
        print(f"{seat}({status})", end="  ")
    print("\n✓ = Available | X = Booked")

def book_ticket(bookings, seats):
    # Main booking flow: date, movie, time, seats, and payment selection
    print_line()
    date = select_date()
    movie_list = show_movies_for_date(date)
    movie = select_movie(movie_list)
    time = select_time(movie)

    seat_data = seats[movie][date][time]
    available = [s for s, b in seat_data.items() if not b]

    if not available:
        print("No seats available.")
        return

    show_available_seats(seat_data)

    name = input("Enter your name: ").strip()
    while True:
        try:
            num_tickets = int(input(f"Enter number of tickets (1-{len(available)}): "))
            if 1 <= num_tickets <= len(available):
                break
        except ValueError:
            pass
        print("Invalid number.")

    selected = []
    for i in range(num_tickets):
        while True:
            seat = input(f"Select seat {i + 1} (e.g., A1): ").upper()
            if seat in available and seat not in selected:
                selected.append(seat)
                break
            else:
                print("Seat not available or already selected.")

    print("Payment Methods: 1. Card  2. Cash  3. PhonePe")
    pay_options = {"1": "Card", "2": "Cash", "3": "PhonePe"}
    while True:
        pay = input("Choose payment method: ")
        if pay in pay_options:
            payment_method = pay_options[pay]
            break
        print("Invalid choice.")

    # Mark selected seats as booked (True)
    for seat in selected:
        seat_data[seat] = True

    # Add booking details to bookings list
    bookings.append({
        "name": name,
        "movie": movie,
        "date": date,
        "time": time,
        "seats": selected,
        "payment": payment_method
    })

    # Save bookings and seat status to files
    save_bookings(bookings)
    save_seats(seats)

    print_line()
    print(f"Booking confirmed for {name}")
    print(f"{movie} | {date} at {time} | Seats: {', '.join(selected)}")
    print(f"Paid via: {payment_method}")
    print_line()

def view_bookings(bookings):
    # Display all existing bookings with details
    print_line()
    if not bookings:
        print("No bookings yet.")
    for i, b in enumerate(bookings, 1):
        print(f"{i}. {b['name']} | {b['movie']} | {b['date']} | {b['time']} | Seats: {', '.join(b['seats'])} | Payment: {b['payment']}")
    print_line()

def cancel_booking(bookings, seats):
    # Allows user to cancel a booking by selecting from the list
    view_bookings(bookings)
    if not bookings:
        return
    try:
        choice = int(input("Enter booking number to cancel: ")) - 1
        if 0 <= choice < len(bookings):
            b = bookings.pop(choice)
            # Mark seats as available again
            for seat in b['seats']:
                seats[b['movie']][b['date']][b['time']][seat] = False
            save_bookings(bookings)
            save_seats(seats)
            print(f"Cancelled booking for {b['name']}")
    except:
        print("Invalid input.")

def main():
    # Load existing bookings and seats or initialize them
    bookings = load_bookings()
    seats = load_seats()
    while True:
        print("\nTicket Booking System")
        print_line()
        print("1. Book Ticket")
        print("2. View Bookings")
        print("3. Cancel Booking")
        print("4. Exit")
        print_line()
        choice = input("Choose an option: ")
        if choice == '1':
            book_ticket(bookings, seats)
        elif choice == '2':
            view_bookings(bookings)
        elif choice == '3':
            cancel_booking(bookings, seats)
        elif choice == '4':
            print("Thank you! Goodbye.")
            break
        else:
            print("Invalid choice.")

# Run the program only if this script is executed directly
if __name__ == "__main__":
    main()
