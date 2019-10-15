
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


## High Level Design
At a high-level we would need the following components:
1. **Processing Queue:**: Each uploaded video will be pushed to a processing queue ot be de-queued later for encoding, thumbnail generation, and storage.
2. **Encoder:** To encode each uploaded video into multiple formats.
3. **Thumbnails generator:** To generate thumbnails for each video.
4. **Video and Thumbnail storage:** To store video and thumbnail files in some distributed file storage.
5. **User DB:** To store user's info e.g name, email, address, etc.
6. **Video metadata storage:** A metadata DB to store information about videos like title, its file path, uploading user, total views, likes, comments etc. 

![](images/hld_youtube.png)

## Database Schema

#### Video metadata storage - MySQL
