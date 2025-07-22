// 페이지 로드 시 진행
window.addEventListener('DOMContentLoaded', () => {
  const parts = window.location.pathname.split('/');
  const movieId = parts[parts.length - 1];
  const params = new URLSearchParams(window.location.search);
  const title = params.get('title') || '';
  loadRecommendations(title);  // 추천 영화
  loadMovieDetail(movieId);   // 영화 상세 정보
  loadReviews(movieId);       // 리뷰 출력
});

// 영화 상세 데이터 함수
function loadMovieDetail(movieId) {
  fetch(`/api/movie/${movieId}`)
    .then(res => res.json())
    .then(movie => {
      document.getElementById('title_ko').textContent = `${movie.제목}`;
      document.getElementById('release_date').textContent = `${movie.연도}`;
      document.getElementById('rating_value').textContent = `${movie.평점}`;
      document.getElementById('overview').textContent = movie.줄거리 || '줄거리 정보가 없습니다.';
      document.getElementById('genres').textContent = movie.장르.join(', ');

      if (movie.포스터) {
        const posterImg = document.getElementById('poster');
        posterImg.src = movie.포스터;
        posterImg.classList.remove('d-none');
        document.getElementById('poster_empty').classList.add('d-none');
      }
    })
    .catch(err => {
      console.error('영화 상세 불러오기 실패:', err);
      document.getElementById('overview').textContent = '영화 정보를 불러올 수 없습니다.';
    });
}

// 리뷰 데이터 함수
function loadReviews(movieId) {
  fetch(`/api/review/${movieId}`)
    .then(res => res.json())
    .then(data => {
      const reviewContainer = document.getElementById('review_list');
      reviewContainer.innerHTML = ''; // 기존 리뷰 지우기

      // data 자체가 배열이므로 data.forEach 사용
      data.forEach(review => {
        const div = document.createElement('div');
        div.className = 'review-item';
        div.innerHTML = `
          <p><strong>${review.닉네임}</strong></p>
          <p>${review.리뷰}</p>
          <p>평점: ${review.평점}</p>
        `;
        reviewContainer.appendChild(div);
      });
    })
    .catch(err => {
      console.error('리뷰 불러오기 실패:', err);
    });
}

// 추천 영화 리스트 생성 함수
function loadRecommendations(title) {
  fetch(`/api/recommend?title=${encodeURIComponent(title)}`)
    .then(res => res.json())
    .then(recommendData => {
      const container = document.getElementById('recommend_list');
      container.innerHTML = '';

      recommendData.recommendations.forEach(movie => {
        const movieDiv = document.createElement('div');
        movieDiv.className = 'recommend-item bg-secondary';
        movieDiv.style.cssText = "width: 220px; height: 350px; text-align: center; padding: 10px; box-sizing: border-box; cursor: pointer;";

        movieDiv.innerHTML = `
          <img src="${movie.poster_path ? movie.poster_path : '/img/unimg.jpg'}" 
          onerror="this.onerror=null; this.src='/img/unimg.jpg';"
          style="width: 150px; height: 250px;" 
          alt="${movie.title_ko}">
          <p><strong>제목:</strong> ${movie.title_ko}</p>
          <p><strong>장르:</strong> ${(movie.genres || []).slice(0, 2).join(', ')}</p>
        `;

        // 클릭 시 기존 검색 함수 실행
        movieDiv.addEventListener('click', () => {
          executeSearch(movie.title_ko);
        });

        container.appendChild(movieDiv);
      });
    })
    .catch(err => {
      console.error("추천 영화 불러오기 실패:", err);
    });
}