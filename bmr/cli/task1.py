# import click
from flask import Blueprint
from ..models import db

task1_bp = Blueprint('dba', __name__)


@task1_bp.cli.command('init2')
def init():
    # session = db.session()
    print(f"hello world")
    # print(f"session: {session}")
