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

### Actual result
실행 후 직접 기록:

### Errors
오류가 있으면 원문을 그대로 기록:

### Conclusion
실행 후 직접 기록: