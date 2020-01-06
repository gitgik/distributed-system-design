# Design E-Ticketing System

Let's design an online E-ticketing system that sells movie tickets.

A movie ticket booking system provides its customer the ability to purchase theatre seats online. They allows the customer to browse movies currently being played and to book available seats, anywhere anytime.

## 1. Requirements and System goals

### Functional Requirements
- The service should list different cities where its affiliated cinemas are located.
- When user selects a city, the service should display movies released in that particular city.
- When user selects movie, the service should display the cinemas running the movie plus available show times.
- Users should be able to book a show at a cinema and book tickets.
- The service should be able to show the user the seating arrangement of the cinema hall. The user should be able to select multiple seats according to the preference.
- The user should be able to distinguish between available seats from booked ones.
- Users should be able to put a hold on the seat (for 5 minutes) while they make payments.
- Users should be able to wait if there is a chance that the seats might become available (When holds by other users expire).
- Waiting customers should be serviced in a fair, first come, first serve manner.

### Non-Functional Requirements
- The service should be highly concurrent. There will be multiple booking requests for the same seat at any particular point in time.
- The system has financial transactions, meaning it should be secure and the DB should be ACID compliant.
- Assume traffic will spike on popular/much-awaited movie releases and the seats would fill up pretty fast, so the service should be highly scalable and highly available to keep up with the surge in traffic.

### Design Considerations
1. Assume that our service doesn't require authentication.
2. No handling of partial ticket orders. Either users get all the tickets they want or they get nothing.
3. Fairness is mandatory.
4. To prevent system abuse, restrict users from booking more than 10 seats at a time.

## 2. Capacity Estimation

> **Traffic estimates:** 3 billion monthly page views, sells 10 million tickets a month.
> **Storage estimates:** 500 cities, on average each city has 10 cinemas, each with 300 seats, 3 shows daily.

Let's assume each seat booking needs 50 bytes (IDs, NumberOfSeats, ShowID, MovieID, SeatNumbers, SeatStatus, Timestamp, etc) to store in the DB.
We need to store information about movies and cinemas; assume another 50 bytes.

So to store all data about all shows of all cinemas of all cities for a day

```text
        500 cities * 10 cinemas * 300 seats * 3 shows * (50 + 50) bytes = 450 MB / day
```
To store data for 5 years, we'd need around
```text
    450 MB/day * 365 * 5 = 821.25 GB
```

## 3. System APIs
Let's use REST APIs to expose the functionality of our service.

### Searching movies
```python
search_movies(
    api_dev_key: str,      #  The API developer key. This will be used to throttle users
                           #  based on their allocated quota.
    keyword: str,          # Keyword to search on.
    city: str,             # City to filter movies by.
    lat_long: str,         # Latitude and longitude to filter by.
    radius: int,           # Radius of the area in which we want to search for events.
    start_date: datetime,  # Filter with a starting datetime.
    end_date: datetime,    # Filter with an ending datetime.
    postal_code: int,      # Filter movies by postal code / zipcode.
    include_spell_check,   # (Enum: yes or no)
    result_per_page: int   # number of results to return per page. Max = 30.
    sorting_order: str     # Sorting order of the search result.
                           # Allowable values: 'name,asc', 'name,desc', 'date,asc',
                           # 'date, desc', 'distance,asc', 'name,date,asc', 'name,date,desc'
)

```
Returns: (JSON)
```json
[
  {
    "MovieID": 1,
    "ShowID": 1,
    "Title": "Klaus",
    "Description": "Christmas animation about the origin of Santa Claus",
    "Duration": 97,
    "Genre": "Animation/Comedy",
    "Language": "English",
    "ReleaseDate": "8th Nov. 2019",
    "Country": "USA",
    "StartTime": "14:00",
    "EndTime": "16:00",
    "Seats":
    [
      {
        "Type": "Regular",
        "Price": 14.99,
        "Status": "Almost Full"
      },
      {
        "Type": "Premium",
        "Price": 24.99,
        "Status": "Available"
      }
    ]
  },
  {
    "MovieID": 2,
    "ShowID": 2,
    "Title": "The Two Popes",
    "Description": "Biographical drama film",
    "Duration": 125,
    "Genre": "Drama/Comedy",
    "Language": "English",
    "ReleaseDate": "31st Aug. 2019",
    "Country": "USA",
    "StartTime": "19:00",
    "EndTime": "21:10",
    "Seats":
    [
        {
          "Type": "Regular",
          "Price": 14.99,
          "Status": "Full"
      },
        {
          "Type": "Premium",
        "Price": 24.99,
        "Status": "Almost Full"
      }
    ]
  },
 ]
 ```
 ### Reserving Seats
 ```python
reserve_seats(
    api_dev_key: str,  # API developer key.
    session_id: str,   # User Session ID to track this reservation.
                       # Once the reservation time of 5 minutes expires,
                       # user's reservation on the server will be removed using this ID.
    movie_id: str,     # Movie to reserve.
    show_id:  str,     # Show to reserve.
    seats_to_reserve: List(int)  # An array containing seat IDs to reserve.
)
```

Returns: (JSON)
```text
    The status of the reservation, which would be one of the following:
        1. Reservation Successful,
        2. Reservation Failed - Show Full
        3. Reservation Failed - Retry, as other users are holding reserved seats.
```

## 4. DB Design

1. Each **City** can have multiple **Cinema**s
2. Each **Cinema** can have multiple **Cinema_Hall**s.
3. Each **Movie** will have **Show**s and each Show will have multiple **Booking**s.
4. A **User** can have multiple **Booking**s.

&nbsp;

![](images/e_ticketing_db_design.svg)

