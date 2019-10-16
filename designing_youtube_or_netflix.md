
# Designing Youtube or Netflix
Let's design a video sharing service like Youtube where users will be able to upload/view/search videos.

Similar Services: Netflix, Vimeo

## 1. Requirements and Goals of the System

#### Functional Requirements:
1. Users should be able to upload videos.
2. Users should have ability to share and view videos.
3. Users should be able to perform searches based on video titles.
4. Service should have starts on videos, e.g likes/dislikes, no. of views, etc.
5. Users should be able to add and view comments on videos


#### Non-Functional Requirements:
- System should be highly reliable, any video uploaded should never be lost.
- System should be highly available.
- Users should have a real time experience while watching videos and shoult not feel any lag.


## 2. Capacity Estimation and Constraints

Assume we have 1 billion total users, 800 million daily active. If on average a user views 5 videos per day, then the total video views per second is:

```
800000000 * 5 / (60 * 60 * 24) ==> ~46000 videos/sec
```

Now, let's assume our upload:view ratio is 1:200 (For every video upload, we have 200 videos viewed)
The number of videos uploaded per second is:

```
46000 / 200 => 230 videos/sec
```


**Storage Estimates:** Lets assume 500 hours of video per minute are uploaeded. If on average, one minute of video needs 50MB of storage(videos need to be stored in multiple formats), then total storage is:

```
500 hours * 60 min * 50 MB => 1500 GB/min OR 25GB/sec
```

We are ignoring video compression and replication, which would change our storage estimates.

**Bandwidth Estimates:** 500 videos/min of uploads, and assuming each video takes a bandwidth of 10 MB/min, we would be getting:

```
500 hours * 60 mins * 10 MB ==> 300 GB/min == 5GB/sec
```

With upload:view ratio being 1:200, we would need 
`200 * 5GB/sec ==> 1TB/s` outgoing bandwidth.

## 3. System APIs
We can have a RESTful API to expose the functionality of our service.

#### Uploading a video
```python
upload_video(
    api_dev_key,  # (string): API developer key of registered account.
    video_title,  # (string): Title of the video.
    video_desc,   # (string): Optional description of video.
    tags,         # (string): Optional tags for the video.
    category_id,  # (string): Category of the video, e.g Song, Docuseries, etc.
    default_language,   # (string): English, Mandarin, Fr, etc.
    recording_details,  # (string): Location where video was recorded.
    video_contents      # (stream): Video to be uploaded.
)

```
Returns:
(string):
A successful upload will return HTTP 202 (request accepted) and once the video encoding is completed the user is notified through email with a link to access the video.

#### Searching video
```python
search_video(
    api_dev_key,
    search_query,   # (string): containing the search term
    user_location,  # (string): optional location of user performing search
    maximum_videos_to_return,  # (number): max number of results returned in one request
    page_token      # (string): This token specifies a page in the result set to be returned
)
```
Returns: (JSON)

A JSON containing informaiton about the list of video resources matching the search query.
Each resource will have a video title, a video creation date, and a view count.

#### Streaming video
```python
stream_video(
    api_dev_key, 
    video_id,   # (string): unique ID of the video
    offset,     # (number): time in offset from the beginning of the video. If we support
                # pausing a video from multiple devices, we need to store the offset.
                # This enables the user to pick up watching a video where they left from.
    codec,      # (string): 
    resolution  # (string): Imagine watching a video on TV app, pausing it, then resuming on
                # Netflix mobile app, you'll need codec and resolution, as both devices have
                # different resolution and use a different codec.
)
```
Returns: (STREAM)
A media stream (video chunk) from the given offset.


## 4. High Level Design
At a high-level we would need the following components:
1. **Processing Queue:**: Each uploaded video will be pushed to a processing queue ot be de-queued later for encoding, thumbnail generation, and storage.
2. **Encoder:** To encode each uploaded video into multiple formats.
3. **Thumbnails generator:** To generate thumbnails for each video.
4. **Video and Thumbnail storage:** To store video and thumbnail files in some distributed file storage.
5. **User DB:** To store user's info e.g name, email, address, etc.
6. **Video metadata storage:** A metadata DB to store information about videos like title, its file path, uploading user, total views, likes, comments etc. 

