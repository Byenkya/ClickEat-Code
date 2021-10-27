from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse


def join_telephone(code, telephone, joiner="-"):
	return f"{code}{joiner}{telephone}"


def split_telephone(telephone, splitter="-"):
	return telephone.split(splitter)


def attach_query_params(url, query_params_dict):
	url_parts = list(urlparse(url))
	params = dict(parse_qsl(url_parts[4]))
	params.update(query_params_dict)
	url_parts[4] = urlencode(params)
	return urlunparse(url_parts)