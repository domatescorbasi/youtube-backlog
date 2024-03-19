import subprocess


class YoutubeDownloadManager:
    def __init__(self, input_file, output_file, is_verbose=False):
        self.is_verbose = is_verbose
        self.input_file = input_file
        self.output_file = output_file

    def _print_verbose(self, message):
        if self.is_verbose:
            print(message)

    def download_titles_and_durations(self):
        command = [
            "yt-dlp",
            "-a", self.input_file,
            "--print", "%(channel)s§%(title)s§%(duration>%H:%M:%S)s§%(webpage_url)s"
        ]

        try:
            with open(self.output_file, "w") as outfile:
                if self.is_verbose:
                    subprocess.run(command, stdout=outfile, check=True)
                else:
                    subprocess.run(command, stdout=outfile, stderr=subprocess.DEVNULL, check=True)
            self._print_verbose("Titles and durations download completed successfully.")
        except subprocess.CalledProcessError as e:
            self._print_verbose(f"Error: {e}")

    def download_video(self, link):
        command = [
            "yt-dlp",
            "-f", "22",
            link,
            "-o",
            "./Videos/%(uploader)s/%(upload_date)s %(title)s.%(ext)s"
        ]
        try:
            if self.is_verbose:
                subprocess.run(command, check=True)
            else:
                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            self._print_verbose("Download completed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            self._print_verbose(f"Error: {e}")
            return False
