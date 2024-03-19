from datetime import datetime, time

from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Time
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    category = Column(String)
    videos = relationship("Video", back_populates="channel")

    __table_args__ = (
        UniqueConstraint('name'),
    )


class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    duration = Column(Time)
    link = Column(String, unique=True)
    is_downloaded = Column(Boolean, default=False)
    channel_id = Column(Integer, ForeignKey('channels.id'))
    channel = relationship("Channel", back_populates="videos")

    __table_args__ = (
        UniqueConstraint('link'),
    )


def add_times(time1, time2):
    total_seconds = time1.hour * 3600 + time1.minute * 60 + time1.second + \
                    time2.hour * 3600 + time2.minute * 60 + time2.second

    days, remainder = divmod(total_seconds, 24 * 3600)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return days, time(hour=hours, minute=minutes, second=seconds)


class ChannelManager:
    def __init__(self, db_name, is_verbose=False):
        self.is_verbose = is_verbose
        self.engine = create_engine('sqlite:///' + db_name)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def _print_verbose(self, message):
        if self.is_verbose:
            print(message)

    def add_channel(self, name, category):
        existing_channel = self.session.query(Channel).filter_by(name=name).first()
        if not existing_channel:
            new_channel = Channel(name=name, category=category)
            self.session.add(new_channel)
            self.session.commit()
            self._print_verbose(f"Channel '{name}' added successfully.")
        else:
            self._print_verbose(f"Channel with name '{name}' already exists. Skipping insertion.")

    def add_video(self, channel_name, title, duration, link):
        channel = self.session.query(Channel).filter_by(name=channel_name).first()
        if not channel:
            self._print_verbose(f"Channel '{channel_name}' does not exist. Adding channel before adding video.")
            self.add_channel(channel_name, "")
        try:
            channel = self.session.query(Channel).filter_by(name=channel_name).first()
            video = Video(title=title, duration=duration, link=link, channel_id=channel.id)
            self.session.add(video)
            self.session.commit()
            self._print_verbose(f"Video '{title}' added to channel '{channel_name}'.")
        except IntegrityError:
            self._print_verbose(
                f"Video with link '{link}' already exists in channel '{channel_name}'. Skipping insertion.")
            self.session.rollback()

    def mark_video_downloaded(self, link):
        video = self.session.query(Video).filter_by(link=link).first()
        if video:
            video.is_downloaded = True
            self.session.commit()
            self._print_verbose(f"Video '{video.title}' marked as downloaded.")
        else:
            self._print_verbose(f"Error: Video with link '{link}' not found.")

    def cleanup_downloaded_videos(self):
        downloaded_videos = self.session.query(Video).filter_by(is_downloaded=True).all()
        removal_candidate_channels = set()
        for video in downloaded_videos:
            self.session.delete(video)
            self._print_verbose(f"Downloaded video link '{video.title}' deleted.")
            removal_candidate_channels.add(video.channel)

        for channel in removal_candidate_channels:
            # Check if the channel of the deleted video has any more videos
            videos = self.get_videos(channel_name=channel.name)
            if len(videos) == 0:
                self.session.delete(channel)
                self._print_verbose(f"Channel '{channel.name}' deleted since it has no more videos.")
        self.session.commit()

    def get_all_channels(self):
        return self.session.query(Channel)

    def get_videos(self, channel_name):
        channel = self.session.query(Channel).filter_by(name=channel_name).first()
        return channel.videos if channel else []

    def get_channel_category(self, channel_name):
        channel = self.session.query(Channel).filter_by(name=channel_name).first()
        return channel.category if channel else None

    def get_cumulative_duration_for_channel(self, channel_name):
        videos = self.get_videos(channel_name=channel_name)
        cumulativeDuration = datetime.strptime("00:00:00", '%H:%M:%S').time()
        cumulativeDay = 0
        if videos:
            for video in videos:
                _day, cumulativeDuration = add_times(cumulativeDuration, video.duration)
                cumulativeDay = cumulativeDay + _day
        return cumulativeDay, cumulativeDuration

    def set_channel_category(self, channel_name, new_category):
        channel = self.session.query(Channel).filter_by(name=channel_name).first()
        if channel:
            channel.category = new_category
            self.session.commit()
            self._print_verbose(f"Category for channel '{channel_name}' set to '{new_category}'.")
        else:
            self._print_verbose(f"Error: Channel '{channel_name}' not found.")

    def close(self):
        self.session.close()

    def report_all_channels_all_videos_cumulative_duration(self):
        channels = self.session.query(Channel)
        cumDay = 0
        cumDuration = datetime.strptime("00:00:00", '%H:%M:%S').time()
        for channel in channels:
            day, duration = self.get_cumulative_duration_for_channel(channel.name)
            extra_day, cumDuration = add_times(cumDuration, duration)
            cumDay = cumDay + day + extra_day
        print(f"Total : {cumDay} day and {cumDuration}")

    def report_individual_channels_all_videos_cumulative_duration(self, channel_name=""):
        # Individual channels all videos cumulative duration

        if channel_name == "":
            channels = self.session.query(Channel)
        else:
            channels = self.session.query(Channel).filter_by(name=channel_name)

        for channel in channels:
            name = channel.name
            day, duration = self.get_cumulative_duration_for_channel(channel.name)
            if day == 0:
                print(f"{name} {duration}")
            else:
                print(f"{name} {day} day and {duration}")
