# distributed-system-design
A curated collection of approaches to creating large scale distributed systems during interviews.

## Step 1: Requirements Clarifications
It's always a good idea to know the exact scope of the problem we are solving. 
Design questions are mostly open-ended, that's why clarifying ambiguities early in the interview becomes critical. Since we have 30-45 minutes to design a (supposedly large system, we should clarify what parts of the system we will be focusing on.

Let's look at an example: Twitter-like service.

Here are some questions that should be answered before moving on to the next steps:
- Will users be able to post tweets and follow other people?
- Should we also design to create and display user's timeline?
- Will the tweets contain photos and videos?
- Are we focusong on the backend only or are we developing the front-end too?
- Will users be able to search tweets?
- Will there be any push notification for new or important tweets?
- Do we need to display hot trending topics?



## Step 2: System Interface definition
Defin what APIs are expected from the system. This will ensure we haven't gotten any requirements wrong and establish that exact contract expected from the system.

Example:
```python
post_tweet(
    user_id,
    tweet_data,
    tweet_location,
    user_location,
    timestamp, ...
)
```

```python
generate_timeline(user_id, current_time, user_location, ...)
```

```python
mark_tweet_favorite(user_id, tweet_id, timestamp, ...)
```


## Step 3: Back-of-the-envelope estimation
It's always a good idea to estimate the scale of the system we're going to design. This will help later when we focus on scaling, partitioning, load balancing and caching.

- What scale is expected from the system? (no. of tweets/sec, no. of views/sec ...)
- How much storage will we need? We will have different numbers if user can have photos and videos in their tweets.
- What network bandwidth usage are we expecting? Crucial in deciding how we will manage traffic and balance load between servers.


## Step 4: Defining data model
This will clarify how the data flows among different components in the system.
Later, it will guide towards data partitioning and management. The candidate should identity various system entities, how they interact with each other, and different aspect of data management like storage, transportation, encryption, etc.

Examples for a Twitter-like service:
 - User: user_id, name, email, date_of_birth, created_at, last_login, etc.
 - Tweet: tweet_id, contentm tweet_location, number_of_likes, timestamp, etc.
 - UserFollowers: user_id1, user_id2
 - FavoriteTweets: user_id, tweet_id, timestamp
 
 > Which database system should be use? Will NoSQL best fit our needs, or should we use a MySQL-like relational DB? What kind of block storage should we use to store photos and videos?
 
 ## Step 5: High-level Design
 Draw a block diagram with 5-6 boxes representing the core system components. We should identify enough components that are needed to solve the problem from end-to-end.
 
For Twitter-like service, at a high-level, we need multiple application servers to serve all read/write requests with load balancers in from of them for traffic distributions. 
 
Assuming we'll have more read than write traffic, we can decide to have separate servers for handling these scenarios.

On the backend, we need an efficient DB that can store all tweets and can support a huge number of reads. We also need a distributed file storage system for storing static media like photos and videos.

![](images/twitter_like_high_level.png)