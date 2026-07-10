# 로컬 아카이브(AnnualReport_MD) 인제스트 트래커 (KOSDAQ)

- 아카이브 회사 수: **1706건** (source_documents/AnnualReport_MD/, 각 머신에 로컬 배치 필요·git 미포함)
- 완료(done, Full): **1109건**
- 대기(pending): **597건** (이 중 stub→Full 승급 대상 130건)

> done 기준: wiki/companies/<회사>.md 가 존재하고 is_stub:false.
> market 판정: 위키 frontmatter 우선, 없으면 원본 MD의 '상장 유형' 표(유가증권시장/코스닥시장 상장)에서 추출.
> 이 파일은 `python dart_pipeline/local_archive_status.py [--market KOSPI|KOSDAQ]` 로 재생성됩니다.
> 다음 N개사 산출: `python dart_pipeline/local_archive_status.py [--market KOSPI|KOSDAQ] --next N`

## ⏳ 대기 (상위 50건, 전체 597건)

- APS이노베이션 (`KOSDAQ`) — `source_documents/AnnualReport_MD/APS이노베이션-사업보고서-2024.12.md`
- CS (`KOSDAQ`) — `source_documents/AnnualReport_MD/CS-사업보고서-2025.12.md`
- DGI (`KOSDAQ`) — `source_documents/AnnualReport_MD/DGI-사업보고서-2025.12.md`
- DXVX (`KOSDAQ`) — `source_documents/AnnualReport_MD/DXVX-사업보고서-2025.12.md`
- GC메디아이 (`KOSDAQ`) — `source_documents/AnnualReport_MD/GC메디아이-사업보고서-2025.12.md`
- HK이노엔 (`KOSDAQ`) — `source_documents/AnnualReport_MD/HK이노엔-사업보고서-2025.12.md`
- IBKS제23호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/IBKS제23호스팩-사업보고서-2025.12.md`
- IBKS제24호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/IBKS제24호스팩-사업보고서-2025.12.md`
- IBKS제25호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/IBKS제25호스팩-사업보고서-2025.12.md`
- KB제29호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/KB제29호스팩-사업보고서-2025.12.md`
- KB제30호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/KB제30호스팩-사업보고서-2025.12.md`
- KB제31호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/KB제31호스팩-사업보고서-2025.12.md`
- KB제32호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/KB제32호스팩-사업보고서-2025.12.md`
- KB제33호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/KB제33호스팩-사업보고서-2025.12.md`
- KT지니뮤직 (`KOSDAQ`) — `source_documents/AnnualReport_MD/KT지니뮤직-사업보고서-2025.12.md`
- KX (`KOSDAQ`) — `source_documents/AnnualReport_MD/KX-사업보고서-2025.12.md`
- LSK아이로봇 (`KOSDAQ`) — `source_documents/AnnualReport_MD/LSK아이로봇-사업보고서-2025.12.md`
- NHN KCP (`KOSDAQ`) — `source_documents/AnnualReport_MD/NHN KCP-사업보고서-2025.12.md`
- NICE인프라 (`KOSDAQ`) — `source_documents/AnnualReport_MD/NICE인프라-사업보고서-2025.12.md`
- SFA (`KOSDAQ`) — `source_documents/AnnualReport_MD/SFA-사업보고서-2025.12.md`
- SK증권제11호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/SK증권제11호스팩-사업보고서-2025.12.md`
- SK증권제12호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/SK증권제12호스팩-사업보고서-2025.12.md`
- SK증권제13호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/SK증권제13호스팩-사업보고서-2025.12.md`
- 가비아 (`KOSDAQ`) — `source_documents/AnnualReport_MD/가비아-사업보고서-2025.12.md`
- 경동제약 (`KOSDAQ`) — `source_documents/AnnualReport_MD/경동제약-사업보고서-2025.12.md`
- 골프존 (`KOSDAQ`) — `source_documents/AnnualReport_MD/골프존-사업보고서-2025.12.md`
- 골프존홀딩스 (`KOSDAQ`) — `source_documents/AnnualReport_MD/골프존홀딩스-사업보고서-2025.12.md`
- 교보15호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/교보15호스팩-사업보고서-2025.12.md`
- 교보16호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/교보16호스팩-사업보고서-2025.12.md`
- 교보17호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/교보17호스팩-사업보고서-2025.12.md`
- 교보18호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/교보18호스팩-사업보고서-2025.12.md`
- 교보19호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/교보19호스팩-사업보고서-2025.12.md`
- 국전 (`KOSDAQ`) — `source_documents/AnnualReport_MD/국전-사업보고서-2025.12.md`
- 그래디언트 (`KOSDAQ`) — `source_documents/AnnualReport_MD/그래디언트-사업보고서-2025.12.md`
- 나노 (`KOSDAQ`) — `source_documents/AnnualReport_MD/나노-사업보고서-2025.12.md`
- 네오위즈 (`KOSDAQ`) — `source_documents/AnnualReport_MD/네오위즈-사업보고서-2025.12.md`
- 넥슨게임즈 (`KOSDAQ`) — `source_documents/AnnualReport_MD/넥슨게임즈-사업보고서-2025.12.md`
- 뉴트리 (`KOSDAQ`) — `source_documents/AnnualReport_MD/뉴트리-사업보고서-2025.12.md`
- 다날 (`KOSDAQ`) — `source_documents/AnnualReport_MD/다날-사업보고서-2025.12.md`
- 다산네트웍스 (`KOSDAQ`) — `source_documents/AnnualReport_MD/다산네트웍스-사업보고서-2025.12.md`
- 다우데이타 (`KOSDAQ`) — `source_documents/AnnualReport_MD/다우데이타-사업보고서-2025.12.md`
- 다원시스 (`KOSDAQ`) — `source_documents/AnnualReport_MD/다원시스-사업보고서-2025.12.md`
- 다이나믹솔루션 (`KOSDAQ`) — `source_documents/AnnualReport_MD/다이나믹솔루션-사업보고서-2025.12.md`
- 대성창투 (`KOSDAQ`) — `source_documents/AnnualReport_MD/대성창투-사업보고서-2025.12.md`
- 대신밸런스제17호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/대신밸런스제17호스팩-사업보고서-2025.12.md`
- 대신밸런스제19호스팩 (`KOSDAQ`) — `source_documents/AnnualReport_MD/대신밸런스제19호스팩-사업보고서-2025.12.md`
- 대아티아이 (`KOSDAQ`) — `source_documents/AnnualReport_MD/대아티아이-사업보고서-2025.12.md`
- 대원 (`KOSDAQ`) — `source_documents/AnnualReport_MD/대원-사업보고서-2025.12.md`
- 대주전자재료 (`KOSDAQ`) — `source_documents/AnnualReport_MD/대주전자재료-사업보고서-2025.12.md`
- 더네이쳐홀딩스 (`KOSDAQ`) — `source_documents/AnnualReport_MD/더네이쳐홀딩스-사업보고서-2025.12.md`
