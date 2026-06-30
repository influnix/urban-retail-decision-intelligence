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
