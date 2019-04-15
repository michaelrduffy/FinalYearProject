import xmltodict as xml
import json
import pybullet as p
import time
import pybullet_data
import math
import os
import binascii
import redis
import random
from elasticsearch import Elasticsearch
#Recusively find links:
# - Find previous [:
  # Go back through lstring
# - Get Id and generate link

#Programmatically find edges of blocks:
#Origin + Width/2
BRANCH_TERMINATORS = ['[', ']']
PARAM_STARTS = ['(', '{']
PARAM_ENDS = [')', '}']

r = redis.Redis(host='192.168.0.9', port=6379, db=0)
resultsDb = redis.Redis(host='192.168.0.9', port=6379, db=1)
es = Elasticsearch({'host':'192.168.0.9'})
out = None
key = -1
obj = {}

def translate_char(char, idx, params=None):
    OBJ_PARAMS = ["x", "y", "z", "mass"]
    initScale = 0.2
    cube = json.loads("""
          {
            "@name": "unset",
            "visual": {
              "geometry": {
                "box": {
                  "@size": "0.2 0.2 0.2"
                }
              },
              "origin": {
                "@rpy": "0 0 0",
                "@xyz": "0 0.0 0"
              },
              "material": {
                "@name": "white",
                "color": {
                  "@rgba": "1 1.0 1.0 1.0"
                }
              }
            },
            "collision": {
              "geometry": {
                "box": {
                  "@size": "0.2 0.2 0.2"
                }
              },
              "origin": {
                "@rpy": "0 0 0",
                "@xyz": "0 0.0 0.0"
              }
            },
            "inertial": {
              "mass": {
                "@value": "1"
              },
              "inertia": {
                "@ixx": "0.000",
                "@ixy": "0.0",
                "@ixz": "0.0",
                "@iyy": "0.000",
                "@iyz": "0.0",
                "@izz": "0.0"
              },
              "origin": {
                "@rpy": "0 0 0",
                "@xyz": "0 0 0"
              }
            }
          }
    """)
    if char == 'F':
        temp = cube.copy()
        temp["@name"] = idx

        if params != None:
            dimensions = [0.2,0.2,0.2]
            for foo, p in enumerate(params):
                toChange = OBJ_PARAMS[foo]
                if toChange == "x":
                    x = initScale * float(p)
                    dimensions[0] = x
                elif toChange == "y":
                    y = initScale * float(p)
                    dimensions[1] = y
                elif toChange == "z":
                    z = initScale * float(p)
                    dimensions[2] = z
                elif toChange == "mass":
                    temp["inertial"]["mass"]["@value"] = float(p)
            newDimensions = [str(d) for d in dimensions]
            newDimensions = ' '.join(newDimensions)
            temp["visual"]["geometry"]["box"]["@size"] = newDimensions
            temp["collision"]["geometry"]["box"]["@size"] = newDimensions

        return temp
    elif char == '[':
        #Recursion!!?
        return 'Branch Start'
    elif char == ']':
        #End Recursion!!
        return 'Branch End'

def make_joint(parent, child, childobj, params=None, num=0):
    if num > 0:
        num = num % 6
    JOINT_PARAMS = ["axis", "effort", "velocity", "upper", "lower"]
    dimensions = childobj["collision"]["geometry"]["box"]["@size"].split(' ')
    dimensions = [float(d) for d in dimensions]

    joint = json.loads("""
      {
            "@name": "base_flap",
            "@type": "revolute",
            "parent": {
              "@link": ""
            },
            "child": {
              "@link": ""
            },
            "axis": {
              "@xyz": "0 0 1"
            },
            "limit": {
              "@upper": "1.9",
              "@lower": "-1.9",
              "@effort": "0",
              "@velocity": "0"
            },
            "origin": {
              "@rpy": "0 0 0",
              "@xyz": "0.1 0.0 0.0"
            }
          }
    """)
    temp = joint.copy()
    temp["@name"] = parent+child
    temp["type"] = 'revolute'
    temp["parent"]["@link"] = parent
    temp["child"]["@link"] = child
    if num == 0:
        o = [0.0, 1.0, 0.0]
        origin = str(dimensions[0]*o[0]) + ' ' + str(dimensions[1]*o[1]) + ' ' + str(dimensions[2]*o[2])
    elif num == 1:
        o = [1.0, 0.0, 0.0]
        origin = str(dimensions[0]*o[0]) + ' ' + str(dimensions[1]*o[1]) + ' ' + str(dimensions[2]*o[2])
    elif num == 2:
        o = [0.0, -1.0, 0.0]
        origin = str(dimensions[0]*o[0]) + ' ' + str(dimensions[1]*o[1]) + ' ' + str(dimensions[2]*o[2])
    elif num == 3:
        o = [-1.0, 0.0, 0.0]
        origin = str(dimensions[0]*o[0]) + ' ' + str(dimensions[1]*o[1]) + ' ' + str(dimensions[2]*o[2])
    elif num == 4:
        o = [0.0, 0.0, 1.0]
        origin = str(dimensions[0]*o[0]) + ' ' + str(dimensions[1]*o[1]) + ' ' + str(dimensions[2]*o[2])
        temp["axis"]['@xyz'] = "1 0 0"
        neworig = [0.0, 0.0, -0.5]
        neworigin = str(dimensions[0]*neworig[0]) + ' ' + str(dimensions[1]*neworig[1]) + ' ' + str(dimensions[2]*neworig[2])
        childobj["visual"]["origin"]["@xyz"] = neworigin
        childobj["collision"]["origin"]["@xyz"] = neworigin
        childobj["inertial"]["origin"]["@xyz"] = neworigin
    elif num == 5:
        o = [0.0, 0.0, -1.0]
        origin = str(dimensions[0]*o[0]) + ' ' + str(dimensions[1]*o[1]) + ' ' + str(dimensions[2]*o[2])
        temp["axis"]['@xyz'] = "1 0 0"
        neworig = [0.0, 0.0, 0.5]
        neworigin = str(dimensions[0]*neworig[0]) + ' ' + str(dimensions[1]*neworig[1]) + ' ' + str(dimensions[2]*neworig[2])
        childobj["visual"]["origin"]["@xyz"] = neworigin
        childobj["collision"]["origin"]["@xyz"] = neworigin
        childobj["inertial"]["origin"]["@xyz"] = neworigin
    temp["origin"]["@xyz"] = origin
    if params != None:
        for idx, p in enumerate(params):
            toChange = JOINT_PARAMS[idx]
            if toChange == "axis":
                #do thing
                a = 1 + (int(p)% 7)
                if a == 1:
                    a = "0 0 1"
                elif a == 2:
                    a = "0 1 0"
                elif a == 3:
                    a = "0 1 1"
                elif a == 4:
                    a = "1 0 0"
                elif a == 5:
                    a = "1 0 1"
                elif a == 6:
                    a = "1 1 0"
                elif a == 7:
                    a = "1 1 1"
                temp["axis"]["@xyz"] = a
            elif toChange == "effort":
                temp["limit"]["@effort"] = float(p)
            elif toChange == "velocity":
                temp["limit"]["@velocity"] = float(p)
            elif toChange == "upper":
                temp["limit"]["@upper"] = float(p)
            elif toChange == "lower":
                temp["limit"]["@lower"] = float(p)
    return temp