## 5. High Level Design
From a bird's eye view,
- Web servers handle user's sessions,
- Application servers handle all the ticket management and
- stored in the DB
- as well as work with cache servers to process reservations.

![](images/e_ticketing_high_level.svg)

## 6. Detailed Component Design

Let's explore the workflow part where there are no seats available to reserve, but all seats haven't been booked yet, (some users are holding in the reservation pool and have not booked yet)
- the user is taken to a waiting page, waiting until the required seats get freed from the reservation pool. Options for the user at this point include:
- if the required number of seats become available, take the user to theatre page to choose seats
- While waiting, if all seats are booked, or there are fewer seats in the reservation pool than the user intends to book, then the user is shown the error message.
- User cancels the waiting and is taken back to the movie search page.
- At maximum, a user waits for an hour, after that the user's session expires and the user is taken back to the movie search page.

If seats are reserved successfully, the user has 5 minutes to pay for the reservation. After payment, booking is marked complete. If the user isn't able to pay within 5 minutes, all the reserved seats are freed from the reservation pool to become available to other users.

### How we'll keep track of all active reservations that have not been booked yet, and keep track of waiting customers

We need two daemon services for this:

#### a. Active Reservation Service

This will keep track of all active reservations and remove expired ones from the system.

We can keep all the reservations of a show in memory in a [Linked Hashmap](https://www.geeksforgeeks.org/linkedhashmap-class-java-examples/), in addition to also keeping data in the DB.
- We will need this doubly-linked data structure to jump to any reservation position to remove it when the booking is complete.
- The head of the HashMap will always points to the oldest record, since we will have expiry time associated with each reservation. The reservation can be expired when the timeout is reached.

To store every reservation for every show, we can have a HashTable where the `key` = `ShowID` and `value` = Linked HashMap containing `BookingID` and creation `Timestamp`.

In the DB,
- We store reservation in the `Booking` table.

- Expiry time will be in the Timestamp column.

- The `Status` field will have a value of `Reserved(1)` and, as soon as a booking is complete, update the status to `Booked(2)`.

- After status is changed, remove the reservation record from Linked HashMap of the relevant show.

- When reservation expires, remove it from the Booking table or mark it `Expired(3)`, and remove it from memory as well.

ActiveReservationService will work with the external Financial service to process user payments. When a booking is completed, or a reservation expires, WaitingUserService will get a signal so that any waiting customer can be served.

```python

# The HashTable keeping track of all active reservations
hash_table = {
    # ShowID :  # LinkedHashMap <BookingID, Timestamp>
    'showID1': {
        (1, 1575465935),
        (2, 1575465940),
        (2, 1575466950),
    },
    'showID2': { ... },
}
```

#### b. Waiting User Service

- This daemon service will keep track of waiting users in a Linked HashMap or TreeMap.
- To help us jump to any user in the list and remove them when they cancel the request.
- Since it's a first-come-first-served basis, the head of the Linked HashMap would always point to the longest waiting user, so that whenever seats become available, we can serve users in a fair manner.

We'll have a HashTable to store all waiting users for every show.
    Key = `ShowID`, value = `Linked HashMap containing UserIDs and their  start-time`

Clients can use Long Polling to keep themselves updated for their reservation status. Whenever seats become available, the server can use this request to notify the user.

#### Reservation Expiration
On the server, the Active Reservation Service keeps track of expiry of active connections (based on reservation time).

On the client, we will show a timer (for expiration time), which could be a little out of sync with the server. We can add a buffer of 5 seconds on the server to prevent the client from ever timing out after the server, which, if left unchecked, could prevent successful purchase.

## 7. Concurrency
We need to handle concurrency, such that no 2 users are able to book the same seat.

We can use transactions in SQL databases, isolating each transaction by locking the rows before we can update them. If we read rows, we'll get a write lock on the them so that they can't be updated by anyone else.

Once the DB transaction is committed and successful, we can start tracking the reservation in the Active Reservation Service.

## 8. Fault Tolerance
If the two services crash, we can read all active reservations from the Booking table.

Another option is to have a **master-slace configuration** so that, when the master crashes, the slave can take over. We are not storing the waiting users in the DB, so when Waiting User Service crashes, we don't have any means to recover the data unless we have a master-slave setup.

We can also have the same master-slave setup for DBs to make them fault tolerant.

## 9. Data Partitioning
Partitioning by MovieID will result in all Shows of a Movie being in a single server.
For a hot movie, this could cause a lot of load on that server. A better approach would be to partition based on ShowID; this way, the load gets distributed among different servers.

We can use Consistent Hashing to allocate application servers for both (ActiveReservationService and WaitingUserService) based on `ShowID`. This way, all waiting users of a particular show will be handled by a certain set of servers.

**When a reservation expires, the server holding that reservation will:**

1. Update DB to remove the expired Booking (or mark it `Expired(3)` and update the seats status in `Show_Seats` table.
2. Remove the reservation from Linked HashMap.
3. Notify the user that their reservation expired.
4. Broadcast a message to `WaitingUserService` servers that are holding waiting users of that Show to find who the longest waiting user is. Consistent Hashing scheme will help tell what servers are holding these users.
5. Send a message to the `WaitingUserService` to go ahead and process the longest waiting user if required seats have become available.

**When a reservation is successful:**
1. The server holding that reservation will send a message to all servers holding waiting users of that Show.
2. These servers upon receiving the above message, will query the DB (or a DB cache) to find how many seats are available.
3. The servers can now expire all waiting users that want to reserve more seats than the available seats.
4. For this, the WaitingUSerService has to iterate through the Linked HashMap of all the waiting users to remove them.
