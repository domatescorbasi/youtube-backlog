import argparse

import backlog_manager


def err_and_exit(msg: str):
    print(msg)
    exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Manage an offline 'YouTube watch later' backlog with download capabilities.\n"
                    "If a channel name is provided, operations will run exclusively on that channel.\n"
                    "If no channel name is provided, operations will run on the entire backlog."
    )

    group = parser.add_mutually_exclusive_group()
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode for detailed output.')
    group.add_argument('-l', '--load', action='store_true',
                       help='Parse and load YouTube links from youtube-links.txt, into the backlog.')
    group.add_argument('-c', '--clean', action='store_true',
                       help='Clean up the database by removing downloaded links. Deletes output file. Asks to reset youtube-links.txt')

    parser.add_argument('--channel',
                        help='Specify the channel name. If provided, following operations relevant to the specified channel will be executed.',
                        default="", type=str)
    group.add_argument('-t', '--time', action='store_true', help='Report the length of the backlog in terms of time.')
    group.add_argument('-d', '--download', action='store_true', help='Download videos from the database.')

    parser.add_argument('-ns', '--nosubtitles', action='store_true', default=False,
                        help='Do not download english subtitles for the video / Only usable while download')
    parser.add_argument('-rl', '--ratelimit', action='store_true', default=False,
                        help='Enable rate limiting for less bandwidth usage per second / Only usable while download')

    args = parser.parse_args()

    if args.nosubtitles and not args.download:
        err_and_exit(
            "-ns / --nosubtitles can be only used while downloading video(s) ( aka with -d | --download flag )")
    if args.ratelimit and not args.download:
        err_and_exit("-rl / --ratelimit can be only used while downloading video(s) ( aka with -d | --download flag )")

    backlog = backlog_manager.BacklogManager(is_verbose=args.verbose, is_rate_limited=args.ratelimit,
                                             is_no_subtitles=args.nosubtitles)
    if args.load:
        backlog.get_titles_and_durations()
        backlog.parse_and_load_to_database()
    elif args.time:
        if args.channel == "":
            backlog.report_all_duration()
        else:
            backlog.report_individual_channel_duration(args.channel)
    elif args.clean:
        backlog.cleanup()
    elif args.download:
        if args.channel == "":
            backlog.download_all_videos()
        else:
            backlog.download_all_videos_of_channel(args.channel)
    backlog.close()


if __name__ == '__main__':
    main()
