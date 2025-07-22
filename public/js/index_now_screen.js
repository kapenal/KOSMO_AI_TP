// 현재 상영 영화 데이터 호출
window.onload = async () => {
    const container = document.querySelector('.now-playing .row');
    const spinner = document.getElementById('loading-spinner');

    try {
        const response = await fetch('/now_screen', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`서버 응답 오류: ${response.status} ${response.statusText}\n${errorText}`);
        }

        const data = await response.json();

        if (!data.movies || data.movies.length === 0) {
            container.innerHTML = '<p>현재 상영작을 불러올 수 없습니다.</p>';
            return;
        }

        container.innerHTML = '';  // 초기화

        data.movies.forEach(movie => {
            const col = document.createElement('div');
            col.className = 'col';

            const card = document.createElement('div');
            card.className = 'movie-card p-3';

            card.innerHTML = `
                <img src="${movie.포스터 !== "이미지 없음" ? movie.포스터 : 'https://via.placeholder.com/200x300?text=No+Image'}"
                    alt="${movie.제목}"
                    style="width:304px; height:436px; object-fit: cover; border-radius: 10px;">
                <h5 class="mt-2">${movie.제목}</h5>
                <p>${movie.개요 || ''}</p>
                <p>⭐ 별점: ${movie.별점 || '정보 없음'}</p>
            `;
            card.style.cursor = "pointer";
            // 클릭 시 영화 제목으로 검색 실행
            card.addEventListener('click', () => {
                executeSearch(movie.제목);
            });

            col.appendChild(card);
            container.appendChild(col);
        });

    } catch (error) {
        console.error('현재 상영작 불러오기 실패:', error);
        container.innerHTML = `<p>현재 상영작 정보를 가져오는 중 오류가 발생했습니다.</p>
            <pre style="white-space: pre-wrap; color: red;">${error.message}</pre>`;
    } finally {
        if (spinner) spinner.remove();
    }
};