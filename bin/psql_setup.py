#!/usr/bin/env python
import os
import click
from pgrag.models import Document
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from dotenv import load_dotenv
import psycopg2


def create_table_ddl():
    engine = create_engine("postgresql://")

    tables = map(
        lambda t: str(CreateTable(t).compile(engine)),
        Document.metadata.tables.values(),
    )
    return "\n".join(list(tables))


def execute_sql(url, sql):
    conn = psycopg2.connect(url)
    cur = conn.cursor()

    cur.execute(sql)
    conn.commit()

    res = None
    try:
        res = cur.fetchall()
    except psycopg2.ProgrammingError as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return res


@click.group()
@click.option("--tf_output", "-to", default=None)
@click.pass_context
def group(ctx, tf_output):
    load_dotenv()

    ctx.ensure_object(dict)
    ctx.obj["DATABASE_URL"] = (
        "postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_INSTANCE}:5432/{POSTGRES_DB}".format(
            **os.environ
        )
    )


@group.command()
@click.pass_context
def setup_vector(ctx):
    """vector(pgVextro) の設定"""
    sql = """CREATE EXTENSION IF NOT EXISTS vector;"""
    execute_sql(ctx.obj["DATABASE_URL"], sql)


@group.command()
@click.pass_context
def create_schema(ctx):
    """スキーマ作成"""
    params = Document.__table_args__
    sql = """CREATE SCHEMA {schema};""".format(**params)
    execute_sql(ctx.obj["DATABASE_URL"], sql)


@group.command()
@click.pass_context
def create_role(ctx):
    """ロール(アクセスユーザー)作成"""
    sql = """CREATE ROLE {ROLE_USER} WITH PASSWORD '{ROLE_PASSWORD}' LOGIN;""".format(
        **os.environ
    )
    res = execute_sql(ctx.obj["DATABASE_URL"], sql)
    print(res)


@group.command()
@click.pass_context
def create_table(ctx):
    """KBテーブル作成"""
    sql = create_table_ddl()
    res = execute_sql(ctx.obj["DATABASE_URL"], sql)
    print(res)


@group.command()
@click.pass_context
def create_vector_index(ctx):
    """ベクトルフィールドにインデックス作成"""
    field = Document.get_vector_field()
    params = dict(
        table_name=Document.__tablename__, field=field.name, **Document.__table_args__
    )
    sql = "CREATE INDEX on {schema}.{table_name} USING hnsw ({field} vector_cosine_ops);".format(
        **params
    )
    res = execute_sql(ctx.obj["DATABASE_URL"], sql)
    print(res)


@group.command()
@click.pass_context
def grant_schema(ctx):
    """スキーマに許可"""
    params = dict(username=os.getenv("ROLE_USER"), **Document.__table_args__)
    sql = """GRANT ALL ON SCHEMA {schema} to {username};""".format(**params)
    res = execute_sql(ctx.obj["DATABASE_URL"], sql)
    print(res)


@group.command()
@click.pass_context
def grant_table(ctx):
    """テーブルに許可"""
    params = dict(
        table_name=Document.__tablename__,
        username=os.getenv("ROLE_USER"),
        **Document.__table_args__,
    )
    sql = """GRANT ALL ON TABLE {schema}.{table_name} to {username};""".format(**params)
    res = execute_sql(ctx.obj["DATABASE_URL"], sql)
    print(res)


if __name__ == "__main__":
    group()
