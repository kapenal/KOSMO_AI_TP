// // 영화 상세 페이지
window.addEventListener('DOMContentLoaded', () => {
  const parts = window.location.pathname.split('/');
  const movieId = parts[parts.length - 1];

  fetch(`/api/movie/${movieId}`)
    .then(res => res.json())
    .then(movie => {
      // 영화 정보 삽입
      document.getElementById('title_ko').textContent = `[${movie.제목}]`;
      // document.getElementById('title_en').textContent = movie.영문제목 || '';
      document.getElementById('release_date').textContent = `개봉일: ${movie.연도}`;
      // document.getElementById('runtime').textContent = `상영시간: ${movie.상영시간 || '-'}분`;
      document.getElementById('rating_value').textContent = `${movie.평점}`;
      document.getElementById('director').textContent = movie.감독 || '-';
      // document.getElementById('actors').textContent = (movie.출연진 || []).join(', ');
      document.getElementById('overview').textContent = movie.줄거리 || '줄거리 정보가 없습니다.';

      // // 장르 뱃지
      // const genreContainer = document.getElementById('genre_badges');
      // genreContainer.innerHTML = '';
      // (movie.장르 || []).forEach(genre => {
      //   const span = document.createElement('span');
      //   span.className = 'badge bg-secondary me-1';
      //   span.textContent = genre;
      //   genreContainer.appendChild(span);
      // });

      // 포스터 이미지
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
});

//     // 추천 영화 데이터 로드
//     window.onload = function () {
//       // 1. URL에서 title 추출
//       const params = new URLSearchParams(window.location.search);
//       const titleFromUrl = params.get('title') || '';
//             const recommendData = titleFromUrl

//             if (recommendData && recommendData.recommendations) {
//                 console.log("추천 데이터:", recommendData);

//                 // 검색어 input에 값 넣기
//                 document.getElementById('search_text').value = recommendData.input_title || '';

//                 // 추천 영화들 반복 렌더링
//                 const container = document.getElementById('recommend_container');
//                 container.innerHTML = ''; // 기존 내용 초기화

//                 recommendData.recommendations.forEach((movie, index) => {
//                     const movieDiv = document.createElement('div');
//                     movieDiv.style.cssText = "width: 20%; padding: 10px; box-sizing: border-box;";

//                     movieDiv.innerHTML = `
//                         <img src="${movie.poster_path}" style="width: 200px%; height: 300px;" alt="${movie.title_ko}">
//                         <p><strong>제목:</strong> ${movie.title_ko}</p>
//                         <p><strong>장르:</strong> ${(movie.genres || []).join(', ')}</p>
//                         <p><strong>개봉일:</strong> ${movie.release_date}</p>
//                         <p><strong>평점:</strong> ${movie.vote_average.toFixed(1)}</p>
//                     `;

//                     container.appendChild(movieDiv);
//                 });
//             } else {
//                     console.error("추천 데이터가 없습니다.");
//             }
//         };



// 추천 영화 데이터 리스트
window.onload = function () {
  const params = new URLSearchParams(window.location.search);
  const titleFromUrl = params.get('title') || '';
  console.log("추천 영화 제목:", titleFromUrl);
  if (titleFromUrl) {
    fetch(`/api/recommend?title=${encodeURIComponent(titleFromUrl)}`)
      .then(res => res.json())
      .then(recommendData => {
        console.log("추천 데이터:", recommendData);

        // document.getElementById('search_text').value = recommendData.input_title || '';

        const container = document.getElementById('recommend_list');
        container.innerHTML = '';

        recommendData.recommendations.forEach((movie, index) => {
          const movieDiv = document.createElement('div');
          movieDiv.style.cssText = "width: 20%; padding: 10px; box-sizing: border-box;";

          movieDiv.innerHTML = `
            <a href="/movie/${movie.link}?title=${encodeURIComponent(movie.title_ko)}" style="text-decoration: none;">
              <img src="${movie.poster_path}" style="width: 200px; height: 300px;" alt="${movie.title_ko}">
              <p><strong>제목:</strong> ${movie.title_ko}</p>
              <p><strong>장르:</strong> ${(movie.genres || []).slice(0, 2).join(', ')}</p>
            </a>
          `;

          container.appendChild(movieDiv);
        });
      })
      .catch(err => {
        console.error("추천 영화 불러오기 실패:", err);
      });
  } else {
    console.error("추천 데이터가 없습니다.");
  }
};