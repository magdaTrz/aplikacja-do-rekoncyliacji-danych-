from pytest import fixture
from models.mate.mate import Mate
from text_variables import TextEnum


@fixture
def mate_load():
    return Mate(
        stage=TextEnum.LOAD
    )

@fixture
def mate_end():
    return Mate(
        stage=TextEnum.END
    )
