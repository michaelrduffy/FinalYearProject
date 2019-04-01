#Generate valid creatures
import random as r



def findNextBracket(robot, start):
    return robot.find("[", start+1, len(robot))

def generate(n=10):
    robot = "F[]"
    numLayers = n
    startPos = 1

    for i in range(numLayers):
        x = r.randrange(100)
        if x > 25:
            if x > 50:
                robot = robot[:startPos+1] + "F[]" + robot[startPos+1:]
                startPos += 2
            else:
                robot = robot[:startPos+1] + "F" + robot[startPos+1:]
                startPos += 1
        else:
            robot = robot[:startPos+1] + "," + robot[startPos+1:]
            startPos += 1

        print startPos
        print robot


    print robot
    return robot