![](images/hld_youtube.png)

## 5. Database Schema

#### Video metadata storage - MySQL
- VideoID
- Title
- Description
- Size
- Thumbnail
- Uploader/User
- Total likes
- Total dislikes
- Total views

For each video comment, we nneed to store:
- CommentID
- VideoID
- UserID
- Comment
- CreatedAt

#### User data storage - MySQL
* UserID, Name, email, address, age, registration details etc

## 6. Detailed Component Design
The service will be read-heavy, since more people are viewing than uploading videos. We'll focus on building a system that can retrieve videos quickly. We can expect a read:write ratio of 200:1.

#### Where would videos be stored?
Videos can be stored in a distributed file storage system like HDFS or GlusterFS.

#### Hows should we efficiently manage read traffic?
We should seperate read from write traffic. We can distribute our read traffic on different servers, since we will have multiple copies of each video.
For metadata, we can have a master-slave config where writes go to master first and then gets applied at all the slaves. Such configurations can cause some staleness in data, e.g., when a new video is added, its metadata would be inserted in the master first and before it gets applied at the slave, our slaves would not be able to see it; and therefore it will be returning stale results to the user. This staleness might be acceptable in our system as it would be very short-lived and the user would be able to see the new videos after a few milliseconds.

#### Where would thumbnails be stored?
There will be a lot more thumbnails than videos. Assume each video has 5 thumbnails, we need to have a very efficient storage system that'll serve huge read traffic.
Two considerations:
1. Thumbnails are small files, max 5KB each.
2. Read traffic for thumbnails will be huge compared to videos. Users will be watching one video at a time, but they might be looking at a page that has 20 thumbnails of other videos.

Let's evaluate storing thumbnails on disk.
Given the huge number of files, we have to perform a lot of seeks to different locations on the disk to read these files. This is quite inefficient and will result in higher latencies.

