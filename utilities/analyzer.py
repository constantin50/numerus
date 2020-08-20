"""
Analyzer implements parsing videos from YouTube
"""
import re
import webbrowser as wb
import json
import random
import requests
from youtube_transcript_api import YouTubeTranscriptApi as yt_trns

"""
key - your API key from YouTube

scan_channel() takes id of channel, 
makes request to API of YouTube for receiving 
ids of first 25 videos from upload playlist;
it returns ids of first 25 videos

scan_video() takes id of video and 
makes request for transcript, searches
numbers; it returns pair ['timecode', 'number']   

get_videos() takes ids of channels and language of this
channel; it returns quadruple: ['language', 'id of video', 'timecode', 'number', phrase']

"""

class Analyzer:
	def __init__(self, key):
		self.key = key

	def get_videos(self,channels, lang):
		result = list()
		for channel in channels:
			print(channel)
			videos = self.scan_channel(channel)
			for video in videos:
				data = self.scan_video(video, lang)
				if (data != None and data != []):
					result.append(data)


		print(len(result), " extracts were done")
		return self.formate(result)

	def scan_channel(self, channel_id):
		
		video_id = list()

		channel_info = "https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={}&key=" + self.key
		channel_info = channel_info.format(channel_id)
		channel_info = json.loads(requests.get(channel_info).text)

		playlist = channel_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']

		playlist_items = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=25&playlistId={}&key=" + self.key
		playlist_items = playlist_items.format(playlist)
		playlist_items = json.loads(requests.get(playlist_items).text)

		for i in range(len(playlist_items['items'])):
			video_id.append(playlist_items['items'][i]['contentDetails']['videoId'])

		return video_id
			

	def launch(self, video_id, t):
		print("https://youtu.be/" + video_id + "?t=" + str(int(t)))
		wb.open("https://youtu.be/" + video_id + "?t=" + str(int((t))))

	def scan_video(self, video_id, lang):

		text = '';
		result = list() # pairs [lang,timecode, number,phrase]
		try: 
			text = yt_trns.get_transcript(video_id, languages=[lang])
		except Exception:
			print("subs are't found");
		
		pttrn = '\d+';

		for i in range(len(text)):
			if (re.findall(pttrn,text[i]["text"])):
				number = re.findall(pttrn,text[i]["text"])
				if (i > 0 and i+1 < len(text)):
					phrase = text[i-1]["text"]+" "+text[i]["text"]+" "+text[i+1]["text"];
					t = str(int(text[i]["start"])-2);
					phrase =phrase.replace(',', '')


					# formate numers
					ptr = r'\d\s\d{3,}'
					nums = re.findall(ptr,phrase);
					for i in range(len(nums)):
						phrase =phrase.replace(nums[i], nums[i].replace(' ', ''))
					result.append([lang, video_id, t, number,phrase])
						
		return result	

	
	def formate(self, data):
		result = list()
		for i in range(len(data)):
			for j in range(len(data[i])):
				result.append(data[i][j])
		return result
