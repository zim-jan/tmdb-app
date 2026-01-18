"""
Media models for Movie and TV Show objects.

This module contains the base and concrete models for media content,
following the Abstract Factory pattern.
"""

from typing import Any

from django.db import models


class MediaType(models.TextChoices):
    """
    Enumeration of media types.

    Attributes
    ----------
    MOVIE : str
        Movie media type.
    TV_SHOW : str
        TV Show media type.
    """

    MOVIE = "MOVIE", "Movie"
    TV_SHOW = "TV_SHOW", "TV Show"


class Media(models.Model):
    """
    Abstract base model for all media content.

    This is the base class for Movie and TVShow models,
    implementing the Abstract Factory pattern.

    Attributes
    ----------
    tmdb_id : int
        The Movie Database (TMDb) unique identifier.
    title : str
        Media title.
    original_title : str
        Original title in the original language.
    overview : str
        Media description/synopsis.
    poster_path : str
        Path to the poster image.
    backdrop_path : str
        Path to the backdrop image.
    release_date : date
        Release date (for movies) or first air date (for TV shows).
    popularity : float
        TMDb popularity score.
    vote_average : float
        Average user rating from TMDb.
    vote_count : int
        Number of votes on TMDb.
    original_language : str
        ISO 639-1 code of the original language.
    media_type : str
        Type of media (MOVIE or TV_SHOW).
    created_at : datetime
        Timestamp when the record was created.
    updated_at : datetime
        Timestamp when the record was last updated.
    """

    tmdb_id = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
        help_text="The Movie Database (TMDb) unique identifier",
    )
    title = models.CharField(
        max_length=255,
        help_text="Media title",
    )
    original_title = models.CharField(
        max_length=255,
        help_text="Original title in the original language",
    )
    overview = models.TextField(
        blank=True,
        help_text="Media description/synopsis",
    )
    poster_path = models.CharField(
        max_length=255,
        blank=True,
        help_text="Path to the poster image",
    )
    backdrop_path = models.CharField(
        max_length=255,
        blank=True,
        help_text="Path to the backdrop image",
    )
    release_date = models.DateField(
        null=True,
        blank=True,
        help_text="Release date (for movies) or first air date (for TV shows)",
    )
    popularity = models.FloatField(
        default=0.0,
        help_text="TMDb popularity score",
    )
    vote_average = models.FloatField(
        default=0.0,
        help_text="Average user rating from TMDb",
    )
    vote_count = models.IntegerField(
        default=0,
        help_text="Number of votes on TMDb",
    )
    original_language = models.CharField(
        max_length=10,
        help_text="ISO 639-1 code of the original language",
    )
    media_type = models.CharField(
        max_length=20,
        choices=MediaType.choices,
        db_index=True,
        help_text="Type of media (MOVIE or TV_SHOW)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated",
    )

    class Meta:
        """Meta options for Media model."""

        db_table = "media"
        ordering = ["-created_at"]
        verbose_name = "Media"
        verbose_name_plural = "Media"
        indexes = [
            models.Index(fields=["tmdb_id"]),
            models.Index(fields=["media_type"]),
        ]

    def __str__(self) -> str:
        """
        Return string representation of the media.

        Returns
        -------
        str
            Title of the media.
        """
        return self.title


class Movie(Media):
    """
    Movie model extending Media base class.

    Attributes
    ----------
    runtime : int
        Movie runtime in minutes.
    budget : int
        Movie production budget.
    revenue : int
        Movie revenue.
    """

    runtime = models.IntegerField(
        null=True,
        blank=True,
        help_text="Movie runtime in minutes",
    )
    budget = models.BigIntegerField(
        default=0,
        help_text="Movie production budget",
    )
    revenue = models.BigIntegerField(
        default=0,
        help_text="Movie revenue",
    )

    class Meta:
        """Meta options for Movie model."""

        db_table = "movies"
        verbose_name = "Movie"
        verbose_name_plural = "Movies"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Save the movie instance.

        Ensures media_type is set to MOVIE before saving.

        Parameters
        ----------
        args : Any
            Positional arguments.
        kwargs : Any
            Keyword arguments.
        """
        self.media_type = MediaType.MOVIE
        super().save(*args, **kwargs)


class TVShow(Media):
    """
    TV Show model extending Media base class.

    Attributes
    ----------
    number_of_seasons : int
        Total number of seasons.
    number_of_episodes : int
        Total number of episodes.
    episode_run_time : int
        Average episode runtime in minutes.
    status : str
        Current status (Returning Series, Ended, etc.).
    first_air_date : date
        Date of the first episode airing.
    last_air_date : date
        Date of the most recent episode airing.
    """

    number_of_seasons = models.IntegerField(
        default=0,
        help_text="Total number of seasons",
    )
    number_of_episodes = models.IntegerField(
        default=0,
        help_text="Total number of episodes",
    )
    episode_run_time = models.IntegerField(
        null=True,
        blank=True,
        help_text="Average episode runtime in minutes",
    )
    status = models.CharField(
        max_length=50,
        blank=True,
        help_text="Current status (Returning Series, Ended, etc.)",
    )
    first_air_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the first episode airing",
    )
    last_air_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the most recent episode airing",
    )

    class Meta:
        """Meta options for TVShow model."""

        db_table = "tv_shows"
        verbose_name = "TV Show"
        verbose_name_plural = "TV Shows"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Save the TV show instance.

        Ensures media_type is set to TV_SHOW before saving.

        Parameters
        ----------
        args : Any
            Positional arguments.
        kwargs : Any
            Keyword arguments.
        """
        self.media_type = MediaType.TV_SHOW
        super().save(*args, **kwargs)


class WatchedEpisode(models.Model):
    """
    Model for tracking watched TV show episodes.

    Attributes
    ----------
    user : User
        User who watched the episode.
    tv_show : TVShow
        TV show that the episode belongs to.
    season_number : int
        Season number of the episode.
    episode_number : int
        Episode number within the season.
    watched_at : datetime
        Timestamp when the episode was marked as watched.
    """

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="watched_episodes",
        help_text="User who watched the episode",
    )
    tv_show = models.ForeignKey(
        TVShow,
        on_delete=models.CASCADE,
        related_name="watched_episodes",
        help_text="TV show that the episode belongs to",
    )
    season_number = models.IntegerField(
        help_text="Season number of the episode",
    )
    episode_number = models.IntegerField(
        help_text="Episode number within the season",
    )
    watched_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the episode was marked as watched",
    )

    class Meta:
        """Meta options for WatchedEpisode model."""

        db_table = "watched_episodes"
        ordering = ["-watched_at"]
        verbose_name = "Watched Episode"
        verbose_name_plural = "Watched Episodes"
        unique_together = ["user", "tv_show", "season_number", "episode_number"]
        indexes = [
            models.Index(fields=["user", "tv_show"]),
            models.Index(fields=["tv_show", "season_number", "episode_number"]),
        ]

    def __str__(self) -> str:
        """
        Return string representation of the watched episode.

        Returns
        -------
        str
            Description of the watched episode.
        """
        return f"{self.tv_show.title} S{self.season_number:02d}E{self.episode_number:02d}"
