from app import app
import os
import click

@app.cli.group()
def translate():
    """翻譯和本地化命令。"""
    pass

@translate.command()
def update():
    """更新所有語言。"""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract 命令失敗')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update 命令失敗')
    os.remove('messages.pot')

@translate.command()
def compile():
    """編譯所有語言。"""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile 命令失敗')
    
@translate.command()
@click.argument('lang')
def init(lang):
    """初始化一種新語言。"""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract 命令失敗')
    if os.system(
            'pybabel init -i messages.pot -d app/translations -l' + lang):
        raise RuntimeError('init 命令失敗')
    os.remove('messages.pot')