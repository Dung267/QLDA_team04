from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="SurveyQuestion",
        ),
        migrations.RemoveField(
            model_name="surveyresponse",
            name="maintenance_request",
        ),
        migrations.AddConstraint(
            model_name="surveyresponse",
            constraint=models.UniqueConstraint(fields=["survey", "respondent"], name="uniq_survey_response_per_user"),
        ),
    ]