# SmartNougat 설치 가이드 (Windows 10/11)

## 사전 준비사항

### 1. Python 설치 확인
- Windows 명령 프롬프트(cmd) 실행
- `python --version` 입력
- Python 3.8 이상이 설치되어 있어야 합니다
- 없다면 https://www.python.org/downloads/ 에서 다운로드
- **중요**: 설치 시 "Add Python to PATH" 체크박스 반드시 선택!

### 2. Git 설치 확인
- 명령 프롬프트에서 `git --version` 입력
- 없다면 https://git-scm.com/download/win 에서 다운로드

## 설치 방법

### 방법 1: 자동 설치 (권장)

1. **리포지토리 클론**
   ```cmd
   git clone https://github.com/charles69729798/SmartNougat.git
   cd SmartNougat
   ```

2. **설치 스크립트 실행**
   ```cmd
   install_windows.bat
   ```
   - 자동으로 모든 필요한 패키지를 설치합니다
   - 약 5-10분 소요됩니다

3. **설치 확인**
   - 설치가 완료되면 자동으로 테스트가 실행됩니다
   - 모든 항목에 ✓ 표시가 나타나면 성공!

### 방법 2: 수동 설치

1. **리포지토리 클론**
   ```cmd
   git clone https://github.com/charles69729798/SmartNougat.git
   cd SmartNougat
   ```

2. **패키지 설치**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Nougat LaTeX OCR 설치**
   ```cmd
   git clone https://github.com/Norm/nougat-latex-ocr.git
   cd nougat-latex-ocr
   pip install -e .
   cd ..
   ```

4. **YOLO MFD 모델 다운로드**
   ```cmd
   python download_mfd_model.py
   ```

## 사용 방법

### 기본 사용법
```cmd
run_smartnougat.bat 문서.pdf
```

### 페이지 지정
```cmd
run_smartnougat.bat 문서.pdf 1-10
```

### DOCX 파일 처리
```cmd
run_smartnougat.bat 문서.docx
```

## 문제 해결

### Python을 찾을 수 없다는 오류
1. Python이 PATH에 추가되었는지 확인
2. 시스템 환경 변수에서 PATH 확인
3. Python 재설치 (PATH 추가 옵션 체크)

### pip 오류
```cmd
python -m ensurepip --default-pip
python -m pip install --upgrade pip
```

### 한글이 깨져서 보일 때
```cmd
set PYTHONIOENCODING=utf-8
chcp 65001
```

### CUDA/GPU 오류
- CPU 버전으로 자동 설치됩니다
- GPU 사용을 원하면 CUDA 설치 필요

## 출력 결과

처리가 완료되면 다음 파일들이 생성됩니다:
- `output_문서명_날짜시간/` 폴더
  - `layout.pdf` - 수식 위치가 표시된 PDF
  - `result_viewer.html` - 결과 뷰어
  - `txt/output.md` - 추출된 텍스트와 수식
  - `images/` - 추출된 수식 이미지들

## 지원 및 문의

문제가 발생하면 GitHub Issues에 문의해주세요:
https://github.com/charles69729798/SmartNougat/issues