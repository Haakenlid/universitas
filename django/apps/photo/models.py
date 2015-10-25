# -*- coding: utf-8 -*FIELDNAME = forms.SlugField()-
""" Photography and image files in the publication  """
# Python standard library
# import os
import os
import hashlib
import logging

# Django core
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import pre_delete, post_save
from django.utils import timezone
# Installed apps

from model_utils.models import TimeStampedModel
from utils.model_mixins import Edit_url_mixin
from sorl import thumbnail
from slugify import Slugify
# from boto.utils import parse_ts
import boto

# Project apps
from apps.issues.models import current_issue
from .autocrop import AutoCropImage, Cropping
logger = logging.getLogger(__name__)


def local_md5(filepath, blocksize=65536):
    """Hexadecimal md5 hash of a file stored on local disk"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as source:
        buf = source.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = source.read(blocksize)
    return hasher.hexdigest()


def s3_md5(s3key, blocksize=65536):
    """Hexadecimal md5 hash of a file stored in Amazon S3"""
    return s3key.etag.strip('"').strip("'")


def upload_image_to(instance, filename):
    return os.path.join(
        instance.upload_folder(),
        instance.slugify(filename)
    )


class ImageFile(TimeStampedModel, Edit_url_mixin, AutoCropImage):

    class Meta:
        verbose_name = _('ImageFile')
        verbose_name_plural = _('ImageFiles')

    source_file = thumbnail.ImageField(
        upload_to=upload_image_to,
        height_field='full_height',
        width_field='full_width',
        max_length=1024,
    )
    _md5 = models.CharField(
        verbose_name=_('md5 hash of source file'),
        max_length=32,
        editable=False,
        null=True,
    )
    _size = models.PositiveIntegerField(
        verbose_name=_('size of file in bytes'),
        editable=False,
        null=True,
    )
    _mtime = models.PositiveIntegerField(
        verbose_name=_('mtime timestamp of source file'),
        editable=False,
        null=True,
    )
    full_height = models.PositiveIntegerField(
        help_text=_('full height in pixels'),
        verbose_name=_('full height'),
        null=True, editable=False,
    )
    full_width = models.PositiveIntegerField(
        help_text=_('full height in pixels'),
        verbose_name=_('full height'),
        null=True, editable=False,
    )
    from_top = models.PositiveSmallIntegerField(
        default=50,
        help_text=_('image crop vertical. Between 0% and 100%.'),
        validators=[MaxValueValidator(100), MinValueValidator(0)],
    )
    from_left = models.PositiveSmallIntegerField(
        default=50,
        help_text=_('image crop horizontal. Between 0% and 100%.'),
        validators=[MaxValueValidator(100), MinValueValidator(0)],
    )
    crop_diameter = models.PositiveSmallIntegerField(
        default=100,
        help_text=_(
            'area containing most relevant content. Area is considered a '
            'circle with center x,y and diameter d where x and y are the '
            'values "from_left" and "from_right" and d is a percentage of '
            'the shortest axis. This is used for close cropping of some '
            'images, for instance byline photos.'
        ),
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)],
    )

    old_file_path = models.CharField(
        help_text=_('previous path if the image has been moved.'),
        blank=True, null=True,
        max_length=1000)

    contributor = models.ForeignKey(
        'contributors.Contributor',
        help_text=_('who made this'),
        blank=True, null=True,
    )

    copyright_information = models.CharField(
        help_text=_(
            'extra information about license and attribution if needed.'),
        blank=True,
        null=True,
        max_length=1000,
    )

    def __str__(self):
        if self.source_file:
            return os.path.basename(self.source_file.name)
        else:
            return super(ImageFile, self).__str__()

    def save(self, *args, **kwargs):
        pk = self.pk
        if pk and not kwargs.pop('autocrop', False):
            self.md5 = None
            self.size = None
            self.mtime = None
            try:
                saved = type(self).objects.get(id=self.pk)
                if (self.from_left,
                    self.from_top) != (saved.from_left,
                                       saved.from_top):
                    self.cropping_method = self.CROP_MANUAL
            except ImageFile.DoesNotExist:
                pass
        assert not self.size is None
        assert not self.md5 is None
        assert not self.mtime is None
        super().save(*args, **kwargs)
        if pk is None and self.cropping == self.CROP_NONE:
            self.autocrop()

    @property
    def md5(self):
        """Calculate or retrieve md5 value"""
        if self._md5 is None:
            try:  # Locally stored file
                self._md5 = local_md5(self.source_file.path)
            except NotImplementedError:  # AWS S3 storage
                self._md5 = s3_md5(self.source_file.file.key)
        return self._md5

    @md5.setter
    def md5(self, value):
        self._md5 = value

    @property
    def size(self):
        """Calculate or retrive filesize"""
        if self._size is None:
            self._size = self.source_file.size
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def mtime(self):
        """Modified time as unix timestamp"""
        if self._mtime is None:
            try:  # Locally stored file
                mtime = os.stat(self.source_file.path).st_mtime
                self._mtime = int(mtime)
            except NotImplementedError:  # AWS S3 storage
                key = self.source_file.file.key
                modified = boto.utils.parse_ts(key.last_modified)
                self._mtime = int(modified.strftime('%s'))
        return self._mtime

    @mtime.setter
    def mtime(self, timestamp):
        self._mtime = timestamp
        # created = timezone.datetime.fromtimestamp(timestamp)
        # self.created = timezone.make_aware(created)

    @classmethod
    def upload_folder(cls):
        issue = current_issue()
        return os.path.join(str(issue.date.year), str(issue.number))

    @staticmethod
    def slugify(filename):
        slugify = Slugify(safe_chars='.-', separator='-')
        slugs = slugify(filename).split('.')
        slugs[-1] = slugs[-1].lower().replace('jpeg', 'jpg')
        slug = '.'.join(segment.strip('-') for segment in slugs)
        return slug

    def thumb(self, height=315, width=600):
        geometry = '{}x{}'.format(width, height)
        try:
            return thumbnail.get_thumbnail(
                self.source_file,
                geometry,
                crop=self.get_crop()).url
        except Exception as e:
            msg = 'Thumbnail failed: {} {}'.format(e, self.source_file)
            logger.warn(msg)
            return self.source_file

    @property
    def cropping(self):
        return Cropping(
            top=self.from_top,
            left=self.from_left,
            diameter=self.crop_diameter)

    @cropping.setter
    def cropping(self, crop):
        self.from_top = crop.top
        self.from_left = crop.left
        self.crop_diameter = crop.diameter

    @cropping.deleter
    def cropping(self):
        field_names = (
            'from_top', 'from_left', 'crop_diameter', 'cropping_method')
        for field_name in field_names:
            field = self._meta.get_field(field_name)
            setattr(self, field.name, field.default)

    def get_crop(self):
        """ return center point of image in percent from top and left. """
        if self.cropping_method == self.CROP_NONE:
            self.autocrop()
        return '{h}% {v}%'.format(h=self.from_left, v=self.from_top)

    def compare_and_update(filepath):
        """Check for changes and update stored source file if needed."""
        stat = os.stat(filepath)


    # def identify_photo_file_initials(self, contributors=(),):
    #     """Assign contributor to photo
    #
    #     If passed a file path that matches the Universitas format for photo
    #     credit. Searches database or optional iterable of contributors for a
    #     person that matches initials at end of jpg-file name
    #     """
    #     from apps.contributors.models import Contributor
    #     filename_pattern = re.compile(r'^.+[-_]([A-ZÆØÅ]{2,5})\.jp.?g$')
    #     match = filename_pattern.match(self.source_file.name)
    #     if match:
    #         initials = match.groups()[0]
    #         for contributor in contributors:
    #             if contributor.initials == initials:
    #                 return contributor
    #         try:
    #             return Contributor.objects.get(initials=initials)
    #         except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
    #             logger.warning(self, initials, e)

    #     return None


class ProfileImage(ImageFile):

    class Meta:
        proxy = True
        verbose_name = _('Profile Image')
        verbose_name_plural = _('Profile Images')

    UPLOAD_FOLDER = 'byline-photo'

    @staticmethod
    def slugify(filename):
        return ImageFile.slugify(filename.title())

    @staticmethod
    def upload_folder():
        return ProfileImage.UPLOAD_FOLDER


def remove_imagefile_and_thumbnail(sender, instance, **kwargs):
    """Remove image file"""
    thumbnail.delete(instance.source_file, delete_file=True)
    # instance.source_file.delete()


def remove_thumbnail(sender, instance, **kwargs):
    thumbnail.delete(instance.source_file, delete_file=False)

pre_delete.connect(remove_imagefile_and_thumbnail, sender=ImageFile)
pre_delete.connect(remove_imagefile_and_thumbnail, sender=ProfileImage)
post_save.connect(remove_thumbnail, sender=ImageFile)
post_save.connect(remove_thumbnail, sender=ProfileImage)
