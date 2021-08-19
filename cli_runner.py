from log import compare_dates, delete_latest_entry
from database import insert_into_showlist_collection, remove_show_from_list, get_showlist
from main import send_message
import click

@click.group()
def cli():
    pass


@cli.command()
def send_email():
    """
    Searches the TV guides for the list of shows and sends the results in an email
    """
    status = compare_dates()
    print(status)
    if status:
        send_message()
        


@cli.command()
def delete_log_entry():
    """
    Deletes the latest log entry
    """
    delete_latest_entry()


@cli.command()
def add_show():
    """
    Adds the given show into the list of shows
    """
    insert_into_showlist_collection()


@cli.command()
def show_list():
    """
    Displays the current list of shows that the TVGuide is searching for
    """
    for show in get_showlist:
        print(show)


if __name__ == '__main__':
    cli()