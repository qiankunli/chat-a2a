import os

from typing import TYPE_CHECKING

import pymysql
import pymysql.cursors

from libs.conf import settings

if TYPE_CHECKING:
    from pymysql.connections import Connection
    from pymysql.cursors import DictCursor

FILE_DIR = os.path.dirname(__file__)


def _get_connection_config():
    return dict(
        user=settings.DB_USERNAME,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        database=settings.DB_DATABASE,
        port=int(settings.DB_PORT),
        charset=settings.DB_CHARSET,
    )


class MySQLMigrations:
    def __init__(self, migration_dir=None):
        self.config = _get_connection_config()
        self.migration_dir = 'migrations'
        self.connection: Connection = self._initialize_connection()
        self.cursor: DictCursor = self._initialize_cursor()
        self.original_version = 'v0.0.0'

        if migration_dir:
            self.migration_dir = migration_dir
        self._setup_migration()

    def _initialize_connection(self):
        try:
            return pymysql.connect(**self.config, cursorclass=pymysql.cursors.DictCursor)
        except pymysql.MySQLError as e:
            raise pymysql.MySQLError(f"Failed to connect to database: {e}")

    def _initialize_cursor(self):
        return self.connection.cursor(pymysql.cursors.DictCursor)

    def _setup_migration(self):
        fn = os.path.join(FILE_DIR, 'create_migration.sql')
        sts = self.get_sql_statements_from_file(fn)
        for command in sts:
            self.execute_query(command)

    def execute_query(self, command: str, *args, **kwargs):
        if command:
            if kwargs:
                self.cursor.execute(command, kwargs)
            elif args:
                self.cursor.execute(command, args if len(args) > 1 else args[0])
            else:
                self.cursor.execute(command)
            results = self.cursor.fetchall()
            return results
        else:
            raise ValueError("No SQL command provided.")

    def close_connection(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def get_version_from_file(self, file) -> str:
        return os.path.splitext(file)[0]

    def get_current_version(self) -> str:
        """ Get current version from migration file"""
        sql = 'select version from migration;'
        rows = self.execute_query(sql)
        if len(rows) == 0:
            return self.original_version
        return rows[0]['version']

    def set_current_version(self, version) -> None:
        """ Set current version in migration file"""
        if not version:
            version = self.original_version
        sql = "UPDATE migration SET version = %(version)s"
        self.execute_query(sql, version=version)

    def get_migration_files(self, direction: str) -> list:
        try:
            files = os.listdir(self.migration_dir + '/' + direction)
            files.sort()
        except FileNotFoundError:
            files = []
        return files

    def get_sql_statements_from_file(self, file: str) -> list:
        with open(file, 'r') as f:
            statements = f.read().split(';')
            statements = [s for s in statements if s.strip() != '']
            return statements

    @staticmethod
    def int_version(version: str) -> tuple[int, ...]:
        version_tuple = tuple(int(x) for x in version[1:].split('.'))
        return version_tuple

    def get_up_files(self, target_version=None) -> list:
        """ Get all up files from current version to target version"""
        current_version = self.get_current_version()
        if not target_version:
            target_version = self.get_latest_version()
        files = self.get_migration_files('up')
        files_to_run = []
        for file in files:
            version = self.get_version_from_file(file)
            if MySQLMigrations.int_version(current_version) < MySQLMigrations.int_version(version) \
                    <= MySQLMigrations.int_version(target_version):
                files_to_run.append(file)
        return files_to_run

    def get_down_files(self, target_version=None) -> list:
        """ Get all down files from current version to target version in reverse order"""
        if not target_version:
            target_version = self.original_version

        current_version = self.get_current_version()
        files_to_run = []
        files = self.get_migration_files('down')
        for file in files:
            version = self.get_version_from_file(file)
            if MySQLMigrations.int_version(current_version) >= MySQLMigrations.int_version(version) \
                    > MySQLMigrations.int_version(target_version):
                files_to_run.append(file)

        files_to_run.reverse()
        return files_to_run

    def get_latest_version(self) -> str:
        """ Get latest version from migration up files"""
        files = self.get_migration_files('up')
        if len(files) == 0:
            return self.original_version

        last_file = files[-1]
        version = self.get_version_from_file(last_file)
        return version

    def get_migrate_up_statements(self, target_version=None) -> list:
        if not target_version:
            target_version = self.get_latest_version()

        up_files = self.get_up_files(target_version)
        statements = []
        for file in up_files:
            statements += self.get_sql_statements_from_file(
                self.migration_dir + '/up/' + file)
        return statements

    def get_migrate_down_statements(self, target_version=None) -> list:
        if not target_version:
            target_version = 0

        down_files = self.get_down_files(target_version)
        statements = []
        for file in down_files:
            statements += self.get_sql_statements_from_file(
                self.migration_dir + '/down/' + file)

        return statements

    def migrate_up(self, target_version=None):
        if not self.connection:
            raise Exception(
                'No connection. You will need to connect first.'
            )

        if not target_version:
            target_version = self.get_latest_version()
        if not self.cursor:
            raise Exception(
                'No cursor. You will need to initialize connection first.'
            )
        statements = self.get_migrate_up_statements(target_version)
        for statement in statements:
            self.execute_query(statement)
        # todo need run py file in script folder
        self.set_current_version(target_version)

    def migrate_down(self, target_version=None):
        if not self.connection:
            raise Exception(
                'No connection. You will need to connect first. Use MySQLMigration.connect(*kwargs, **kwargs)')

        if not target_version:
            target_version = self.original_version

        statements = self.get_migrate_down_statements(target_version)
        for statement in statements:
            self.execute_query(statement)
        self.set_current_version(target_version)
