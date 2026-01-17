"""
Episode tracking service.

This module provides service layer for tracking watched TV show episodes.
"""

from django.db import transaction

from media.models import TVShow, WatchedEpisode
from users.models import User


class EpisodeTrackingService:
    """
    Service for tracking watched TV show episodes.

    This service provides business logic for marking episodes as watched
    and retrieving watch history.
    """

    @transaction.atomic
    def mark_episode_watched(
        self,
        user: User,
        tv_show: TVShow,
        season_number: int,
        episode_number: int,
    ) -> WatchedEpisode:
        """
        Mark an episode as watched for a user.

        Parameters
        ----------
        user : User
            User who watched the episode.
        tv_show : TVShow
            TV show the episode belongs to.
        season_number : int
            Season number of the episode.
        episode_number : int
            Episode number within the season.

        Returns
        -------
        WatchedEpisode
            The watched episode record.
        """
        watched_episode, created = WatchedEpisode.objects.get_or_create(
            user=user,
            tv_show=tv_show,
            season_number=season_number,
            episode_number=episode_number,
        )

        return watched_episode

    @transaction.atomic
    def unmark_episode_watched(
        self,
        user: User,
        tv_show: TVShow,
        season_number: int,
        episode_number: int,
    ) -> bool:
        """
        Unmark an episode as watched for a user.

        Parameters
        ----------
        user : User
            User who watched the episode.
        tv_show : TVShow
            TV show the episode belongs to.
        season_number : int
            Season number of the episode.
        episode_number : int
            Episode number within the season.

        Returns
        -------
        bool
            True if the episode was unmarked, False if it wasn't watched.
        """
        deleted_count, _ = WatchedEpisode.objects.filter(
            user=user,
            tv_show=tv_show,
            season_number=season_number,
            episode_number=episode_number,
        ).delete()

        return deleted_count > 0

    def get_watched_episodes(self, user: User, tv_show: TVShow) -> list[WatchedEpisode]:
        """
        Get all watched episodes for a TV show.

        Parameters
        ----------
        user : User
            User whose watch history to retrieve.
        tv_show : TVShow
            TV show to get watched episodes for.

        Returns
        -------
        list[WatchedEpisode]
            List of watched episodes.
        """
        return list(
            WatchedEpisode.objects.filter(
                user=user,
                tv_show=tv_show,
            ).order_by("season_number", "episode_number")
        )

    def get_watch_progress(self, user: User, tv_show: TVShow) -> dict[str, int]:
        """
        Calculate watch progress for a TV show.

        Parameters
        ----------
        user : User
            User whose progress to calculate.
        tv_show : TVShow
            TV show to calculate progress for.

        Returns
        -------
        dict[str, int]
            Dictionary containing:
            - watched_episodes: Number of watched episodes
            - total_episodes: Total number of episodes in the show
            - progress_percentage: Percentage of completion
        """
        watched_count = WatchedEpisode.objects.filter(
            user=user,
            tv_show=tv_show,
        ).count()

        total_episodes = tv_show.number_of_episodes

        progress_percentage = 0
        if total_episodes > 0:
            progress_percentage = int((watched_count / total_episodes) * 100)

        return {
            "watched_episodes": watched_count,
            "total_episodes": total_episodes,
            "progress_percentage": progress_percentage,
        }

    def is_episode_watched(
        self,
        user: User,
        tv_show: TVShow,
        season_number: int,
        episode_number: int,
    ) -> bool:
        """
        Check if an episode is watched.

        Parameters
        ----------
        user : User
            User to check for.
        tv_show : TVShow
            TV show the episode belongs to.
        season_number : int
            Season number of the episode.
        episode_number : int
            Episode number within the season.

        Returns
        -------
        bool
            True if the episode is watched, False otherwise.
        """
        return WatchedEpisode.objects.filter(
            user=user,
            tv_show=tv_show,
            season_number=season_number,
            episode_number=episode_number,
        ).exists()
