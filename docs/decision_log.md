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

## Decision 002: CUDA 기반 PyTorch 환경 사용

### 상황

개발 장비에 NVIDIA RTX 3050 GPU가 설치되어 있으며, 향후 PyTorch 기반 신경망 모델과 시계열.공간 모델을 실험한 계획이다.

### 검토한 선택지

1. CPU 전용 PyTorch
2. CUDA 기반 GPU PyTorch
3. 초기에는 CPU를 사용하고 이후 GPU 환경으로 전환

### 결정

CUDA 12.6 기반 PyTorch 환경을 초기 개발환경으로 사용한다.

### 근거
- 현재 장비에서 `torch.cuda.is_available()`이 `True`로 확인됐다.
- 동일한 Conda 환경에서 데이터 처리와 GPU 학습을 모두 수행할 수 있다.
- 이후 MLP, Temporal Fusion Transformer, Graph Neural Network 등을 비교할 때 환경을 다시 구축할 필요가 없다.
- GPU 환경을 먼저 검증해 CUDA 호환성 문제를 초기 단계에서 발견할 수 있다.

### 확인 결과
- PyTorch 버전: `2.12.1+cu126`
- CUDA 사용 가능 여부: `True`
- 기본 텐서 연산 결과: `11.0`

### 위험 요소
- CUDA 패키지는 CPU 버전보다 설치 용량이 크다.
- PyTorch, torchvision, CUDA 버전 간 호환성이 맞지 않으면 실행 오류가 발생할 수 있다.
- GPU 메모리가 부족한 경우 배치 크기 조정이나 CPU 대체 실행이 필요하다.

### 재검토 조건
다음 상황이 발생하면 환경 구성을 다시 검토한다.
- PyTorch와 CUDA 버전 충돌
- GPU 메모리 부족으로 학습이 반복적으로 실패
- 클라우드 환경과 로컬 환경의 재현성 차이 발생
- 운영 파이프라인에서 CPU 실행이 더 경제적인 것으로 판단됨