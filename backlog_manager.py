from datetime import datetime
import os

import database
import ytdlp_wrapper


def get_yes_or_no_input(prompt):
    while True:
        response = input(prompt).strip().lower()
        if response == 'yes' or response == 'y':
            return True
        elif response == 'no' or response == 'n':
            return False
        else:
            print("Please enter 'yes' or 'no'.")


class BacklogManager:
    def __init__(self, is_verbose):
        self.is_verbose = is_verbose
        self.channel_manager = database.ChannelManager("channels.db", is_verbose=is_verbose)
        self.input_file = "youtube-links.txt"
        self.output_file = "output.txt"
        self.youtube_dl = ytdlp_wrapper.YoutubeDownloadManager(self.input_file, self.output_file, is_verbose=is_verbose)

    def _print_verbose(self, message):
        if self.is_verbose:
            print(message)

    def get_titles_and_durations(self):
        self.youtube_dl.download_titles_and_durations()

    def parse_and_load_to_database(self):
        dataFile = open(self.output_file, 'r')
        dataLines = dataFile.readlines()
        for data in dataLines:
            split = data.strip().split("§")
            channel = split[0]
            title = split[1]
            duration = datetime.strptime(split[2], '%H:%M:%S').time()
            url = split[3]
            self.channel_manager.add_video(channel_name=channel, title=title, duration=duration, link=url)
        self._print_verbose("Parse and load job completed")
        self.channel_manager.close()

    def download_all_videos(self):
        channels = self.channel_manager.get_all_channels()
        for channel in channels:
            self.download_all_videos_of_channel(channel_name=channel.name)
        self._print_verbose("All download jobs completed")

    def download_all_videos_of_channel(self, channel_name):
        videos = self.channel_manager.get_videos(channel_name)
        for video in videos:
            if self.youtube_dl.download_video(video.link):
                self.channel_manager.mark_video_downloaded(video.link)
        self._print_verbose(f"Download job of '{channel_name}' completed")

    def report_all_duration(self):
        self.channel_manager.report_individual_channels_all_videos_cumulative_duration()
        self.channel_manager.report_all_channels_all_videos_cumulative_duration()

    def report_individual_channel_duration(self, channel_name):
        self.channel_manager.report_individual_channels_all_videos_cumulative_duration(channel_name=channel_name)

    def close(self):
        self.channel_manager.close()

    def cleanup(self):
        self.channel_manager.cleanup_downloaded_videos()
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            self._print_verbose(f"{self.output_file} has been deleted.")
        else:
            self._print_verbose(f"{self.output_file} does not exist.")

        if os.path.exists(self.input_file):
            response = get_yes_or_no_input(f"Do you want to delete {self.input_file}? (yes/no): ")
            if response:
                os.remove(self.input_file)
                self._print_verbose(f"{self.input_file} has been deleted.")
                with open(self.input_file, 'w'):
                    pass  # Using pass to indicate no further action is needed
                self._print_verbose(f"Fresh {self.input_file} has been created.")
        else:
            self._print_verbose(f"{self.input_file} does not exist.")
