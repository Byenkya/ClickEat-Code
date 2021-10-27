from jinja2 import filters
from Application import app
from datetime import datetime
from wtforms.validators import DataRequired, InputRequired
import re


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M'):
	if isinstance(value, datetime):
		return value.strftime(format)


@app.template_filter('currency')
def currency(value):
	if isinstance(value, int):
		return f'{value:,} {app.config.get("DEFAULT_CURRENCY", "")}'
	return value



@app.template_filter('build_query_string')
def build_query_string(args):
	query_string = "?"
	for k, v in args.items():
		query_string += f"{k}={v}&"
	return query_string



@app.template_filter('is_required')
def is_required(field):
	for validator in field.validators:
		if isinstance(validator, (DataRequired, InputRequired)):
			return True
	return False



# filters.FILTERS['datetimeformat'] = datetimeformat
# filters.FILTERS['currency'] = currency
# filters.FILTERS['is_required'] = is_required
# filters.FILTERS['is_weekend'] = is_weekend
# filters.FILTERS['get_filled_activity_count'] = get_filled_activity_count
# filters.FILTERS['build_query_string'] = build_query_string


# app.jinja_env.globals.update(is_required=is_required)