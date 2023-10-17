# from TikTokApi import TikTokApi
# from config import Config
#
#
# # async def get_video_by_url(url: str) -> str | None:
# #     api= TikTokApi()
# #         # await api.create_sessions(ms_tokens=[Config.TIKTOK_TOKEN], num_sessions=1, sleep_after=3)
# #
# #     video_bytes = api.video(url=url).bytes()
# #
# #         # Saving The Video
# #     with open('saved_video.mp4', 'wb') as output:
# #         output.write(video_bytes)
#
#
# async def trending_videos(url: str):
#     async with TikTokApi() as api:
#         print('dsd')
#         await api.create_sessions(ms_tokens=[Config.TIKTOK_TOKEN], num_sessions=1, sleep_after=3)
#         video = api.video(url=url)
#         print(video.sound)
#         # async for video in api.trending.videos(count=30):
#         #     print(video)
#         #     print(video.as_dict)
#
