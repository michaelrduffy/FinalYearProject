import pytest
import parser
import pybullet as p

# Test that parser output is readable by pybullet
# Needs more test cases
# Test cases can be randomly generated using the generator file but they will
# all pass by design
@pytest.mark.parametrize("robot,expected", [("F[]", True), ("F[F{F}]", False)])
def test_parser_output(robot, expected):
    result = False
    try:
        file = parser.build_robot(robot)
        physicsClient = p.connect(p.DIRECT)
        cubeStartPos = [0,0,0]
        cubeStartOrientation = p.getQuaternionFromEuler([0,0,0])
        boxId = p.loadURDF(file,cubeStartPos, cubeStartOrientation)
        result = True
    except:
        result = False
    finally:
        assert result == expected
