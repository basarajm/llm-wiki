# 로컬 아카이브(AnnualReport_MD) 인제스트 트래커 (KOSPI)

- 아카이브 회사 수: **814건** (source_documents/AnnualReport_MD/, 각 머신에 로컬 배치 필요·git 미포함)
- 완료(done, Full): **376건**
- 대기(pending): **438건** (이 중 stub→Full 승급 대상 72건)

> done 기준: wiki/companies/<회사>.md 가 존재하고 is_stub:false.
> market 판정: 위키 frontmatter 우선, 없으면 원본 MD의 '상장 유형' 표(유가증권시장/코스닥시장 상장)에서 추출.
> 이 파일은 `python dart_pipeline/local_archive_status.py [--market KOSPI|KOSDAQ]` 로 재생성됩니다.
> 다음 N개사 산출: `python dart_pipeline/local_archive_status.py [--market KOSPI|KOSDAQ] --next N`

## ⏳ 대기 (상위 50건, 전체 438건)

- DB (`KOSPI`) — `source_documents/AnnualReport_MD/DB-사업보고서-2025.12.md`
- DH오토넥스 (`KOSPI`) — `source_documents/AnnualReport_MD/DH오토넥스-사업보고서-2025.12.md`
- ESR켄달스퀘어리츠 (`KOSPI`) — `source_documents/AnnualReport_MD/ESR켄달스퀘어리츠-사업보고서-2025.11.md`
- F&F 홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/F&F 홀딩스-사업보고서-2025.12.md`
- HDC랩스 (`KOSPI`) — `source_documents/AnnualReport_MD/HDC랩스-사업보고서-2025.12.md`
- HL만도 (`KOSPI`) — `source_documents/AnnualReport_MD/HL만도-사업보고서-2025.12.md`
- HL홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/HL홀딩스-사업보고서-2025.12.md`
- IPARK현대산업개발 (`KOSPI`) — `source_documents/AnnualReport_MD/IPARK현대산업개발-사업보고서-2025.12.md`
- JW홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/JW홀딩스-사업보고서-2025.12.md`
- KB금융 (`KOSPI`) — `source_documents/AnnualReport_MD/KB금융-사업보고서-2025.12.md`
- KB스타리츠 (`KOSPI`) — `source_documents/AnnualReport_MD/KB스타리츠-사업보고서-2026.01.md`
- KEC (`KOSPI`) — `source_documents/AnnualReport_MD/KEC-사업보고서-2025.12.md`
- KG스틸 (`KOSPI`) — `source_documents/AnnualReport_MD/KG스틸-사업보고서-2025.12.md`
- KPX케미칼 (`KOSPI`) — `source_documents/AnnualReport_MD/KPX케미칼-사업보고서-2025.12.md`
- KPX홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/KPX홀딩스-사업보고서-2025.12.md`
- KSS해운 (`KOSPI`) — `source_documents/AnnualReport_MD/KSS해운-사업보고서-2025.12.md`
- KTis (`KOSPI`) — `source_documents/AnnualReport_MD/KTis-사업보고서-2025.12.md`
- LF (`KOSPI`) — `source_documents/AnnualReport_MD/LF-사업보고서-2025.12.md`
- LG생활건강 (`KOSPI`) — `source_documents/AnnualReport_MD/LG생활건강-사업보고서-2025.12.md`
- LG씨엔에스 (`KOSPI`) — `source_documents/AnnualReport_MD/LG씨엔에스-사업보고서-2025.12.md`
- LG에너지솔루션 (`KOSPI`) — `source_documents/AnnualReport_MD/LG에너지솔루션-사업보고서-2025.12.md`
- LG유플러스 (`KOSPI`) — `source_documents/AnnualReport_MD/LG유플러스-사업보고서-2025.12.md`
- LG헬로비전 (`KOSPI`) — `source_documents/AnnualReport_MD/LG헬로비전-사업보고서-2025.12.md`
- LG화학 (`KOSPI`) — `source_documents/AnnualReport_MD/LG화학-사업보고서-2025.12.md`
- LIG디펜스앤에어로스페이스 (`KOSPI`) — `source_documents/AnnualReport_MD/LIG디펜스앤에어로스페이스-사업보고서-2025.12.md`
- LS에코에너지 (`KOSPI`) — `source_documents/AnnualReport_MD/LS에코에너지-사업보고서-2025.12.md`
- LX세미콘 (`KOSPI`) — `source_documents/AnnualReport_MD/LX세미콘-사업보고서-2025.12.md`
- LX하우시스 (`KOSPI`) — `source_documents/AnnualReport_MD/LX하우시스-사업보고서-2025.12.md`
- LX홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/LX홀딩스-사업보고서-2025.12.md`
- MH에탄올 (`KOSPI`) — `source_documents/AnnualReport_MD/MH에탄올-사업보고서-2025.12.md`
- NAVER (`KOSPI`) — `source_documents/AnnualReport_MD/NAVER-사업보고서-2025.12.md`
- NC (`KOSPI`) — `source_documents/AnnualReport_MD/NC-사업보고서-2025.12.md`
- NH올원리츠 (`KOSPI`) — `source_documents/AnnualReport_MD/NH올원리츠-사업보고서-2025.12.md`
- NH프라임리츠 (`KOSPI`) — `source_documents/AnnualReport_MD/NH프라임리츠-사업보고서-2025.11.md`
- NICE (`KOSPI`) — `source_documents/AnnualReport_MD/NICE-사업보고서-2025.12.md`
- NICE평가정보 (`KOSPI`) — `source_documents/AnnualReport_MD/NICE평가정보-사업보고서-2025.12.md`
- OCI (`KOSPI`) — `source_documents/AnnualReport_MD/OCI-사업보고서-2025.12.md`
- PI첨단소재 (`KOSPI`) — `source_documents/AnnualReport_MD/PI첨단소재-사업보고서-2025.12.md`
- PKC (`KOSPI`) — `source_documents/AnnualReport_MD/PKC-사업보고서-2025.12.md`
- POSCO홀딩스 (`KOSPI`) — `source_documents/AnnualReport_MD/POSCO홀딩스-사업보고서-2025.12.md`
- SBS (`KOSPI`) — `source_documents/AnnualReport_MD/SBS-사업보고서-2025.12.md`
- SFA반도체 (`KOSPI`) — `source_documents/AnnualReport_MD/SFA반도체-사업보고서-2025.12.md`
- SHD (`KOSPI`) — `source_documents/AnnualReport_MD/SHD-사업보고서-2025.12.md`
- SJG세종 (`KOSPI`) — `source_documents/AnnualReport_MD/SJG세종-사업보고서-2024.12.md`
- SK (`KOSPI`) — `source_documents/AnnualReport_MD/SK-사업보고서-2025.12.md`
- SKC (`KOSPI`) — `source_documents/AnnualReport_MD/SKC-사업보고서-2025.12.md`
- SK가스 (`KOSPI`) — `source_documents/AnnualReport_MD/SK가스-사업보고서-2025.12.md`
- SK디앤디 (`KOSPI`) — `source_documents/AnnualReport_MD/SK디앤디-사업보고서-2025.12.md`
- SK리츠 (`KOSPI`) — `source_documents/AnnualReport_MD/SK리츠-사업보고서-2026.03.md`
- SK바이오사이언스 (`KOSPI`) — `source_documents/AnnualReport_MD/SK바이오사이언스-사업보고서-2025.12.md`