- **[BigTable](https://cloud.google.com/bigtable/)** can be a reasonable option choice here as it combines multiple files into one block to store on the disk and is very efficient in reading small amounts of data. Both of these are 2 significant requirements of our service. It also autoscales and is easy to replicate and can handle millions of operations per second. Changes to the deployment configuration are also immediate, so there’s no downtime during reconfiguration. 
- Keeping hot thumbnails in cache will also help improve latencies and, given that thumbnails are small in size, we can cache a large number of them in memory.

#### Video uploads: 
Since videos could be huge, if while uploading the connection drops, we should support resuming from the same point.

#### Video Encoding:
Newly uploaded videos are stored on the server and a new task is queued to the processing queue to encode the video into multiple formats. Once completed, the uploader will be notified and the video is made available for viewing/sharing.


![](images/detailed_design_youtube.png)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`Detailed component design of Youtube`

## 7. Metadata Sharding
Read load is extremely high because of huge number of newly uploaded videos. Therefore,
we need to distribute our data onto multiple machines that can share read/write operations 
efficiently.
We have a number of strategies when it comes to sharding:
#### Sharding based on UserID:
We can try storing all data for a particular user on one server. While storing, we can pass the UserID into a hash function which will map the user to a DB server where we'll store their videos metadata. While querying for videos, we can ask our hash function to  find the server holding the users' data and read it from there. To search videos by title we will ahve to query all servers and each server will return a set of videos.
A centralized server will then aggregate and rank them before returning them to the user.

Problems with this approach:
1. What if a user becomes popular? There will be a lot of queries on the user's server holding their videos; this could create a performance bottleneck.
2. Over time, some users can end up storing a lot of videos compared to others. Maintaining a uniform distribution of growing user data is quite tricky.

To recover from these situations, we can **repartition/redistribute** our data or use **consistent hashing to balance the load between servers**

#### Sharding based on VideoID:
Our hash function will map each videoID to a random server where we'll sotre the Video's metadata. To find videos of a user, we query all servers adn each server returns a set of videos. A centralized server will aggregate and rank the results before returning them to the user. This approach solves our problem with hot users, but shifts it to popular videos.

We can further improve our performance by introducing a cache to store hot videos in front of the database servers.

## 8. Video Deduplication
With a huge number of users uploading massive amounts of video data, our service will have to deal with widspread video duplication. Duplicate videos often differ in aspect ratios or encodings, can contain overlays or additional borders, or can be excerpts from a longer original video.

Having duplicate videos can have the following impact on many levels:
1. Data Storage: we'd waste storage by keeping multiple copies of the same video.
2. Caching: They'll degrade cache efficiency by taking up space tht could be used for unique content.
3. Network usage: They'll increase data sent over the network to in-network caching systems.
4. Energy consumption: Higher storage, inefficient cache and high network usage could result in energy wastage.
5. Effect to our user: Duplicate search results, longer video startup times, and interrupted streaming.

#### How do we implement deduplication?
Deduplication should happen when a user is uploading a video as compared to post-processing it to find videos later. Inline deduplication will save us a lot of resources that could be used to encode, transfer, and store the duplicate copy of the video. As soon as any user starts uploading a vidoe, our service can run video matching algorithms to find duplications. Such algorithms include:
- [Block Matching](https://en.wikipedia.org/wiki/Block-matching_algorithm), 
- [Phase Correlation](https://en.wikipedia.org/wiki/Phase_correlation), etc. 

If we already have a copy of the video being uploaded, we can either stop the upload and use the existing copy or continue upload and use the newly uploaded video **if it is of higher quality**. We can also divide the video into smaller chunks if the new video is a subpart of the existing video, or vice versa, so that we **only upload the missing parts**.


## 9. Load Balancing
We should use [Consistent Hashing](https://en.wikipedia.org/wiki/Consistent_hashing#targetText=In%20computer%20science%2C%20consistent%20hashing,is%20the%20number%20of%20slots.) among cache servers, which will also help in balancing the load between cache servers. It allows us to distribute data across a cluster in such a way that will minimize reorganization when nodes are added or removed. Hence, the caching system will be easier to scale up or scale down.
Difference in popularity of videos can lead to uneven load on logical repicas. For instance, if a video becomes popular, the logical replica corresponding to that video will experience more traffic than other servers. This will then translate to uneven load distribution on corresponding physical servers. 

To resolve this issue, **any busy server in one location can redirect a client to a less busy server in the same cache location.** We can use dynamic HTTP redirections for this scenario.

But the use of redirections also has its drawbacks. Since our service tries to lad balance locally, it leads to multiple other redirections when the host that receives the redirection can't serve the video. Also, redirection requires the client to make additional HTTP request; it also leads to higher delays before the video starts playing. 


## 10. Cache
Our service should push its content closer to the user using a large number of geographically distributed video cache servers.

We can introduce a cache for metadata servers to cache hot DB rows. Using Memcache to cache the data and Application servers before hitting the DB ca quickly check if the cache has the desired rows. 

Least Frequently Used(LRU) can be a reasonable cache eviction policy (to remove videos that shouldn't be cached) for our system. Under this policy, discard the least recently viewed row first.

#### How can we build more intelligent cache?
If we go with the 80-20 rule, 
> 20% of daily read volume comes from videos generating 80% of traffic.
This means that certain videos are so popular the majority of people view them.

Therefore, we can try caching 20% of daily read volume of videos and metadata.


## 11. Content Delivery Networks (CDN)
A CDN is a system of distributed servers that deliver static media content to a user based in the geographic locations of the user.

Our service can move popular videos to CDNs:
- CDNs replicate content in multiple places, There a better chance of videos being closer to the user and, with fewer hops, videos will stream from a friendlier network.
- CDN machines make heavy use of caching and can mostly serve videos out of memory.

Less popular videos that are not cached by CDNs can be served by our servers in various data centers.

## 12. Fault Tolerance
We should use [Consistent Hashing](https://en.wikipedia.org/wiki/Consistent_hashing) to help in replacing dead servers, and distributing load among servers.
