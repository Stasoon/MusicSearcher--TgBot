from pytube import YouTube

YouTube('http://youtube.com/watch?v=9bZkp7q19f0').streams[0].download()
