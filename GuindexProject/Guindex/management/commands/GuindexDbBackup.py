import fcntl
import glob
import logging
import os
import time
from shutil import copyfile
from datetime import datetime

import dropbox

from django.conf import settings
from django.core.management.base import BaseCommand

from Guindex.GuindexParameters import GuindexParameters

logger = logging.getLogger(__name__.split('.')[-1])

G_DB_NAME = settings.DATABASES['default']['NAME']
# Survives deletion of dated local copies after Dropbox upload
G_LAST_BACKUP_MARKER = G_DB_NAME + '.last_backup'


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        lock_path = os.path.join(settings.BASE_DIR, 'guindex_db_backup.lock')
        lock_fd = open(lock_path, 'w')

        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            logger.error(
                "Another GuindexDbBackup instance already holds %s; exiting",
                lock_path,
            )
            lock_fd.close()
            return

        logger.info("Acquired db backup lock at %s", lock_path)

        try:
            self._run_backup_loop()
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()

    def _run_backup_loop(self):

        while True:

            sleep_time = self._seconds_until_next_backup()
            if sleep_time > 0:
                logger.info(
                    "Backup period not elapsed; sleeping %d seconds",
                    sleep_time,
                )
                time.sleep(sleep_time)
                continue

            logger.info("Backing up Guindex database")

            # Append current time to database
            current_time = datetime.now().strftime('%Y-%B-%d_%H:%M:%S')

            copied_db_name = "%s-%s" % (G_DB_NAME, current_time)
            copied_db_leaf = copied_db_name.split('/')[-1]

            # Mark the attempt immediately so a crash/restart cannot create
            # another copy within DB_BACKUP_PERIOD (this caused the Oct storm).
            self._touch_last_backup_marker()

            # Copy file locally
            try:
                copyfile(G_DB_NAME, copied_db_name)
            except Exception:
                logger.exception("Failed to create local database copy %s", copied_db_name)
                self._prune_local_backups()
                logger.info("Sleeping for %d seconds", GuindexParameters.DB_BACKUP_PERIOD)
                time.sleep(GuindexParameters.DB_BACKUP_PERIOD)
                continue

            # Copy file to dropbox
            dropbox_context = dropbox.Dropbox(settings.DROPBOX_API_ACCESS_TOKEN)

            try:
                # Stream upload in chunks to avoid loading the whole DB into RAM
                # (OOM here + Restart=always historically caused backup storms).
                self._upload_file(dropbox_context, copied_db_name, copied_db_leaf)

                logger.info("Successfully uploaded %s to dropbox", copied_db_leaf)

                # Dropbox has the backup; free local disk immediately
                try:
                    os.remove(copied_db_name)
                    logger.info("Removed local backup copy %s", copied_db_leaf)
                except Exception:
                    logger.exception("Failed to remove local backup copy %s", copied_db_name)

            except Exception:
                logger.exception("Failed to upload %s to dropbox", copied_db_leaf)
                # Leave the local copy for now; prune() caps how many we keep

            del dropbox_context

            self._prune_local_backups()

            logger.info("Sleeping for %d seconds", GuindexParameters.DB_BACKUP_PERIOD)
            time.sleep(GuindexParameters.DB_BACKUP_PERIOD)

    def _touch_last_backup_marker(self):
        marker = open(G_LAST_BACKUP_MARKER, 'w')
        try:
            marker.write("%s\n" % datetime.now().isoformat())
            marker.flush()
            os.fsync(marker.fileno())
        finally:
            marker.close()

    def _seconds_until_next_backup(self):
        """
            If we already attempted a backup less than DB_BACKUP_PERIOD ago,
            return remaining seconds to wait. Uses a marker file so this still
            works after dated local copies are deleted post-upload.
        """
        newest_mtime = None

        if os.path.exists(G_LAST_BACKUP_MARKER):
            newest_mtime = os.path.getmtime(G_LAST_BACKUP_MARKER)

        newest_backup = self._newest_local_backup()
        if newest_backup:
            backup_mtime = os.path.getmtime(newest_backup)
            if newest_mtime is None or backup_mtime > newest_mtime:
                newest_mtime = backup_mtime

        if newest_mtime is None:
            return 0

        age = time.time() - newest_mtime
        remaining = GuindexParameters.DB_BACKUP_PERIOD - age
        if remaining > 0:
            logger.info("Last backup attempt was %d seconds ago", int(age))
            return int(remaining) + 1

        return 0

    def _newest_local_backup(self):
        backups = glob.glob("%s-*" % G_DB_NAME)
        if not backups:
            return None
        return max(backups, key=os.path.getmtime)

    def _upload_file(self, dropbox_context, local_path, remote_leaf):
        remote_path = '/GuindexDbBackups/' + remote_leaf
        chunk_size = 4 * 1024 * 1024  # 4 MiB

        file_size = os.path.getsize(local_path)
        with open(local_path, 'rb') as f:
            if file_size <= chunk_size:
                dropbox_context.files_upload(f.read(), remote_path, mute=True)
                return

            session = dropbox_context.files_upload_session_start(f.read(chunk_size))
            cursor = dropbox.files.UploadSessionCursor(
                session_id=session.session_id,
                offset=f.tell(),
            )
            commit = dropbox.files.CommitInfo(path=remote_path, mute=True)

            while (file_size - f.tell()) > chunk_size:
                dropbox_context.files_upload_session_append_v2(
                    f.read(chunk_size),
                    cursor,
                )
                cursor.offset = f.tell()

            dropbox_context.files_upload_session_finish(
                f.read(chunk_size),
                cursor,
                commit,
            )

    def _prune_local_backups(self):
        """
            Keep only the newest N dated local DB copies under /usr/share.
            Prevents disk fill when Dropbox uploads fail repeatedly.
        """
        keep = GuindexParameters.DB_BACKUP_LOCAL_KEEP
        pattern = "%s-*" % G_DB_NAME
        backups = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)

        for path in backups[keep:]:
            try:
                os.remove(path)
                logger.info("Pruned old local backup %s", path)
            except Exception:
                logger.exception("Failed to prune old local backup %s", path)
