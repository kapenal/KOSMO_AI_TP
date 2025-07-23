window.addEventListener('DOMContentLoaded', async () => {
    // 날짜 표시 및 리로드 버튼 처리
    const today = new Date();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const formattedDate = `${mm}.${dd} 기준`;

    const dateText = document.getElementById('date-text');
    const reloadBtn = document.getElementById('date-display-btn');
    const reloadIcon = document.getElementById('reload-icon');

    dateText.textContent = formattedDate;

    reloadBtn.addEventListener('click', () => {
        // 텍스트 변경
        dateText.textContent = "실시간 업데이트 중입니다...";
        // 아이콘 회전 애니메이션 추가
        reloadIcon.classList.add('rotate-animation');
        // 1초 후 페이지 새로고침
        setTimeout(() => {
            location.reload();
        }, 1000);
    });

    // trend-list 데이터 불러오기
    const container = document.getElementById('trend-list');
    try {
        const response = await fetch('/mj_data/TrendRanking.json'); // Node static 서버에서 직접 가져옴
        const data = await response.json();

        if (!data.movies || data.movies.length === 0) {
            container.innerHTML = '<p>랭킹 데이터가 없습니다.</p>';
            return;
        }

        data.movies.forEach(movie => {
            const div = document.createElement('div');
            div.className = 'trend_item';
            div.innerHTML = `
                <div class="rank_box">
                    <span class="rank">${movie.순위}</span>
                </div>
                <img class="poster" src="${movie.포스터}" alt="${movie.제목} 포스터" />
                <div class="info">
                    <div class="title">${movie.제목}</div>
                    <div class="genre">${movie.장르}</div>
                </div>
            `;
            div.style.cursor = "pointer";
            // 클릭 시 기존 검색 함수 실행
            div.addEventListener('click', () => {
                executeSearch(movie.제목);
            });

            container.appendChild(div);
        });
    } catch (err) {
        console.error('데이터 로드 오류:', err);
        container.innerHTML = '<p>데이터를 불러오는데 실패했습니다.</p>';
    }
});
