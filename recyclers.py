import json

def get_object():
	with open('recyclers_db.json', encoding='utf-8') as json_file:
		data = json.load(json_file)
		return data


def get_closest(xy, type, top_x):
	availables = {}
	obj = get_object()
	for city in obj:
		try:
			availables[city] = obj[city][type]
		except Exception:
			continue
	arr = []
	for city in availables:
		for street in availables[city]:
			arr.append((city, street, calc_sqr_len(tuple(availables[city][street]), xy)))
	arr.sort(key=sorter)
	return arr[:top_x]


def get_types():
	obj = get_object()
	types = []
	for k in obj:
		for t in obj[k]:
			types.append(t)
	types = list(set(types))
	types.remove('null')
	return types


def calc_sqr_len(a, b):
	return (a[1] - b[0])**2 + (a[0] - b[1])**2

def sorter(elem):
	return elem[2]