from typing import TypedDict

Schedule = TypedDict("Schedule", {
    "time": str,
    "days": list[str]
})
Rating = TypedDict("Rating", {
    "average": str
})
Country = TypedDict("Country", {
    "name": str,
    "code": str,
    "timezone": str
})
Network = TypedDict("Network", {
    "id": int,
    "name": str,
    "country": Country,
    "officialSite": str
})
Externals = TypedDict("Externals", {
    "tvrage": int,
    "thetvdb": int,
    "imdb": str
})
Image = TypedDict("Image", {
    "medium": str,
    "original": str
})
LinkSelf = TypedDict("LinkSelf", {
    "href": str
})
PreviousEpisode = TypedDict("PreviousEpisode", {
    "href": str,
    "name": str
})
ShowLink = TypedDict("ShowLink", {
    "href":str,
    "name": str
})
Links = TypedDict("Links", {
    "self": LinkSelf,
    "previousepisode": PreviousEpisode
})
EpisodeLinks = TypedDict("EpisodeLinks", {
    "self": LinkSelf,
    "show": ShowLink
})

TVMazeShow = TypedDict('TVMazeShow', {
    "id": int,
    "url": str,
    "name": str,
    "type": str,
    "language": str,
    "genres": list[str],
    "status": str,
    "runtime": int,
    "averageRuntime": int,
    "premiered": str,
    "ended": str,
    "officialSite":str,
    "schedule": Schedule,
    "rating": Rating,
    "weight": int,
    "network": Network,
    "webChannel": str,
    "dvdCountry": str,
    "externals": Externals,
    "image": Image,
    "summary": str,
    "updated": int,
    "_links": Links
})

TVMazeEpisode = TypedDict("TVMazeEpisode", {
    "id": int,
    "url": str,
    "name": str,
    "season": int,
    "number": int,
    "type": str,
    "airdate": str,
    "airtime": str,
    "airstamp": str,
    "runtime": int,
    "rating": Rating,
    "image": Image,
    "summary": str,
    "_links": EpisodeLinks
})