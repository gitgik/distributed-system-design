
# Designing Twitter

Twitter is an online social networking service where users post and read short 140-character messages called "tweets". Registered Users can post and read tweets, but those not registered can only read them. 


## 1. Requirements and System Goals

### Functional Requirements
1. Users should be able to post new tweets.
2. A user should be able to follow other users.
3. Users should be able to mark tweets as favorites.
4. Tweets can contain photos and videos.
5. A user should have a timeline consting of top tweets from all the people the user follows.

### Non-functional Requirements
1. Our service needs to be highly available.
2. Acceptance latency of the sytstem is 200ms for timeline generation.
3. Consistency can take a hit (in the interest of availability); if user doesn't see a tweet for a while, it should be fine.

### Extended Requirements
1. Searching tweets.
2. Replying to a tweet.
3. Trending topics - current hot topics.
4. Tagging other users.
5. Tweet notification.
6. Suggestions on who to follow.

## Capacity Estimation and Constraints

Let's assume we have 1 billion users, with 200 million daily active users (DAU). 
Also assume we have 100 million new tweets every day, and on average each user follows 200 people.

**How many favorites per day?** If on average, each user favorites 5 tweets per day, we have:
```
200M users * 5 => 1 billion favorites.
```

**How many total tweet-views?** Let's assume on average a user visits their timeline twice a day and visits 5 other people's pages. On each page if a user sees 20 tweets, then the no. of views our system will generate is:
```
200M DAU * ((2 + 5) * 20 tweets) => 28B/day
```

#### Storage Estimates
Let's say each tweet has 140 characters and we need two bytes to store a character without compression. Assume we need 30 bytes to store metadata with each tweet (like ID, timestamps, etc.). Total storage we would need is:
```
100M new daily tweets * ((140 * 2) + 30) bytes => ~28 GB/day
```

Not all tweets will have media, let's assume that on average every fifth tweet has a photo and every tenth a video. Let's also assume on average, a photo = 0.5MB and a video = 5MB. This will lead us to have:
```
    (100M/5 photos * 0.5MB) + (100M/10 videos * 5MB) ~= 60 TB/day
```

#### Bandwidth Estimates
Since total ingress is 60TB per day, then it will translate to: 
```
60TB / (24 * 60 * 60) ~= 690 MB/sec
```
Remember we have 28 billion tweets views in a day. We must show the photo of every tweet, but let's assume that the users watch every 3rd video they see in their timeline. So, total egress will be:

```
      (28Billion * 280 bytes) / 86400 of text ==> 93MB/s
    + (28Billion/5 * 0.5MB) /  86400 of photos ==> ~32GB/s
    + (28Billion/10/3 * 5MB) / 86400 of videos ==> ~54GB/s
    
    Total ~= 85GB/sec
```


## 3. System APIs

We can have a REST API to expose the functionality of our service. 

```python
tweet(
    api_dev_key,     # (string): The API developer key. Use to throttle users based on their allocated quota.
    tweet_data,      # (string): The text of the tweet, typically up to 140 characters.
    tweet_location,  # (string): Optional location (lat, long) this Tweet refers to.
    user_location,   # (string): optional user's location.
    media_ids,       # (optional list of media_ids to associated with the tweet. (all media - photo, videos needs to be uploaded separately)
)
```
Returns: (string)
    A successful post will return the URL to access that tweet. Otherwise, return an appropriate HTTP error.


## 4. High Level System Design
We need a system that can efficiently store all the new tweets, 
i.e
- store `100M/86400sec => 1150 tweets per second` 
- and read `28billion/86400s => 325,000 tweets per second`.

It's clears that from the requirements, the system will be **read-heavy**.

At a high level:
- we need multiple application servers to serve all these requests with load balancers in front of them for traffic distribution. 
- On the backend, we need an efficent datastore that will store all the new tweets and can support huge read numbers. 
- We also need file storage to store photos and videos.

This traffic will be distributed unevenly throughout the day, though, at peak time we expect at leas a few thousand write requests and around 1M read requests per second. 
**We should keep this in mind while designing the architecture of our system.**


![](images/twitter_high_level.png)


## 5. Database Schema
We need to store data about users, their tweets, their favorite tweets, and people they follow.

![](images/twitter_db_schema.svg)

For choosing between SQL or NoSQL, check out [Designing Instagram](designing_instagram.md)


```python

```
