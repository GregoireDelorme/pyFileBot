#!/usr/bin/env python

from pyfilebot.cli.helpers import do_rename, do_rollback, iter_files, CONTEXT_SETTINGS

from pyfilebot.utils import Files, DEFAULT_RULES
from pyfilebot.main import Cache, Movie, ShowEpisode
from pyfilebot import __version__ as version

import click


class Option:

    @staticmethod
    def dirs(func):
        func = click.option('-c', '--clean', is_flag=True, help='Clean empty dirs at the end', default=False)(func)
        func = click.option('-r', '--recursive', is_flag=True, help='Recursively lookup files in the director(y|ies)',
                            default=False)(func)
        return func

    @staticmethod
    def renamer(func):
        func = click.option('-l', '--language', help=f'Output language file for {func.__name__}', default="en",
                            show_default=True)(func)
        func = click.option('-d', '--dry-run', is_flag=True, help='Dry run your renaming', default=False)(func)
        func = click.option('-f', '--force', is_flag=True,
                            help='Force renaming if an output file already exists, ignore otherwise', default=False)(
            func)
        func = click.option('-i', '--imdb_id',
                            help=f'Force IMDb id for a {func.__name__} (Only works if one media / folder as input)')(
            func)
        func = click.option('-n', '--non-interactive', is_flag=True,
                            help=f'Ignore {func.__name__} not found and disable manual association, the option for non-interactive mode',
                            default=False)(func)
        func = click.option('-a', '--action', type=click.Choice(['move', 'copy', 'sym']), default="move",
                            show_default=True,
                            help="Move, copy or symlink files to the destination")(func)
        func = click.option('-u', '--rules', help='Format to apply for renaming',
                            default=DEFAULT_RULES[func.__name__], show_default=True)(func)
        func = click.option('-o', '--output',
                            help='The directory to move renamed files to, if not specified the input working directory is used')(
            func)
        return func


@click.group(**CONTEXT_SETTINGS)
def cli():
    pass


@cli.command(**CONTEXT_SETTINGS)
@Option.dirs
@Option.renamer
@click.argument('input', nargs=-1, required=True)
def movies(**args):
    """Rename movies from INPUT files or folders"""
    iter_files(do_rename, cls=Movie, cache=None, **args)


@cli.command(**CONTEXT_SETTINGS)
@Option.dirs
@Option.renamer
@click.argument('input', nargs=-1, required=True)
def shows(**args):
    """Rename TV shows from INPUT files or folders"""
    iter_files(do_rename, cls=ShowEpisode, cache=Cache(), **args)


@cli.command(**CONTEXT_SETTINGS)
@Option.dirs
@click.argument('input', nargs=-1, required=True)
def rollback(**args):
    """Rollback INPUT files or folders based on the history"""
    iter_files(do_rollback, **args)


@cli.command(**CONTEXT_SETTINGS)
def history():
    """History of files renamed"""
    Files.read_history()


@cli.command(**CONTEXT_SETTINGS)
def subtitles():
    """Download subtitles on medias from INPUT files or folders"""
    pass


@cli.command(**CONTEXT_SETTINGS)
def version():
    """Show version of pyfilebot"""
    print(version)