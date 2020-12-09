# Distributed System Design

[![Build Status](https://travis-ci.org/gitgik/distributed-system-design.svg?branch=master)](https://travis-ci.org/gitgik/distributed-system-design)
[![Code Quality](https://api.codacy.com/project/badge/Grade/0ab2d18dac654883a4d68ab6bc790c5e)](https://www.codacy.com/manual/gitgik/distributed-system-design?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=gitgik/distributed-system-design&amp;utm_campaign=Badge_Grade)

A curated collection of approaches to creating large scale distributed systems during interviews.

System Design Problems:

1. [Design Instagram](designing_instagram.ipynb)
2. [Design Twitter](designing_twitter.md)
3. [Design Twitter Search](designing_twitter_search.ipynb)
4. [Design Instagram Feed](designing_instagram_feed.ipynb)
5. [Design Youtube or Netflix](designing_youtube_or_netflix.md)
6. [Design Uber or Lyft](designing_uber_backend.md)
7. [Design a Typeahead Suggestion like Google Search](designing_typeahead_suggestion.md)
8. [Design an API Rate Limiter](designing_api_rate_limiter.ipynb)
9. [Design an E-ticketing service like Ticketmaster](designing_ticketmaster.md)
10. [Design a Web Crawler](designing_webcrawler.ipynb)
11. [Design Cloud File Storage like Dropbox/GDrive](designing-cloud-storage.ipynb)

&nbsp;

Object Oriented Design Problems:

1. [Design Amazon: Online Shopping System](OOP-design/designing_amazon_online_shopping_system.ipynb)

## Step 0: Intro

A lot of software engineers struggle with system design interviews (SDIs) primarily because of three reasons:

- The unstructured nature of SDIs is mostly an open-ended design problem that doesn’t have a standard answer.
- Their lack of experience in developing large scale systems.
- They didn't prepare for SDIs.

At top companies such as Google, FB, Amazon, Microsoft, etc., candidates who don't perform above average have a limited chance to get an offer.

Good performance always results in a better offer (higher position and salary), since it shows the candidate's ability to handle a complex system.

The steps below will help guilde you to solve mutiple complex design problems.

## Step 1: Requirements Clarifications

It's always a good idea to know the exact scope of the problem we are solving.
Design questions are mostly open-ended, that's why clarifying ambiguities early in the interview becomes critical. Since we have 30-45 minutes to design a (supposedly large system, we should clarify what parts of the system we will be focusing on.

Let's look at an example: Twitter-like service.

Here are some questions that should be answered before moving on to the next steps:

- Will users be able to post tweets and follow other people?
- Should we also design to create and display user's timeline?
- Will the tweets contain photos and videos?
- Are we focusing on the backend only or are we developing the front-end too?
- Will users be able to search tweets?
- Will there be any push notification for new or important tweets?
- Do we need to display hot trending topics?



## Step 2: System Interface definition

Define what APIs are expected from the system. This ensures we haven't gotten any requirements wrong
and establish the exact contract expected from the system.

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

For Twitter-like service, at a high-level, we need multiple application servers to serve all
read/write requests. Load balancers(LB) should be placed in front of them for traffic distributions.

Assuming we'll have more read than write traffic, we can decide to have separate servers for
handling these scenarios.

On the backend, we need an efficient Database that can store all tweets and can support a
huge number of reads.
We also need a distributed file storage system for storing static media like photos and videos.

![](images/twitter_like_high_level.png)

## Step 6: Detailed design

Dig deeper into 2-3 components; the interviewer's feedback should always guide you on what parts of the system needs further discussion.

- we should present different approaches
- present their pros and cons,
- and explain why we will prefere one approach to the other

There's no single right answer.

> The only important thing is to consider tradeoffs between different options while keeping system constraints in mind.

Questions to consider include:

- Since we will store massive amounts of data, how should we partition our data to distribute it to multiple dBs? Should we try to store all data of a user on the same DB? What issue could this cause?
- How will we handle hot users who tweet a lot or follow a lot of people?
- Since users' tieline will contain the most recent tweets, should we try to store our data in such a way that is optimized for scanning latest tweets?
- How much and at what parts should we introduce cache to speed things up?
- What components need better load balancing?

## Step 7: Identifyng and resolving bottlenecks

Discuss as many bottlenecks and the different approaches to mitigate them.

- Is there a single point of failure? What are we doing to mitigate this?
- Do we have enough replicas of data that if we lose a few servers, we can still serve our users?
- Similary, do we have enough copies of different services running such that a few failures will not cause a total system shutdown?
- How are we monitoring performance? Do we get alerts whenever critical system components fail or performance degrades?