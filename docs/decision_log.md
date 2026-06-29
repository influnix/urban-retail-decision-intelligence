# Decision Log

## Decision 001: Use Python 3.11

### Context

PyTorch와 데이터 분석 패키지를 안정적으로 함께 사용해야 한다.

### Alternatives

1. Python 3.10
2. Python 3.11
3. 최신 Python 버전

### Decision

Python 3.11을 사용한다.

### Reason

최신 문법보다 패키지 호환성과 프로젝트 재현성을 우선한다.

### Risk

장기 프로젝트 중 일부 최신 패키지가 더 높은 Python 버전을
요구할 가능성이 있다.

### Revisit condition

핵심 패키지가 Python 3.11 지원을 종료하거나,
필수 기능이 상위 버전에서만 제공될 때 재검토한다.

---

## Decision 002: Start with CPU PyTorch

### Context

초기 단계의 목적은 환경과 데이터 파이프라인 검증이다.

### Decision

GPU 설정 전에 CPU 버전으로 PyTorch 동작을 검증한다.

### Reason

초기 환경 오류와 CUDA 호환성 오류를 분리하기 위해서다.

### Revisit condition

신경망 학습 시간이 실제 개발 병목이 될 때 GPU 환경을 구성한다.