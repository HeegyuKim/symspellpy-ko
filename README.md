# Symspellpy-ko 0.1.4
[symspellpy](https://github.com/mammothb/symspellpy)를 한글 특성에 맞춰서 수정한 라이브러리. 음소분해를 이용해 더 정확한 오타교정을 해준다.<br/>
symspellpy 6.7의 `SymSpell` 클래스를 가져와서 음소분해 기능을 추가하고 한글 단어사전을 추가했다.<br/>
사용법 역시 동일하며 우측 링크에서 확인 가능하다. https://symspellpy.readthedocs.io/en/latest/examples/index.html

## 왜 음소분해를 하는가?
1. 음소분해를 하지 않을 경우 `안녕`, `안뇽`, `안심` 이 세 어절은 같은 편집거리 1을 가진다. 조합된 한글이 1글자로 취급되기 때문이다.
2. 음소분해를 하면 `ㅇㅏㄴㅕㅇ`, `ㅇㅏㄴㅛㅇ`, `ㅇㅏㄴㅅㅣㅁ` 이렇게 음소별로 편집 거리를 갖게 되서 더 정밀하게 유사한 단어를 찾아서 오타교정이 가능하다.

## Examples
`pip`를 이용해 설치한다
```bash
pip install symspellpy-ko
```

먼저 `koSymSpell` 객체를 생성하고 `load_korean_dictionary` 메서드로 내장된 단어사전을 불러온다.<br/>
`decompose_korean`이 `True`일 경우 음소분해를 해준다. load_bigrams는 기본 False인데, 
lookup_compound와 word_segmentation을 사용해서 띄어쓰기 오류를 수정하기 위한 기능을 사용하려면 필요하다.

```python
from symspellpy_ko import KoSymSpell, Verbosity

sym_spell = KoSymSpell()
sym_spell.load_korean_dictionary(decompose_korean=True, load_bigrams=True)
```

### 어절과 유사한 어절들을 찾기
기본값으로 편집 거리가 2 이하인 어절을 찾는다.

```python
term = "안뇽하세요"
for suggestion in sym_spell.lookup(term, Verbosity.ALL):
  print(suggestion.term, suggestion.distance, suggestion.count)
```
결과
```
안녕하세요 1 3692
```
음소분해를 하지 않을 경우의 결과
```
안녕하세요 1 3692
안심하세요 1 18
하세요 2 1055
생각하세요 2 247
진정하세요 2 187
조심하세요 2 165
말씀하세요 2 119
... 총49개
```
### lookup compound를 이용해 오타교정과 띄어쓰기 문제까지 같이 찾아주기
```python
text = "그래도 괜찮지앟ㄴ을까"
for suggestion in sym_spell.lookup_compound(text, max_edit_distance=2):
  print(suggestion.term, suggestion.distance, suggestion.count)
```
결과
```
그래도 괜찮지 않을까 23 0
```

### word segmentation을 이용하여 띄어쓰기 분리
```python
text = "감기빨리치료해줘"
comp = sym_spell.word_segmentation(text, max_edit_distance=0)
print(comp.corrected_string)
```
결과
```
감기 빨리 치료 해줘
```

## Bad Cases
```python
text = "별 반개도 아깝다 욕나온다 이응경 길용우 연기생활이몇년인지..정말 발로해도 그것보단 낫겟다 납치.감금만반복반복..이드라마는 가족도없다 연기못하는사람만모엿네"

for suggestion in sym_spell.lookup_compound(text, max_edit_distance=2):
  print(suggestion.term, suggestion.distance, suggestion.count)
  
comp = sym_spell.word_segmentation(text, max_edit_distance=0)
print(comp.corrected_string)
```
결과
```
별 안해도 아깝다 이 나온다 이등병 기 용의 연기생활이몇년인지 정말 바 올해도 그것보단 낫겠다 납치 감금만반복반복 이 드라마를 가족 없다 연기못하는사람만모엿네 109 0
별 반 개도 아깝다 욕 나온다 이 응 경 길 용 우 연기 생활이 몇년 인지 .. 정말 발로 해도 그것보단 낫게 ㅅ 다 납치. 감금 만 반복 반복 .. 이 드라마 는 가족도 없다 연기 못하는 사람만 모여 ㅅ 네
```

1. 사전에 등록되지 않은 단어를 이상한 단어로 바꿔버린다.
2. 뉴스 데이터로 학습한 100만개의 bigram이 사전에 있지만 아직 부족하다. 때문에 `안해도`가 `반 개도` 처럼 바뀌는 모습이다.
3. `이응경` 같은 이름을 다 띄어쓰기로 바꿔버리는 모습도 나온다.
4. 더 많고 질 높은 데이터 구축이 필요하다...

## Credits
- [국립국어원 모두의 말뭉치](https://corpus.korean.go.kr/): 신문 말뭉치 2020(2.0), 문어 말뭉치(2.0), 구어 말뭉치(2.0), 일상 대화 말뭉치 2020(1.0)  2020(1.0)을 사용하여 한국어 Bigram 데이터셋을 구축했습니다.
- [SymSpell(MIT)](https://github.com/wolfgarbe/SymSpell)
- [SymSpellPy(MIT)](https://github.com/mammothb/symspellpy)
- [FrequencyWords(MIT)](https://github.com/hermitdave/FrequencyWords) 이곳에서 [한글 어절 빈도수 데이터](https://github.com/hermitdave/FrequencyWords/blob/master/content/2018/ko/ko_50k.txt)를 가져와서 사용했다.
- [hangul-utils(GPLv3)](https://github.com/kaniblu/hangul-utils): `pip install`로 할 경우 mecab이 의존성에 포함되어있어서, `split_syllables`와 `join_jamos` 두 함수만 사용하기 위해 [unicode.py](https://github.com/kaniblu/hangul-utils/blob/master/hangul_utils/unicode.py)만를 그대로 가져와서 사용했다. 
