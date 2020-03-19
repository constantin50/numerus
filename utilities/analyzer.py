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

		channel_info = "https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={}&key=" + key
		channel_info = channel_info.format(channel_id)
		channel_info = json.loads(requests.get(channel_info).text)

		playlist = channel_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']

		playlist_items = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=25&playlistId={}&key=AIzaSyBjjjjindlrUHKt6MoAnn2oirjUd92q36I"
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
		
		pttrn = '';
		if (lang=='en'):
			pttrn = r'(\d{3,}|\d{2,}.\d|\d{1,}\smillion|\d{1,}\smillions|\d{1,}\sthousand\
				|\d{1,}\sthousands|\d{1,}\sbillion|\d{1,}\sbillions)'

		if (lang=='ru'):
			pttrn = r'(\d{3,}|\d{2,}.\d|\d{1,}\sмиллион|\d{1,}\sмиллионов|\d{1,}\sтысяча\
				|\d{1,}\sтысячи|\d{1,}\sмиллиард|\d{1,}\sмиллиард)'

		if (lang=='fr'):
			pttrn = r'(\d{3,}|\d{2,}.\d|\d{1,}\smillion|\d{1,}\smillions|\d{1,}\smille\
				|\d{1,}\smilles|\d{1,}\s|\d{1,}\smilliards|\d{1,}\smilliard)'  


		for i in range(len(text)):
			if (re.findall(pttrn,text[i]["text"])):
				number = re.findall(pttrn,text[i]["text"])
				phrase = text[i-1]["text"]+" "+text[i]["text"]+" "+text[i+1]["text"];
				t = str(int(text[i]["start"])-2);
				phrase =phrase.replace(',', '')

				phrase =phrase.replace('million', '000000')
				phrase =phrase.replace('millions', '000000')
				phrase =phrase.replace('thousand', '000')
				phrase =phrase.replace('thousands', '000')
				phrase =phrase.replace('billion', '000000000')
				phrase =phrase.replace('billions', '000000000')

				phrase =phrase.replace('миллион', '000000')
				phrase =phrase.replace('миллионов', '000000')
				phrase =phrase.replace('тысяча', '000')
				phrase =phrase.replace('тысяч', '000')
				phrase =phrase.replace('миллиард', '000000000')
				phrase =phrase.replace('миллиардов', '000000000')

				phrase =phrase.replace('million', '000000')
				phrase =phrase.replace('millions', '000000')
				phrase =phrase.replace('mille', '000')
				phrase =phrase.replace('milles', '000')
				phrase =phrase.replace('milliard', '000000000')
				phrase =phrase.replace('milliards', '000000000')

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
