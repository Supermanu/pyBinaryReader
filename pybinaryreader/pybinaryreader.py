import json
import subprocess

def getVector(dic):
    vec = []
    for v in dic['children']:
        vec.append(v['value'])
    return vec

def simplifyAABB(AABB):
    newDic = {}
    for e in AABB:
        if 'name' in e:
            if e['name'] == 'min':
                newDic['min'] = getVector(e)
            elif e['name'] == 'max':
                newDic['max'] = getVector(e)
            elif e['name'] == 'leaf_face':
                newDic['leaf_face'] = e['value']
            elif e['name'] == 'plane':
                newDic['plane'] = e['value']
            elif e['name'] == 'leftOffset':
                newDic['leftOffset'] = e['value']
            elif e['name'] == 'rightOffset':
                newDic['rightOffset'] = e['value']

    if newDic['leftOffset'] > 0:
        newDic['leftNode'] = simplifyAABB(AABB[len(AABB) - 2]['pointerTo'][0]['children'][0]['children'])
    if newDic['rightOffset'] > 0:
        newDic['rightNode'] = simplifyAABB(AABB[len(AABB) - 1]['pointerTo'][0]['children'][0]['children'])
    return newDic

def simplifyVector(arr):
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

def arrayToDic(arr, tab=0, game='nwn'):
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
 
                    newDic[e['children'][0]['name']] = arrayToDic(e['children'][0]['children'], tab+1, game)
                    continue
                for c in children:
                    new_children.append(simplifyDic(c))
                newDic[e['name']] = new_children
                continue
            else:
                print("DUNNO")
                continue
        elif 'pointerTo' in e:
            if e['pointerTo'][0]['name'] == 'faces' and game == 'nwn':
                newDic[e['pointerTo'][0]['name']] = simplifyFaces(arrayToDic(e['pointerTo'][0]['children'], tab+1, game))
                continue

            if e['pointerTo'][0]['name'] == 'vertices' or e['pointerTo'][0]['name'] == 'faces':
                newDic[e['pointerTo'][0]['name']] = simplifyVector(e['pointerTo'][0]['children'])
                continue

            if e['pointerTo'][0]['name'] == 'AABBrec':
                newDic['AABB'] = simplifyAABB(e['pointerTo'][0]['children'][0]['children'])
                continue

            newDic[e['pointerTo'][0]['name']] = arrayToDic(e['pointerTo'][0]['children'], tab+1, game)
            continue
        else:
            print("DUNNO DUNNO")

    return newDic

class Wok:
    def __init__(self, file_path, binaryreader_path = None, game='kotor'):
        self.game = game
        data = []
        if binaryreader_path:
            data = json.loads(subprocess.getoutput(binaryreader_path + " -j " + file_path + " -g kotor"))['children']
        else:
            f = open(file_path, 'r')
            data = json.loads(f.read())['children']

        self.model = arrayToDic(data, game=self.game)

class Model:
	def __init__(self, file_path, binaryreader_path = None, game = 'nwn'):
		self.game = game
		data = []
		if binaryreader_path:
			data = json.loads(subprocess.getoutput(binaryreader_path + " -j " + file_path))['children']
		else:
			f = open(file_path, 'r')
			data = json.loads(f.read())['children']

		self.model = arrayToDic(data, game=self.game)

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
