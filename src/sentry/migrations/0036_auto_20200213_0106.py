# Generated by Django 1.11.28 on 2020-02-13 01:06

from django.db import migrations
import sentry.db.models.fields.bounded


class Migration(migrations.Migration):
    # This flag is used to mark that a migration shouldn't be automatically run in
    # production. We set this to True for operations that we think are risky and want
    # someone from ops to run manually and monitor.
    # General advice is that if in doubt, mark your migration as `is_dangerous`.
    # Some things you should always mark as dangerous:
    # - Large data migrations. Typically we want these to be run manually by ops so that
    #   they can be monitored. Since data migrations will now hold a transaction open
    #   this is even more important.
    # - Adding columns to highly active tables, even ones that are NULL.
    is_dangerous = False

    # This flag is used to decide whether to run this migration in a transaction or not.
    # By default we prefer to run in a transaction, but for migrations where you want
    # to `CREATE INDEX CONCURRENTLY` this needs to be set to False. Typically you'll
    # want to create an index concurrently when adding one to an existing table.
    atomic = True

    dependencies = [("sentry", "0035_auto_20200127_1711")]

    operations = [
        migrations.AlterField(
            model_name="pagerdutyserviceproject",
            name="organization_integration",
            field=sentry.db.models.fields.bounded.BoundedBigIntegerField(
                db_column="organization_integration_id", db_index=True, null=True
            ),
        ),
        migrations.AlterField(
            model_name="pagerdutyserviceproject",
            name="pagerduty_service",
            field=sentry.db.models.fields.bounded.BoundedBigIntegerField(
                db_column="pagerduty_service_id", db_index=True
            ),
        ),
        migrations.AlterField(
            model_name="pagerdutyserviceproject",
            name="project",
            field=sentry.db.models.fields.bounded.BoundedBigIntegerField(db_column="project_id"),
        ),
    ]