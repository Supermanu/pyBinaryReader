import json
import subprocess

def simplifyVertices(arr):
    newVertices = []
    for v in arr:
        vertex = []
        for vp in v['children'][0]['children']:
            vertex.append(vp['value'])
        newVertices.append(vertex)

    return newVertices

def simplifyFaces(dic):
    newFaces = [None for _ in range(len(dic))]
    for k,v in dic.items():
        faceDic = {}
        # Normal vector
        normal = []
        for n in v[0]['children']:
            normal.append(n['value'])
        faceDic['normal'] = normal

        # Plane distance
        faceDic['plane_distance'] = [] # TODO: should be v[1]['value']

        # Smooth property
        faceDic['smooth'] = v[2]

        # Vertices index
        vertices_index = []
        for vi in v[4]['children']:
            vertices_index.append(vi['value'])
        faceDic['vertices_index'] = vertices_index
        newFaces[int(k[6:])] = faceDic

    return newFaces

def simplifyDic(dic):
    if not 'children' in dic and 'value' in dic and 'name' in dic:
        return dic['value']
    else:
        return dic

def arrayToDic(arr, tab=0):
    newDic = {}
    for e in arr:
        if 'name' in e:
            #print(tab * '\t' + e['name'])
            if 'value' in e and not 'children' in e:
                newDic[e['name']] = e['value']
                continue
            elif 'children' in e and not 'value' in e:
                if e['name'] == 'Padding':
                    continue
                new_children = []
                children = e['children']
                if len(e['children']) == 1:
 
                    newDic[e['children'][0]['name']] = arrayToDic(e['children'][0]['children'], tab+1)
                    continue
                for c in children:
                    new_children.append(simplifyDic(c))
                newDic[e['name']] = new_children
                continue
            else:
                print("DUNNO")
                continue
        elif 'pointerTo' in e:
            if e['pointerTo'][0]['name'] == 'faces':
                newDic[e['pointerTo'][0]['name']] = simplifyFaces(arrayToDic(e['pointerTo'][0]['children'], tab+1))
                continue

            if e['pointerTo'][0]['name'] == 'vertices':
                newDic['vertices'] = simplifyVertices(e['pointerTo'][0]['children'])
                continue

            newDic[e['pointerTo'][0]['name']] = arrayToDic(e['pointerTo'][0]['children'], tab+1)
            continue
        else:
            print("DUNNO DUNNO")

    return newDic

class Model:
	def __init__(self, file_path, binaryreader_path = None):
		data = []
		if binaryreader_path:
			data = json.loads(subprocess.getoutput(binaryreader_path + " -j " + file_path))['children']
		else:
			f = open(file_path, 'r')
			data = json.loads(f.read())['children']

		self.model = arrayToDic(data)

	def getNode(self, node):
		if node == 'rootNode':
			return self.model['rootNode']

		for k,v in self.model['rootNode']['children'].items():
			if v['nodeName'].startswith(node):
				return v

		return None

	def getNodes(self, flag):
		nodes = []
		if self.model['rootNode']['flags'] == flag:
			nodes.append(self.model['rootNode'])

		for k,v in self.model['rootNode']['children'].items():
			if v['flags'] == flag:
				nodes.append(v)

		return nodes
