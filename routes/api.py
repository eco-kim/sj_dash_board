from struct import calcsize
from sys import modules
from flask import Blueprint, render_template
from modules import calc

##다운로드는 csv? 

##클라에서 서비스종류, api 종류, 조회원하는 기간 받아야함

##services : kitech, lme, lms
##api 종류는 아직 알 수 없음.
##db 테이블 구조를 통일해야 하나의 함수로 처리 가능.

api = Blueprint('api', __name__)


@api.route("/api", methods=['GET'])
async def kitechCalls():
    return