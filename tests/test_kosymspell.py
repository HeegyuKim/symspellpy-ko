from symspellpy_ko import KoSymSpell, split_syllables, join_jamos, Verbosity
import pytest


@pytest.fixture
def sym_spell():
    sp = KoSymSpell()
    sp.load_korean_dictionary(decompose_korean=True, load_bigrams=True)

    return sp


@pytest.fixture
def term():
    return "안뇽하세요"


@pytest.fixture
def text():
    return "별 반개도 아깝다 욕나온다 이응경 길용우 연기생활이몇년인지..정말 발로해도 그것보단 낫겟다 납치.감금만반복반복..이드라마는 가족도없다 연기못하는사람만모엿네"


def test_lookup(sym_spell, term):
    lookup = sym_spell.lookup(term, Verbosity.CLOSEST)[0]
    assert lookup.term == "안녕하세요"
    assert lookup.distance == 1


def test_lookup_compound(sym_spell, text):
    sugg = sym_spell.lookup_compound(text, max_edit_distance=2)
    comp = " ".join([w.term for w in sugg])

    fixed_text = "별 안해도 아깝다 이 나온다 이등병 기 용의 연기생활이몇년인지 정말 바 올해도 그것보단 낫겠다 납치 감금만반복반복 이 드라마를 가족 없다 연기못하는사람만모엿네"
    assert comp == fixed_text


def test_word_segmentation(sym_spell, text):
    ws = sym_spell.word_segmentation(text, max_edit_distance=0)

    fixed_text = "별 반 개도 아깝다 욕 나온다 이 응 경 길 용 우 연기 생활이 몇년 인지 .. 정말 발로 해도 그것보단 낫게 ㅅ 다 납치. 감금 만 반복 반복 .. 이 드라마 는 가족도 없다 연기 못하는 사람만 모여 ㅅ 네"

    assert ws.corrected_string == fixed_text
