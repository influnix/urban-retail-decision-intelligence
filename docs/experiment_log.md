# Experiment Log

## EXP-000: Environment verification

### Objective

Python, 주요 데이터 패키지 및 PyTorch가 동일한 Conda 환경에서
정상 실행되는지 확인한다.

### Expected result

- Python executable path에 `envs\mosaic`이 포함된다.
- PyTorch tensor 연산 결과가 11.0이다.
- pytest가 1개의 테스트를 통과한다.

### Command

```powershell
python scripts\verify_environment.py
pytest
ruff check .
```

### 실제 결과
- Python 실행 경로: `C:\Users\PC\miniconda3\envs\mosaic\python.exe`
- Python 버전: `3.11.15`
- NumPy 버전: `2.4.6`
- pandas 버전: `3.0.4`
- scikit-learn 버전: `1.9.0`
- PyTorch 버전: `2.12.1+cu126`
- CUDA 사용 가능 여부: `True`
- 텐서 행렬곱 결과: `11.0`
- pytest 결과: `1 passed`
- Ruff 결과: `All checks passed`

### 발생한 오류
최초 실행에서 다음 오류가 발생했다.
```
can't open file '...\scripts\verify_environment.py': 
[Errno 2] No such file or directory
```

### 오류 원인
`scripts` 디렉터리는 생성했지만 `verify_environment.py` 파일을 생성하기 전에 실행했다.
파일을 생성한 후 동일 명령을 다시 실행하자 정상적으로 통과했다.

### 결론
Conda 환경 안에서 Python, 주요 데이터 분석 패키지, PyTorch 및 CUDA가 정상적으로 실행된다.
자동 테스트와 정적 코드 검사도 통과했으므로 초기 개발환경 검증을 완료했다.
초기 오류는 패키지나 환경 문제가 아니라 실행 대상 파일이 존재하지 않아 발생한 작업 순서 문제였다.

---

## EXP-001

### 발생한 오류

1. Ruff에서 import 정렬 오류 `I001`이 발생했다.
2. 일반 Python 실행에서 `mosaic` 패키지를 찾지 못했다.

### 원인 분석

pytest는 `pyproject.toml`의 `pythonpath = ["src"]` 설정을 사용하지만,
일반 python 스크립트 실행에는 해당 설정이 적용되지 않는다.

따라서 테스트에서는 import가 성공했지만,
`python scripts/inspect_raw_archives.py` 실행에서는
`src/mosaic` 패키지를 찾지 못했다.

### 해결 방법

프로젝트에 build system과 package discovery 설정을 추가하고
`python -m pip install -e .` 명령으로 editable package로 설치했다.

---

## EXP-002: 점포 데이터 스키마 표준화

### 목적

2021년~2024년 한국어 헤더와 2025년 영문 헤더를
하나의 내부 표준 스키마로 변환할 수 있는지 검증한다.

### 사전 예상

- 2021년~2024년 파일은 동일한 한국어 헤더 구조를 사용할 것으로 예상했다.
- 2025년 파일은 영문 약어 헤더를 사용하므로 원본 스키마 서명이 다를 것으로 예상했다.
- 연도별 원본 헤더를 명시적인 alias 매핑으로 변환하면, 모든 연도를 동일한 14개 표준 컬럼으로 정규화할 수 있을 것으로 예상했다.
- 필수 컬럼이 매핑표에서 누락되면 빈 컬럼을 생성해 계속 실행하지 않고 즉시 오류가 발생해야 한다.

### 실행 명령

```powershell
pytest tests\ingestion\test_schema_contract.py
python scripts\validate_store_schema.py
pytest
ruff check .
```

### 실제 결과

- 스키마 계약 단위 테스트: `5 passed`
- 전체 테스트: `11 passed`
- Ruff: `All checks passed`
- 2021년~2025년 모든 파일의 원본 컬럼 수: 14개
- 정규화 이후 컬럼 수: 14개
- 스키마 검증 실패 건수: 0건
- 정규화 이후 스키마 서명: 1개로 통일
- 2025년 영문 약어 헤더도 alias 매핑을 통해 동일한 내부 표준 컬럼으로 변환됐다.

### 발견한 스키마 변화

- 2021년~2024년은 동일한 한국어 헤더 구조를 사용한다.
- 2025년은 같은 의미의 데이터를 영문 약어 헤더로 제공한다.
- 따라서 원본 스키마 서명은 2025년에 변경됐지만, 컬럼 의미와 개수는 alias 매핑을 통해 기존 표준 스키마로 정규화할 수 있었다.
- 내부 표준 컬럼은 의미가 명확한 영어 `snake_case` 14개로 통일했다.

### 위험

- 신규 연도에 또 다른 헤더명이 등장하면 alias 매핑을 갱신하지 않는 한 파이프라인이 중단될 수 있다.
- 철자가 비슷하다는 이유로 컬럼을 자동 추측해 매핑하면 서로 다른 의미의 컬럼이 잘못 연결될 수 있다.
- 컬럼명과 개수가 같더라도 값의 정의, 단위 또는 코드체계가 변경되면 현재의 스키마 검사만으로는 탐지하지 못할 수 있다.
- 필수 컬럼 누락 시 빈 컬럼을 생성해 계속 실행하면 결측값이 조인, 집계, 후보 키 검사와 모델 입력까지 전파될 수 있다.
- 여러 원본 컬럼이 하나의 표준 컬럼으로 충돌하지 않는지 지속적으로 검사해야 한다.

### 결론

2021년~2025년 점포 데이터의 서로 다른 원본 헤더를 하나의 내부 표준 스키마로 변환하는 데 성공했다.
2025년의 원본 스키마 변경은 명시적 alias 매핑으로 처리했으며,
정규화 이후 모든 연도는 동일한 14개 컬럼과 하나의 스키마 서명을 갖는다.

필수 컬럼 누락을 즉시 실패시키는 데이터 계약과 자동 테스트를 함께 구성했으므로,
원본 제공기관의 헤더 변경이 조용히 후속 파이프라인으로 전파되는 위험을 줄였다.
다음 단계에서는 컬럼 존재 여부뿐 아니라 행 수, 분기 범위, 결측률,
후보 키 중복, 코드-이름 대응 관계와 값 범위를 검증한다.