#Read string char by char
#Could turn into a list comprehension

#Lists of lists
# New List on [], filled with children
# Is this bad? - Probably

def generate_id():
    return binascii.b2a_hex(os.urandom(4))

def build_robot(lstring):
    joints = []
    links = []
    def create_branch(subString, parentId):
        branch = []
        tempString = subString[:]
        childId = None
        str_iter = enumerate(subString)
        for i, char in str_iter:
            if char not in BRANCH_TERMINATORS:
                if char == ',':
                    continue
                childId = generate_id()
                objParams = ''
                jointParams = ''
                print '\n'
                print "SubString: " + subString
                print "TempString: " + tempString
                skip = 0
                if subString[i+1] in PARAM_STARTS:
                    endChar = PARAM_ENDS[PARAM_STARTS.index(subString[i+1])]
                    end = subString.find(endChar, i+1)
                    if endChar == '}':
                        objParams = subString[i+2:end]
                        skip = end
                    elif endChar == ')':
                        jointParams = subString[i+2:end]
                        skip = end
                    i = i+skip
                    if(len(subString)-1 > i+1):
                        if subString[i+1] in PARAM_STARTS:
                            endChar = PARAM_ENDS[PARAM_STARTS.index(subString[i+1])]
                            end = subString.find(endChar, i+1)
                            if endChar == '}':
                                objParams = subString[i+2:end]
                                skip = end
                            elif endChar == ')':
                                jointParams = subString[i+2:end]
                                skip = end
                            i = i+skip
                objParams = objParams.split(' ') if objParams != '' else None
                jointParams = jointParams.split(' ') if jointParams != '' else None

                print objParams
                print jointParams
                print char
                temp = translate_char(char, childId, params=objParams)
                branch.append(temp)
                if parentId != None:
                    joints.append(make_joint(parentId, childId, temp, params=jointParams, num=i))
                if parentId == None:
                    parentId = childId
                for foo in range(skip):
                    str_iter.next()
            elif char == '[':
                numOpen = 0
                numClosed = 0
                end = None
                for j, c in enumerate(tempString[i:]):
                    if c == '[':
                        numOpen += 1
                    elif c == ']':
                        numClosed += 1

                    if numOpen == numClosed and numOpen != 0:
                        end = j
                        break
                #Send parent Id
                create_branch(tempString[i+1:end+i],branch[-1]["@name"])
                break
            elif char == ']':
                #end branch
                links.extend(branch)
                return branch
        links.extend(branch)
        return branch

    branch = create_branch(lstring, None)
    x = {'branch' : branch, 'joints' : joints, 'links' : links}
    '''
        Iterate through list
        on [ create new list recurse until ]
    '''
    joints = x['joints']
    links = x['links']
    out = { "robot" : {
        "@name" : "paul",
        "link" : links,
        "joint" : joints
    }}

    parents = [x['parent']['@link'] for x in joints]
    children = [x['child']['@link'] for x in joints]
    try:
        os.remove("robot.urdf")
    except:
        print "robot.urdf does not exist"
    with open("robot.urdf", "w") as f:
        f.write(xml.unparse(out, pretty=True))

    return "robot.urdf"

# x = [translate_char(char, i) for i, char in enumerate(robot) if char not in ['[',']']]
